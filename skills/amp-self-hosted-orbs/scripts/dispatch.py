#!/usr/bin/env python3
"""Single-host Amp/Docker lifecycle dispatcher. Python standard library only."""
import fcntl
import json
import os
import re
import stat
import subprocess
import sys
import time
from pathlib import Path

PROVIDER = 'amp.self-hosted.provider'
ORB = 'amp.self-hosted.orb'
KIND = 'amp.self-hosted.kind'
BUDGET_SECONDS = 270
deadline = 0.0
COMPONENT = r'[a-z0-9]+(?:(?:[._]|__|-+)[a-z0-9]+)*'
NAME = rf'(?:[a-z0-9]+(?:[.-][a-z0-9]+)*:[0-9]+/)?{COMPONENT}(?:/{COMPONENT})*'
TAGGED = rf'{NAME}(?::[a-z0-9_][a-z0-9_.-]{{0,127}})?'


class Refusal(ValueError):
    """Safe, static diagnostic suitable for provider logs."""


def remaining():
    seconds = deadline - time.monotonic()
    if seconds <= 0:
        raise Refusal('Lifecycle deadline exceeded; inspect owned resources before retrying')
    return seconds


def docker(*args):
    excluded = {'AMP_ORB_PROVIDER_TOKEN'}
    if args[0] != 'exec':
        excluded.update(('ORB_TOKEN', 'AMP_URL'))
    try:
        result = subprocess.run(['docker', '--host', 'unix:///var/run/docker.sock', *args],
                                capture_output=True, text=True, timeout=min(60, remaining()),
                                env={k: v for k, v in os.environ.items() if k not in excluded}, check=False)
    except subprocess.TimeoutExpired:
        raise Refusal('Docker request timed out; daemon work may still finish; inspect before retrying') from None
    if result.returncode:
        raise Refusal('Docker operation failed (details withheld)')
    return result.stdout


def inputs():
    path = Path(os.environ['AMP_ORB_RESOURCES'])
    if not path.is_absolute():
        raise Refusal('Resource path must be absolute')
    config = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(config, dict) or set(config) != {'provider', 'platform', 'cpus', 'memory_mib', 'max_running_orbs'}:
        raise Refusal('Resource keys are missing or unsupported')
    if not isinstance(config['provider'], str) or not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', config['provider']):
        raise Refusal('Invalid provider label')
    if config['platform'] not in ('linux/amd64', 'linux/arm64'):
        raise Refusal('Unsupported platform')
    for key, low, high in [('cpus', 1, 128), ('memory_mib', 1024, 1048576), ('max_running_orbs', 1, 64)]:
        if type(config[key]) is not int or not low <= config[key] <= high:
            raise Refusal('Invalid resource ceiling')
    operation = os.environ['ORB_OPERATION']
    if operation not in ('spawn', 'pause', 'delete'):
        raise Refusal('Unsupported lifecycle operation')
    if not re.fullmatch(r'amp-[A-Za-z0-9][A-Za-z0-9_-]{0,119}', os.environ['ORB_ID']):
        raise Refusal('Invalid orb ID')
    snapshot = os.environ.get('ORB_SNAPSHOT_ID', '')
    if snapshot and (len(snapshot) > 255 or not re.fullmatch(TAGGED, snapshot)):
        raise Refusal('Invalid snapshot ID')
    if operation == 'spawn':
        if not os.environ.get('ORB_TOKEN'):
            raise Refusal('ORB_TOKEN is required')
        image = os.environ['ORB_IMAGE']
        if len(image) > 512 or not re.fullmatch(rf'{TAGGED}(?:@sha256:[0-9a-f]{{64}})?', image):
            raise Refusal('Invalid image reference')
        if os.environ.get('ORB_TYPE'):
            raise Refusal('Orb types are not supported by this dispatcher')
    return config


def lifecycle(config):
    orb_id = os.environ['ORB_ID']
    operation = os.environ['ORB_OPERATION']
    names = docker('container', 'ls', '--all', '--format', '{{.Names}}').splitlines()
    container = None
    if orb_id in names:
        container = json.loads(docker('container', 'inspect', orb_id))[0]
        labels = container['Config'].get('Labels') or {}
        if any(labels.get(key) != value for key, value in
               [(PROVIDER, config['provider']), (ORB, orb_id), (KIND, 'orb')]):
            raise Refusal('Container ownership mismatch; refusing operation')
    if operation == 'delete':
        if container:
            docker('rm', '-f', orb_id)
        print('delete complete')
        return
    snapshot = os.environ.get('ORB_SNAPSHOT_ID', '')
    saved = local_image(snapshot) if snapshot else None
    if saved:
        labels = saved['Config'].get('Labels') or {}
        if labels.get(PROVIDER) != config['provider'] or labels.get(KIND) != 'snapshot':
            raise Refusal('Snapshot ownership mismatch; refusing operation')
    if operation == 'pause':
        if container and container['State']['Running']:
            docker('stop', '--time', '20', orb_id)
        if container and snapshot:
            docker('commit', '--change', 'LABEL '+PROVIDER+'='+config['provider']+' '+KIND+'=snapshot',
                   orb_id, snapshot)
        print('pause complete')
        return
    info = json.loads(docker('info', '--format', '{{json .}}'))
    if info.get('MemoryLimit') is not True:
        raise Refusal('Docker memory limit enforcement unavailable; refusing spawn')
    if container:
        validate_container(config, container)
    if not container or not container['State']['Running']:
        running = docker('container', 'ls', '--filter', 'label='+PROVIDER+'='+config['provider'],
                         '--format', '{{.ID}}').splitlines()
        if len(running) >= config['max_running_orbs']:
            raise Refusal('Provider capacity ceiling reached')
    if container:
        if not container['State']['Running']:
            docker('start', orb_id)
    else:
        create(config, orb_id, snapshot if saved else os.environ['ORB_IMAGE'])
        try:
            validate_container(config, json.loads(docker('container', 'inspect', orb_id))[0])
        except ValueError:
            docker('stop', '--time', '20', orb_id)
            raise
    args = ['exec', '-d', '--env', 'ORB_TOKEN']
    if os.environ.get('AMP_URL'):
        args += ['--env', 'AMP_URL']
    docker(*args, orb_id, 'amp', 'orb', 'bootstrap')
    print('spawn complete')


def local_image(reference):
    reference = image_reference(reference)
    # Inventory failure is fatal, never confused with a missing/unlabelled image.
    references = docker('image', 'ls', '--digests', '--format',
                        '{{.Repository}}:{{.Tag}} {{.Repository}}@{{.Digest}}').split()
    if reference not in references:
        return None
    return json.loads(docker('image', 'inspect', reference))[0]


def image_reference(reference):
    # Docker inventory uses familiar Docker Hub names, not registry aliases.
    for prefix in ('docker.io/', 'index.docker.io/'):
        if reference.startswith(prefix):
            reference = reference[len(prefix):]
            break
    reference = reference.removeprefix('library/')
    if '@' in reference:
        name, digest = reference.split('@', 1)
        if ':' in name.rsplit('/', 1)[-1]:
            name = name.rsplit(':', 1)[0]
        return name + '@' + digest
    if '@' not in reference and ':' not in reference.rsplit('/', 1)[-1]:
        return reference + ':latest'
    return reference


def validate_container(config, container):
    host = container['HostConfig']
    memory = config['memory_mib'] * 1024 * 1024
    expected = {'Memory': memory, 'MemorySwap': memory, 'NanoCpus': config['cpus'] * 1000000000,
                'PidsLimit': 1024, 'ShmSize': 1073741824}
    valid = all(host.get(key) == value for key, value in expected.items())
    valid = valid and host.get('Privileged') is False and not container.get('Mounts')
    valid = valid and all(not host.get(key) for key in
                          ('Binds', 'Mounts', 'PortBindings', 'PublishAllPorts', 'CapAdd', 'Devices', 'DeviceRequests'))
    valid = valid and host.get('NetworkMode') in ('default', 'bridge')
    valid = valid and host.get('PidMode') == '' and host.get('IpcMode') in ('', 'private')
    valid = valid and 'NET_RAW' in (host.get('CapDrop') or [])
    valid = valid and container['Config'].get('User') in ('user', 'user:user')
    if not valid:
        raise Refusal('Container configuration does not match current limits/isolation; refusing spawn')


def create(config, orb_id, image):
    image = image_reference(image)
    details = local_image(image)
    if not details:
        raise Refusal('Image is not cached locally; pre-pull it before starting the provider')
    image_config = details['Config']
    if (details.get('Os')+'/'+details.get('Architecture') != config['platform']
            or image_config.get('User') not in ('user', 'user:user') or image_config.get('Volumes')):
        raise Refusal('Image platform, default user, or declared volumes are unsupported')
    memory = str(config['memory_mib'] * 1024 * 1024)
    docker('run', '--pull=never', '--init', '--platform', config['platform'], '-d', '--name', orb_id,
           '--label', PROVIDER+'='+config['provider'],
           '--label', ORB+'='+orb_id, '--label', KIND+'=orb',
           '--cpus', str(config['cpus']), '--memory', memory, '--memory-swap', memory,
           '--pids-limit', '1024', '--shm-size', '1073741824', '--cap-drop', 'NET_RAW',
           '--log-driver', 'json-file',
           '--log-opt', 'max-size=10m', '--log-opt', 'max-file=2',
           '--entrypoint', 'sleep', image, 'infinity')


def main():
    global deadline
    deadline = time.monotonic() + BUDGET_SECONDS
    config = inputs()
    state = Path(os.environ['AMP_ORB_STATE_DIR'])
    if not state.is_absolute():
        raise Refusal('State directory must be absolute')
    state.mkdir(mode=0o700, exist_ok=True)
    info = state.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
        raise Refusal('State directory must be owned by this user, private (0700), and not a symlink')
    fd = os.open(state/'lifecycle.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
            raise Refusal('Lifecycle lock must be a private owned regular file')
        while True:
            remaining()
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                time.sleep(min(0.05, remaining()))
        lifecycle(config)


if __name__ == '__main__':
    try:
        main()
    except Refusal as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, IndexError, TypeError, AttributeError, OSError, subprocess.SubprocessError):
        print('Invalid configuration, missing environment, or Docker failure (details withheld)', file=sys.stderr)
        sys.exit(1)
