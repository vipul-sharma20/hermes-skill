"""Public packaging checks; behavioral Docker-boundary tests are in the sibling."""
import ast
import importlib.util
import json
import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/amp-self-hosted-orbs'


class PackageTests(unittest.TestCase):
    def test_frontmatter_sections_and_supporting_files(self):
        path = SKILL/'SKILL.md'
        self.assertTrue(path.is_file(), 'Public workflow is missing')
        text = path.read_text(encoding='utf-8')
        header = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
        self.assertIsNotNone(header)
        assert header is not None
        frontmatter = header.group(1)
        for line in ('name: amp-self-hosted-orbs', 'version: 0.1.0',
                     'author: Vipul Sharma (vipul-sharma20), Hermes Agent',
                     'license: MIT', 'platforms: [linux]', '    related_skills: []'):
            self.assertIn(line, frontmatter)
        description_match = re.search(r'^description: "?([^\n"]+)"?$', frontmatter, re.MULTILINE)
        self.assertIsNotNone(description_match)
        assert description_match is not None
        description = description_match.group(1)
        self.assertLessEqual(len(description), 60)
        self.assertTrue(description.endswith('.'))
        for section in ('When to Use', 'Prerequisites', 'Procedure', 'Pitfalls', 'Verification'):
            self.assertIn('## '+section, text)
        for path in SKILL.rglob('*'):
            if any(part in {'__pycache__', '.pytest_cache', '.ruff_cache'} for part in path.relative_to(SKILL).parts) or path.suffix == '.pyc':
                continue
            if path.is_file() and path.name != 'SKILL.md':
                self.assertIn('`'+path.relative_to(SKILL).as_posix()+'`', text)
        self.assertLessEqual(len(text.splitlines()), 220)

    def test_resource_template_passes_real_dispatcher_validation(self):
        path = SKILL/'templates/resources.example.json'
        self.assertTrue(path.is_file(), 'Resource ceiling template is missing')
        config = json.loads(path.read_text())
        spec = importlib.util.spec_from_file_location('resource_validation', SKILL/'scripts/dispatch.py')
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.dict(os.environ, {'AMP_ORB_RESOURCES': str(path), 'ORB_OPERATION': 'delete',
                                     'ORB_ID': 'amp-template-check'}, clear=True):
            self.assertEqual(module.inputs(), config)
        self.assertEqual(config['max_running_orbs'], 1)

    def test_workflow_documents_actual_scope_and_data_boundary(self):
        path = SKILL/'SKILL.md'
        self.assertTrue(path.is_file(), 'Public workflow is missing')
        text = path.read_text() + (SKILL/'references/operations.md').read_text()
        for phrase in ('ORB_TOKEN', 'ORB_SNAPSHOT_ID', 'ORB_TYPE', 'AMP_URL',
                       'AMP_ORB_PROVIDER_TOKEN', 'ARM64', 'exactly one', 'outbound HTTPS',
                       'ceilings', 'not reservations', 'memory', 'host-local',
                       'archiving', 'Public Portals', 'metadata', 'egress',
                       'host-admin', 'multi-tenant', 'inference', 'stored with the thread',
                       'passwordless sudo', '270', 'offline', 'plan-dependent'):
            self.assertIn(phrase, text)
        examples = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        self.assertTrue(examples)
        for example in examples:
            ast.parse(example)
        self.assertNotIn('--token ', text)
        self.assertNotRegex(text, r'/(?:opt/data|Users/|home/[^\s`]+)')
        self.assertNotRegex(text, r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')


if __name__ == '__main__':
    unittest.main()
