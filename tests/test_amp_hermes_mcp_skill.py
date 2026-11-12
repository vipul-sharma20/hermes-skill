"""Static documentation-contract checks, not runtime security or end-to-end evidence."""
import ast
import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'amp-hermes-mcp' / 'SKILL.md'

class AmpHermesSkillTests(unittest.TestCase):
    def content(self):
        self.assertTrue(SKILL.is_file(), 'Reusable Amp/Hermes skill is missing')
        return SKILL.read_text(encoding='utf-8')

    def test_skill_exists_with_standard_frontmatter(self):
        text = self.content()
        match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
        if match is None:
            raise AssertionError('Missing standard YAML frontmatter')
        data = yaml.safe_load(match.group(1))
        self.assertEqual(data['name'], 'amp-hermes-mcp')
        self.assertLessEqual(len(data['description']),60)
        self.assertTrue(data['description'].endswith('.'))
        self.assertEqual(data['platforms'],['linux'])
        self.assertIn('Vipul Sharma',data['author'])
        self.assertIn('Hermes Agent',data['author'])
        for name in data['metadata']['hermes']['related_skills']:
            self.assertTrue((ROOT/'skills'/name/'SKILL.md').is_file())

    def test_contract_keeps_consultation_separate_from_approval(self):
        text=self.content()
        for required in ['get_context','ask_hermes','request_action','get_action_status',
            'anthropic/requiresUserInteraction','pending_owner_approval','completed','failed','declined',
            'separate owner approval','not a turnkey server']:
            with self.subTest(required=required):self.assertIn(required,text)

    def test_safety_includes_less_obvious_runtime_bypasses(self):
        text=self.content()
        for control in ['enabled_toolsets=[]','skip_memory=True','skip_background_review=True',
            'skip_context_files=True','load_soul_identity=False','HERMES_SAFE_MODE',
            '_execute_tool_calls','_build_system_prompt_parts','_build_system_prompt',
            '_skip_mcp_refresh','_persist_disabled','_session_json_enabled','compressor',
            'ensure_ascii=False','symlink','SHA256','multiplayer']:
            with self.subTest(control=control):self.assertIn(control,text)

    def test_documentation_requires_fail_closed_compatibility_startup_gate(self):
        text = self.content()
        section = text.split('### 3. Make consultation structurally powerless', 1)[1].split('### 4.', 1)[0]
        for required in [
            (
                '**Compatibility startup gate:** Before any model request, verify the installed '
                'constructor options, private prompt/tool-dispatch hooks, and zero-tool/privacy '
                'invariants above.'
            ),
            (
                'If any are absent, changed, unsupported or unverifiable, abort startup '
                'before any model request.'
            ),
            'Never silently ignore unsupported options or fall back to a normal `AIAgent`.',
        ]:
            with self.subTest(required=required):
                self.assertIn(required, section)

    def test_multiplayer_setting_documents_current_label_and_limits(self):
        text = self.content()
        section = text.split('### 7. Register the correct Amp scope', 1)[1].split('### 8.', 1)[0]
        for required in [
            'disable **Use in Multiplayer Threads** and verify the saved setting after reload.',
            (
                'This is accident-prevention, not adversarial server-side authorization; '
                'a determined contributor can bypass it.'
            ),
            'It does not apply to local `amp.mcpServers`.',
        ]:
            with self.subTest(required=required):
                self.assertIn(required, section)
        self.assertNotIn('Allow Use by Contributors in Multiplayer Threads', text)

    def test_documentation_requires_private_canary_support_and_visibility_readback(self):
        text = self.content()
        section = text.split('### 8. Prove the complete path and clean up', 1)[1].split('## Pitfalls', 1)[0]
        for required in [
            (
                'Before creating the canary, use installed `amp --help` to verify this version '
                'supports `--visibility private`; abort if unsupported or unverifiable.'
            ),
            (
                "Read back the created canary thread's actual visibility and confirm it is "
                '`private`; the CLI flag alone is not proof.'
            ),
            (
                'If visibility is not private or cannot be verified, stop the canary '
                'and do not make further MCP calls.'
            ),
        ]:
            with self.subTest(required=required):
                self.assertIn(required, section)

    def test_private_deployment_data_is_not_bundled(self):
        text=self.content()
        self.assertNotRegex(text,r'/(?:opt/data|opt/hermes|mnt/[^\s`]+|Users/[^\s`]+|home/[^\s`]+)')
        self.assertNotRegex(text,r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.assertNotRegex(text,r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b')
        self.assertNotRegex(text,r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        self.assertNotRegex(text,r'(?i)(?:bearer|api[_-]?key|password|secret)\s*[=:]\s*[\"\'][a-z0-9_-]{16,}')

    def test_sections_references_and_python_examples_are_valid(self):
        text=self.content()
        for title in ['When to Use','Prerequisites','Procedure','Pitfalls','Verification','References']:
            self.assertIn('## '+title,text)
        for url in ['https://ampcode.com/docs/customize/mcp',
            'https://hermes-agent.nousresearch.com/marketplace/mcp-serve',
            'https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration']:
            self.assertIn(url,text)
        examples=re.findall(r'```python\n(.*?)\n```',text,re.DOTALL)
        self.assertTrue(examples)
        for example in examples:ast.parse(example)
        self.assertLessEqual(len(text.splitlines()),220)

if __name__=='__main__':unittest.main()
