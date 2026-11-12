"""Run the public dispatcher as a process against fake Docker; no daemon/network."""
import copy
import fcntl
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/amp-self-hosted-orbs/scripts/dispatch.py'
PROVIDER = 'amp.self-hosted.provider'
ORB = 'amp.self-hosted.orb'
KIND = 'amp.self-hosted.kind'

FAKE_DOCKER = r'''#!/usr/bin/env python3
import fcntl, json, os, sys, time
from pathlib import Path
root = Path(os.environ['FAKE_DOCKER_DIR'])
a = sys.argv[1:]
assert a[:2] == ['--host', 'unix:///var/run/docker.sock'], a
a = a[2:]
with (root/'fake.lock').open('a') as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    state = json.loads((root/'state.json').read_text())
    with (root/'calls.jsonl').open('a') as log:
        log.write(json.dumps({'args': a, 'provider_token_present': 'AMP_ORB_PROVIDER_TOKEN' in os.environ,
                              'orb_token': os.environ.get('ORB_TOKEN')})+'\n')
    if a[0] in state.get('fail', []):
        print('private-docker-error '+os.environ.get('ORB_TOKEN',''), file=sys.stderr)
        sys.exit(1)
    if a[0] == 'info': print(json.dumps({'MemoryLimit': state.get('memory', True)}))
    elif a[:2] == ['container', 'ls']:
        containers = state['containers']
        if '--all' in a: print('\n'.join(containers))
        else:
            filters = [a[i+1][6:] for i,x in enumerate(a) if x == '--filter' and a[i+1].startswith('label=')]
            for name, c in containers.items():
                if c['State']['Running'] and all(c['Config']['Labels'].get(f.split('=',1)[0]) == f.split('=',1)[1] for f in filters):
                    print(name)
    elif a[:2] == ['container', 'inspect']:
        if a[-1] not in state['containers']: sys.exit(1)
        print(json.dumps([state['containers'][a[-1]]]))
    elif a[:2] == ['image', 'ls']:
        assert a[2:] == ['--digests', '--format', '{{.Repository}}:{{.Tag}} {{.Repository}}@{{.Digest}}']
        for reference, details in state['images'].items():
            name, _, digest = reference.partition('@')
            last = name.rsplit('/', 1)[-1]
            repository, tag = name.rsplit(':', 1) if ':' in last else (name, '<none>')
            for tagged in details.get('RepoTags', [repository+':'+tag]):
                for pinned in details.get('RepoDigests', [repository+'@'+(digest or '<none>')]):
                    print(tagged+' '+pinned)
    elif a[:2] == ['image', 'inspect']:
        if a[-1] not in state['images']: sys.exit(1)
        print(json.dumps([state['images'][a[-1]]]))
    elif a[0] == 'run':
        def val(flag): return a[a.index(flag)+1]
        name = val('--name')
        if name in state['containers']: sys.exit(1)
        time.sleep(state.get('run_delay', 0))
        labels = dict(a[i+1].split('=',1) for i,x in enumerate(a) if x == '--label')
        c = {'Config': {'Labels': labels, 'User': 'user'}, 'State': {'Running': True}, 'Mounts': [],
             'HostConfig': {'Memory': int(val('--memory')), 'MemorySwap': int(val('--memory-swap')),
                            'NanoCpus': int(val('--cpus'))*1000000000, 'PidsLimit': int(val('--pids-limit')),
                            'ShmSize': int(val('--shm-size')), 'Privileged': False,
                            'Binds': [], 'PortBindings': {}, 'PublishAllPorts': False,
                            'NetworkMode': 'bridge', 'PidMode': '', 'IpcMode': 'private',
                            'CapAdd': [], 'CapDrop': ['NET_RAW'],
                            'SecurityOpt': [], 'Devices': [], 'DeviceRequests': []}}
        c['HostConfig'].update(state.get('run_override', {}))
        state['containers'][name] = c
        print('fake-container-id')
    elif a[0] in ('start','stop','rm'):
        name = a[-1]
        if a[0] == 'rm': state['containers'].pop(name)
        else: state['containers'][name]['State']['Running'] = a[0] == 'start'
    elif a[0] == 'commit':
        label = a[a.index('--change')+1].removeprefix('LABEL ')
        labels = dict(item.split('=',1) for item in label.split())
        state['images'][a[-1]] = {'Architecture': 'amd64', 'Os': 'linux',
                                 'Config': {'Labels': labels, 'User': 'user', 'Volumes': None}}
    elif a[0] == 'exec': pass
    else: raise AssertionError(a)
    (root/'state.json').write_text(json.dumps(state))
if a[:2] == ['container', 'ls'] and '--all' not in a:
    time.sleep(state.get('count_delay', 0))
'''


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = {'provider': 'example-provider', 'platform': 'linux/amd64',
                       'cpus': 1, 'memory_mib': 2048, 'max_running_orbs': 1}
        self.state = {'containers': {}, 'images': {'example.invalid/orb:tested': self.image()}}
        self.config_path = self.root/'resources.json'
        fake = self.root/'docker'
        fake.write_text(FAKE_DOCKER)
        fake.chmod(0o755)
        self.env = {**os.environ, 'PATH': str(self.root)+os.pathsep+os.environ['PATH'],
                    'AMP_ORB_RESOURCES': str(self.config_path),
                    'AMP_ORB_STATE_DIR': str(self.root/'provider-state'),
                    'FAKE_DOCKER_DIR': str(self.root),
                    'ORB_OPERATION': 'spawn', 'ORB_ID': 'amp-canary',
                    'ORB_IMAGE': 'example.invalid/orb:tested', 'ORB_TOKEN': 'offline-canary-only',
                    'AMP_ORB_PROVIDER_TOKEN': 'offline-provider-only',
                    'PYTHONDONTWRITEBYTECODE': '1'}
        for key in ('ORB_SNAPSHOT_ID', 'ORB_TYPE', 'AMP_URL'):
            self.env.pop(key, None)

    @staticmethod
    def image(labels=None, arch='amd64'):
        return {'Architecture': arch, 'Os': 'linux',
                'Config': {'User': 'user', 'Volumes': None, 'Labels': labels or {}}}

    def save(self):
        self.config_path.write_text(json.dumps(self.config))
        (self.root/'state.json').write_text(json.dumps(self.state))

    def run_dispatch(self, **env):
        self.assertTrue(SCRIPT.is_file(), 'Portable dispatcher is missing')
        self.save()
        result = subprocess.run([sys.executable, '-B', str(SCRIPT)], env={**self.env, **env},
                                text=True, capture_output=True, timeout=15, cwd=self.root, check=False)
        self.state = json.loads((self.root/'state.json').read_text())
        return result

    def calls(self):
        path = self.root/'calls.jsonl'
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def args(self, command):
        return [call['args'] for call in self.calls() if call['args'][0] == command]

    def test_spawn_refuses_missing_memory_enforcement(self):
        self.state['memory'] = False
        result = self.run_dispatch()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('memory limit', result.stderr.lower())
        self.assertFalse(self.args('run'))
        self.assertFalse(self.args('exec'))
    def test_new_spawn_has_resource_ceilings_and_token_only_in_exec_env(self):
        result = self.run_dispatch(AMP_URL='https://example.com')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.args('run')), 1, 'Spawn must create one orb')
        run, = self.args('run')
        for flag, value in [('--cpus', '1'), ('--memory', '2147483648'),
                            ('--memory-swap', '2147483648'), ('--pids-limit', '1024'),
                            ('--shm-size', '1073741824'), ('--platform', 'linux/amd64'),
                            ('--cap-drop', 'NET_RAW')]:
            self.assertEqual(run[run.index(flag)+1], value)
        for forbidden in ('--privileged', '--volume', '-v', '--mount', '-p', '--publish',
                          '--publish-all', '--memory-reservation', '--cpuset-cpus', '--gpus'):
            self.assertNotIn(forbidden, run)
        self.assertNotIn('--security-opt', run, 'Stock Amp requires working passwordless sudo')
        self.assertEqual(run[-2:], ['example.invalid/orb:tested', 'infinity'])
        execution, = self.args('exec')
        self.assertIn('ORB_TOKEN', execution)
        self.assertIn('AMP_URL', execution)
        self.assertEqual(execution[-4:], ['amp-canary', 'amp', 'orb', 'bootstrap'])
        for call in self.calls():
            self.assertNotIn('offline-canary-only', json.dumps(call['args']))
            self.assertNotIn('offline-provider-only', json.dumps(call))
            self.assertFalse(call['provider_token_present'])
            if call['args'][0] != 'exec':
                self.assertIsNone(call['orb_token'])
        self.assertEqual(self.calls()[-1]['orb_token'], 'offline-canary-only')
    def assert_digest_spawn(self, repository, tagged):
        digest = 'sha256:' + 'a' * 64
        canonical = repository + '@' + digest
        requested = repository + (':tested' if tagged else '') + '@' + digest
        self.state['images'] = {canonical: {
            **self.image(), 'RepoTags': [repository + ':tested'], 'RepoDigests': [canonical]}}
        result = self.run_dispatch(ORB_IMAGE=requested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args('run')[0][-2:], [canonical, 'infinity'])
        inspected = [args[-1] for args in self.args('image') if args[1] == 'inspect']
        self.assertEqual(inspected, [canonical])
        self.assertEqual(len(self.args('exec')), 1)

    def test_digest_only_reference_uses_cached_digest(self):
        self.assert_digest_spawn('example.invalid/orb', tagged=False)

    def test_tag_and_digest_reference_uses_cached_digest(self):
        self.assert_digest_spawn('example.invalid/orb', tagged=True)

    def test_tag_and_digest_reference_preserves_registry_port(self):
        self.assert_digest_spawn('registry.example.invalid:5000/team/orb', tagged=True)

    def test_invalid_inputs_fail_before_docker_or_mutation(self):
        cases = [({'ORB_OPERATION': 'restart'}, {}), ({'ORB_ID': '--help'}, {}),
                 ({'ORB_ID': 'amp-../escape'}, {}), ({'ORB_TOKEN': ''}, {}),
                 ({'ORB_SNAPSHOT_ID': '--foreign', 'ORB_OPERATION': 'pause'}, {}),
                 ({'ORB_SNAPSHOT_ID': 'bad tag', 'ORB_OPERATION': 'delete'}, {}),
                 ({'ORB_SNAPSHOT_ID': 'amp-a/', 'ORB_OPERATION': 'pause'}, {}),
                 ({'ORB_SNAPSHOT_ID': 'amp-a:', 'ORB_OPERATION': 'pause'}, {}),
                 ({'ORB_SNAPSHOT_ID': 'amp-a//bad', 'ORB_OPERATION': 'pause'}, {}),
                 ({'ORB_IMAGE': '--privileged'}, {}), ({'ORB_TYPE': 'gpu'}, {}),
                 ({}, {'max_running_orbs': 0}), ({}, {'max_running_orbs': '1+1'}),
                 ({}, {'cpus': True}), ({}, {'cpus': -1}), ({}, {'memory_mib': 0}),
                 ({}, {'platform': 'linux/ppc64le'}), ({}, {'provider': 'bad=label'}),
                 ({}, {'unexpected': 'ignored?'}), ({'AMP_ORB_RESOURCES': 'relative.json'}, {})]
        for env, config in cases:
            with self.subTest(env=env, config=config):
                self.config = {'provider': 'example-provider', 'platform': 'linux/amd64',
                               'cpus': 1, 'memory_mib': 2048, 'max_running_orbs': 1, **config}
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch(**env)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.calls(), [], 'Invalid request reached Docker')
                self.assertNotIn('Traceback', result.stderr)
    def seed_orb(self):
        result = self.run_dispatch()
        self.assertEqual(result.returncode, 0, result.stderr)
        (self.root/'calls.jsonl').unlink()

    def test_unowned_container_is_never_mutated(self):
        self.seed_orb()
        for labels in ({}, {PROVIDER: 'another-provider'},
                       {PROVIDER: self.config['provider'], ORB: 'amp-other', KIND: 'orb'}):
            self.state['containers']['amp-canary']['Config']['Labels'] = labels
            for operation in ('spawn', 'pause', 'delete'):
                with self.subTest(labels=labels, operation=operation):
                    (self.root/'calls.jsonl').unlink(missing_ok=True)
                    result = self.run_dispatch(ORB_OPERATION=operation)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('ownership', result.stderr.lower())
                    for command in ('run', 'start', 'stop', 'rm', 'exec', 'commit'):
                        self.assertFalse(self.args(command))

    def test_pause_and_delete_are_repeatable_without_spawn_credentials(self):
        self.seed_orb()
        for operation in ('pause', 'pause', 'delete', 'delete', 'pause'):
            result = self.run_dispatch(ORB_OPERATION=operation, ORB_TOKEN='', ORB_IMAGE='')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.state['containers'], {})
        self.assertEqual(len(self.args('stop')), 1)
        self.assertEqual(len(self.args('rm')), 1)
        self.assertFalse(self.args('exec'))
        self.assertFalse(self.args('run'))


    def test_capacity_counts_only_this_provider_and_reconnect_is_not_new_admission(self):
        self.seed_orb()
        result = self.run_dispatch(ORB_ID='amp-second')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('capacity', result.stderr.lower())
        result = self.run_dispatch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.args('run'))
        self.assertFalse(self.args('start'))
        self.state['containers']['amp-canary']['State']['Running'] = False
        result = self.run_dispatch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.args('start')), 1)
        self.state['containers']['amp-canary']['Config']['Labels'][PROVIDER] = 'foreign-provider'
        result = self.run_dispatch(ORB_ID='amp-second')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_concurrent_spawn_cannot_over_admit(self):
        self.assertTrue(SCRIPT.is_file())
        self.state['count_delay'] = 0.4
        self.save()
        processes = [subprocess.Popen([sys.executable, '-B', str(SCRIPT)],
                                      env={**self.env, 'ORB_ID': name},
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                     for name in ('amp-first', 'amp-second')]
        outputs = [p.communicate(timeout=15) for p in processes]
        self.assertEqual(sorted(p.returncode for p in processes), [0, 1], outputs)
        self.assertEqual(len(self.args('run')), 1)
    def test_pause_saves_owned_snapshot_and_new_orb_uses_it(self):
        self.seed_orb()
        result = self.run_dispatch(ORB_OPERATION='pause', ORB_SNAPSHOT_ID='amp-snapshot:canary')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.args('commit')), 1, 'Pause must save the requested snapshot')
        image = self.state['images']['amp-snapshot:canary']
        self.assertEqual(image['Config']['Labels'][PROVIDER], self.config['provider'])
        self.assertEqual(image['Config']['Labels'][KIND], 'snapshot')
        result = self.run_dispatch(ORB_ID='amp-from-snapshot', ORB_SNAPSHOT_ID='amp-snapshot:canary')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args('run')[-1][-2], 'amp-snapshot:canary')
        self.assertFalse(self.state['containers']['amp-canary']['State']['Running'])

    def test_existing_unowned_or_foreign_snapshot_is_not_overwritten_or_booted(self):
        self.seed_orb()
        for labels in ({}, {PROVIDER: 'another-provider', KIND: 'snapshot'},
                       {PROVIDER: self.config['provider'], KIND: 'orb'}):
            self.state['images']['amp-snapshot:collision'] = self.image(labels)
            for operation in ('pause', 'spawn'):
                with self.subTest(labels=labels, operation=operation):
                    (self.root/'calls.jsonl').unlink(missing_ok=True)
                    result = self.run_dispatch(ORB_OPERATION=operation, ORB_SNAPSHOT_ID='amp-snapshot:collision')
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('snapshot ownership', result.stderr.lower())
                    for command in ('run', 'start', 'stop', 'exec', 'commit'):
                        self.assertFalse(self.args(command))
                    self.assertEqual(self.state['images']['amp-snapshot:collision']['Config']['Labels'], labels)

    def test_docker_hub_snapshot_alias_cannot_bypass_foreign_ownership(self):
        self.seed_orb()
        self.state['images']['ubuntu:latest'] = self.image()
        for alias in ('docker.io/library/ubuntu:latest', 'index.docker.io/library/ubuntu:latest',
                      'docker.io/ubuntu:latest', 'library/ubuntu:latest'):
            for operation in ('pause', 'spawn'):
                with self.subTest(alias=alias, operation=operation):
                    (self.root/'calls.jsonl').unlink(missing_ok=True)
                    result = self.run_dispatch(ORB_OPERATION=operation, ORB_SNAPSHOT_ID=alias)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn('snapshot ownership', result.stderr.lower())
                    for command in ('run', 'start', 'stop', 'exec', 'commit'):
                        self.assertFalse(self.args(command))
                    self.assertIn(['image', 'inspect', 'ubuntu:latest'], self.args('image'))

    def test_custom_registry_snapshot_references_keep_repository_and_port(self):
        self.seed_orb()
        for reference in ('registry.example.invalid/library/ubuntu:latest',
                          'registry.example.invalid:5000/library/ubuntu:latest'):
            self.state['images'][reference] = self.image()
            with self.subTest(reference=reference):
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch(ORB_OPERATION='pause', ORB_SNAPSHOT_ID=reference)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('snapshot ownership', result.stderr.lower())
                self.assertIn(['image', 'inspect', reference], self.args('image'))
                self.assertFalse(self.args('commit'))
                self.assertFalse(self.args('stop'))

    def test_missing_snapshot_falls_back_to_base_image(self):
        result = self.run_dispatch(ORB_SNAPSHOT_ID='amp-snapshot:missing')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args('run')[0][-2], self.env['ORB_IMAGE'])


    def test_resume_rejects_old_limits_or_unsafe_container_configuration(self):
        self.seed_orb()
        pristine = copy.deepcopy(self.state['containers']['amp-canary'])
        for key, value in [('Memory', 0), ('MemorySwap', -1), ('NanoCpus', 0),
                           ('PidsLimit', 0), ('Privileged', True),
                           ('Binds', ['/some-host-path:/data']), ('PortBindings', {'80/tcp': [{}]}),
                           ('NetworkMode', 'host'), ('PidMode', 'host'), ('IpcMode', 'host'),
                           ('CapAdd', ['SYS_ADMIN']), ('Devices', [{'PathOnHost': '/dev/example'}])]:
            with self.subTest(key=key):
                self.state['containers']['amp-canary'] = copy.deepcopy(pristine)
                self.state['containers']['amp-canary']['State']['Running'] = False
                self.state['containers']['amp-canary']['HostConfig'][key] = value
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('configuration', result.stderr.lower())
                self.assertFalse(self.args('start'))
                self.assertFalse(self.args('exec'))
        self.state['containers']['amp-canary'] = pristine
        self.config['memory_mib'] = 3072
        result = self.run_dispatch()
        self.assertNotEqual(result.returncode, 0, 'A resource edit must not silently reuse old limits')

    def test_new_container_with_ineffective_memory_limit_is_not_bootstrapped(self):
        self.state['run_override'] = {'Memory': 0}
        result = self.run_dispatch()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.args('exec'))
        self.assertFalse(self.state['containers']['amp-canary']['State']['Running'])
    def test_images_must_be_local_matching_platform_nonroot_without_volumes(self):
        images = [{}, {self.env['ORB_IMAGE']: self.image(arch='arm64')},
                  {self.env['ORB_IMAGE']: {**self.image(), 'Config': {'User': 'root'}}},
                  {self.env['ORB_IMAGE']: {**self.image(), 'Config': {'User': 'user', 'Volumes': {'/data': {}}}}}]
        for entries in images:
            with self.subTest(images=entries):
                self.state = {'containers': {}, 'images': entries}
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.args('run'))
                self.assertFalse(self.args('exec'))
        self.config['platform'] = 'linux/arm64'
        self.state = {'containers': {}, 'images': {self.env['ORB_IMAGE']: self.image(arch='arm64')}}
        result = self.run_dispatch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.args('run')[0][self.args('run')[0].index('--platform')+1], 'linux/arm64')
        self.assertIn('--pull=never', self.args('run')[0])

    def test_untagged_snapshot_collision_is_not_treated_as_absent(self):
        self.seed_orb()
        self.state['images']['amp-snapshot:latest'] = self.image()
        result = self.run_dispatch(ORB_OPERATION='pause', ORB_SNAPSHOT_ID='amp-snapshot')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.args('stop'))
        self.assertFalse(self.args('commit'))


    def test_state_directory_and_lock_cannot_be_shared_or_symlinked(self):
        public = self.root/'public-state'
        public.mkdir(mode=0o755)
        link = self.root/'linked-state'
        link.symlink_to(public, target_is_directory=True)
        locked = self.root/'linked-lock-state'
        locked.mkdir(mode=0o700)
        target = self.root/'unrelated-file'
        target.write_text('unchanged')
        (locked/'lifecycle.lock').symlink_to(target)
        for state in ('relative-state', str(public), str(link), str(locked)):
            with self.subTest(state=state):
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch(AMP_ORB_STATE_DIR=state)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.calls(), [])
                self.assertEqual(target.read_text(), 'unchanged')

    def load_dispatcher(self):
        spec = importlib.util.spec_from_file_location('offline_dispatch', SCRIPT)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, 'BUDGET_SECONDS'), 'Lifecycle deadline is missing')
        self.assertLess(module.BUDGET_SECONDS, 300)
        return module

    def test_total_deadline_bounds_real_docker_wait(self):
        module = self.load_dispatcher()
        self.state['count_delay'] = 0.5
        self.save()
        before = time.monotonic()
        with patch.dict(os.environ, self.env, clear=True), patch.object(module, 'BUDGET_SECONDS', 0.2), \
                self.assertRaisesRegex(ValueError, 'deadline|timed out'):
            module.main()
        self.assertLess(time.monotonic()-before, 1)
        self.assertFalse(self.args('run'))

    def test_total_deadline_bounds_lock_wait(self):
        module = self.load_dispatcher()
        self.save()
        state = Path(self.env['AMP_ORB_STATE_DIR'])
        state.mkdir(mode=0o700)
        with (state/'lifecycle.lock').open('w') as lock:
            os.chmod(lock.name, 0o600)
            fcntl.flock(lock, fcntl.LOCK_EX)
            before = time.monotonic()
            with patch.dict(os.environ, self.env, clear=True), patch.object(module, 'BUDGET_SECONDS', 0.15), \
                    self.assertRaisesRegex(ValueError, 'deadline|timed out'):
                module.main()
            self.assertLess(time.monotonic()-before, 1)
        self.assertEqual(self.calls(), [])

    def test_docker_errors_fail_closed_and_do_not_relay_private_stderr(self):
        for command in ('info', 'container', 'image', 'run', 'exec'):
            with self.subTest(command=command):
                self.state = {'containers': {}, 'images': {self.env['ORB_IMAGE']: self.image()}, 'fail': [command]}
                (self.root/'calls.jsonl').unlink(missing_ok=True)
                result = self.run_dispatch(ORB_SNAPSHOT_ID='amp-snapshot:missing')
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('private-docker-error', result.stderr)
                self.assertNotIn(self.env['ORB_TOKEN'], result.stdout+result.stderr)
                if command in ('info', 'container', 'image'):
                    self.assertFalse(self.args('run'))
                    self.assertFalse(self.args('exec'))


if __name__ == '__main__':
    unittest.main()
