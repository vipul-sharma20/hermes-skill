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
                            self.assertIn(f"`{folder}/{supporting_file.name}`", text)

    def test_readme_uses_valid_direct_and_tap_install_forms(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "hermes skills install vipul-sharma20/hermes-skill/skills/<skill-name>",
            readme,
        )
        self.assertIn(
            "hermes skills install vipul-sharma20/hermes-skill/<skill-name>",
            readme,
        )

    def test_publish_note_photo_credentials_are_optional_and_dedicated(self):
        text = (SKILLS / "publish-note" / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if match is None:
            self.fail("Missing publish-note frontmatter")
        frontmatter = yaml.safe_load(match.group(1))
        variables = frontmatter["required_environment_variables"]

        self.assertEqual(
            {item["name"] for item in variables},
            {
                "PUBLISH_NOTE_R2_ACCESS_KEY_ID",
                "PUBLISH_NOTE_R2_SECRET_ACCESS_KEY",
            },
        )
        self.assertTrue(all(item.get("optional") is True for item in variables))

    def test_bundled_image_optimizer_copies_are_identical(self):
        standalone = SKILLS / "optimize-image" / "scripts" / "image_optimizer.py"
        publisher = SKILLS / "publish-note" / "scripts" / "image_optimizer.py"

        self.assertEqual(standalone.read_bytes(), publisher.read_bytes())


if __name__ == "__main__":
    unittest.main()
