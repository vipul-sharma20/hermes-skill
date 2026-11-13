"""Offline publication contracts for the maintenance procedure package."""
import re
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills" / "skill-library-maintenance"
REFERENCES = (
    "hermes-learning-approvals.md",
    "draft-consolidation-validation.md",
    "distribution-audit-patterns.md",
    "release-packaging.md",
    "publishing-contracts.md",
    "trust-boundary-review.md",
    "provenance-privacy.md",
)


class SkillLibraryMaintenanceTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((PACKAGE / "SKILL.md").is_file(), "maintenance package is missing")
        self.text = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")

    def reference(self, name):
        path = PACKAGE / "references" / name
        self.assertTrue(path.is_file(), f"missing bundled reference: {name}")
        return path.read_text(encoding="utf-8")

    def test_portable_metadata_and_actionable_entry_point(self):
        match = re.match(r"\A---\n(.*?)\n---\n", self.text, re.DOTALL)
        if match is None:
            self.fail("maintenance frontmatter is missing")
        meta = yaml.safe_load(match.group(1))
        self.assertEqual(meta["name"], "skill-library-maintenance")
        self.assertLessEqual(len(meta["description"]), 60)
        self.assertTrue(meta["description"].endswith("."))
        self.assertEqual(meta["license"], "MIT")
        self.assertTrue(meta["author"].startswith("Vipul Sharma"))
        self.assertIn("Hermes Agent", meta["author"])
        self.assertEqual(set(meta["platforms"]), {"linux", "macos", "windows"})
        self.assertLessEqual(len(self.text.splitlines()), 220)
        for heading in ("When to Use", "Prerequisites", "Procedure", "Pitfalls", "Verification"):
            self.assertIn(f"## {heading}", self.text)

    def test_accounting_is_not_substantive_review_or_latest_wins(self):
        text = self.text + self.reference("draft-consolidation-validation.md")
        for concept in (
            "actual payloads", "ID-keyed", "exact ID-set", "content", "file_content",
            "merged", "superseded", "rejected", "deferred", "intervening", "already satisfied",
        ):
            self.assertIn(concept, text)
        self.assertIn("not proof", text)
        self.assertIn("newest", text)

    def test_permissions_and_timed_out_approvals_are_not_bypassed(self):
        text = self.text + self.reference("hermes-learning-approvals.md")
        for concept in (
            "fresh consent", "timed out", "separate permissions", "protected",
            "existing pending", "approvals.mode", "write_approval", "staged",
        ):
            self.assertIn(concept, text)
        self.assertIn("Never execute proposal-supplied", text)

    def test_publication_audit_is_folded_in_without_another_skill(self):
        self.assertFalse((ROOT / "skills" / "publication-audit").exists())
        self.assertFalse((ROOT / "skills" / "job-opportunity-research").exists())
        for name in REFERENCES:
            self.reference(name)
            self.assertIn(f"`references/{name}`", self.text)
        text = self.reference("release-packaging.md")
        for concept in ("outbound history", "dedicated", "request", "isolated", "procedure-only"):
            self.assertIn(concept, text)

    def test_side_effect_receipts_are_distinct(self):
        text = self.reference("publishing-contracts.md")
        for concept in ("source commit", "build", "public page", "exactly-once", "unknown", "confirmation"):
            self.assertIn(concept, text)
        self.assertIn("never publish again", text)

    def test_security_and_privacy_patterns_do_not_claim_an_implementation(self):
        trust = self.reference("trust-boundary-review.md")
        privacy = self.reference("provenance-privacy.md")
        for concept in ("symlink", "hardlink", "FIFO", "hooks", "not a bundled implementation"):
            self.assertIn(concept, trust)
        for concept in ("exact revision", "not anonymization", "raw", "traceback", "unknown"):
            self.assertIn(concept, privacy)

    def test_relocated_package_has_complete_local_reference_closure(self):
        with tempfile.TemporaryDirectory() as temporary:
            relocated = Path(temporary) / "maintenance"
            shutil.copytree(PACKAGE, relocated)
            for path in relocated.rglob("*.md"):
                for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                    if "://" in link or link.startswith(("#", "mailto:")):
                        continue
                    target = (path.parent / link.split("#", 1)[0]).resolve()
                    self.assertTrue(target.is_relative_to(relocated.resolve()))
                    self.assertTrue(target.is_file(), f"broken link in {path.name}: {link}")
            self.assertEqual(
                {path.name for path in (relocated / "references").glob("*.md")},
                set(REFERENCES),
            )

    def test_release_contains_no_runtime_or_private_audit_payload(self):
        for path in PACKAGE.rglob("*"):
            self.assertFalse(path.is_symlink())
            if path.is_file():
                self.assertEqual(path.suffix, ".md")
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"/(?:opt/data|home/[^/\s]+|Users/[^/\s]+)/")
                self.assertNotRegex(text, r"(?:gh[oprs]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,})")
                self.assertNotRegex(text, r"\b(?:before|original)-pending\.tar\.gz\b")
                self.assertNotRegex(text, r"\b20\d{6}T\d{6}Z\b")


if __name__ == "__main__":
    unittest.main()
