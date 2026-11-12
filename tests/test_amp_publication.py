"""Guard the entire distributed Amp skill payload, not private deployments."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMP_SKILLS = ("amp-hermes-mcp", "amp-self-hosted-orbs")
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".ruff_cache"}


class AmpPublicationTest(unittest.TestCase):
    def payload(self, name):
        root = ROOT / "skills" / name
        self.assertTrue((root / "SKILL.md").is_file(), f"Missing skill: {name}")
        for path in sorted(root.rglob("*")):
            if CACHE_DIRS.intersection(path.relative_to(root).parts):
                continue
            self.assertFalse(path.is_symlink(), f"Symlink in skill payload: {path}")
            if path.is_file():
                yield path, path.read_text(encoding="utf-8")

    def test_both_amp_skills_have_a_readme_install_target(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in AMP_SKILLS:
            with self.subTest(skill=name):
                self.assertIn(f"](skills/{name}/SKILL.md)", readme)
                self.assertTrue((ROOT / "skills" / name / "SKILL.md").is_file())

    def test_distributed_payload_excludes_personal_deployment_data(self):
        patterns = {
            "personal absolute path": r"/(?:opt/data|opt/hermes|mnt/nvme[0-9]*|Users/[^/\s`]+)(?:/|\b)",
            "email address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "private key": r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----",
            "live Amp provider token": r"\baop_live_[A-Za-z0-9_-]{16,}",
            "live Amp thread identifier": r"\bT-[0-9a-f]{8}-[0-9a-f-]{20,}",
            "workspace/account UUID": r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
        }
        for name in AMP_SKILLS:
            for path, text in self.payload(name):
                for label, pattern in patterns.items():
                    with self.subTest(skill=name, file=str(path.relative_to(ROOT)), check=label):
                        self.assertIsNone(re.search(pattern, text), f"{label} in {path.name}")
                self.assertNotIn(path.suffix, {".db", ".sqlite", ".sqlite3", ".log", ".jsonl", ".zip"})


if __name__ == "__main__":
    unittest.main()
