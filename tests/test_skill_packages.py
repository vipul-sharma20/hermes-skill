import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillPackageTest(unittest.TestCase):
    def test_every_skill_has_publishable_frontmatter(self):
        skill_files = sorted(SKILLS.glob("*/SKILL.md"))
        self.assertGreaterEqual(len(skill_files), 4)
        required = {"name", "description", "version", "author", "license", "platforms"}

        for path in skill_files:
            with self.subTest(skill=path.parent.name):
                text = path.read_text(encoding="utf-8")
                match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
                if match is None:
                    self.fail(f"Missing YAML frontmatter: {path}")
                frontmatter = yaml.safe_load(match.group(1))
                self.assertEqual(required - set(frontmatter), set())
                self.assertLessEqual(len(frontmatter["description"]), 60)
                self.assertTrue(frontmatter["description"].endswith("."))
                self.assertIn("Hermes Agent", frontmatter["author"])
                self.assertIn("hermes", frontmatter.get("metadata", {}))

    def test_supporting_files_are_referenced_by_skill(self):
        for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
            text = skill_file.read_text(encoding="utf-8")
            for folder in ("scripts", "references", "templates"):
                directory = skill_file.parent / folder
                if not directory.exists():
                    continue
                for supporting_file in directory.iterdir():
                    if supporting_file.is_file():
                        with self.subTest(skill=skill_file.parent.name, file=supporting_file.name):
                            self.assertIn(f"{folder}/{supporting_file.name}", text)


if __name__ == "__main__":
    unittest.main()
