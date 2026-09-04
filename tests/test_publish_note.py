import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "publish-note"
    / "scripts"
    / "publish_note.py"
)
spec = importlib.util.spec_from_file_location("published_note", MODULE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class NoteTextTest(unittest.TestCase):
    def test_lifts_trailing_tags_without_rewriting_body(self):
        body, tags, draft = module.parse_note_text(
            "fixed the keyboard firmware #hardware #weekend"
        )

        self.assertEqual(body, "fixed the keyboard firmware")
        self.assertEqual(tags, ["hardware", "weekend"])
        self.assertFalse(draft)

    def test_draft_prefix_is_removed_and_recorded(self):
        body, tags, draft = module.parse_note_text("/draft work in progress")

        self.assertEqual(body, "work in progress")
        self.assertEqual(tags, [])
        self.assertTrue(draft)


class MarkdownTest(unittest.TestCase):
    def test_builds_text_only_note(self):
        markdown = module.build_note_markdown(
            frontmatter_date="2099-12-31T23:59:00+00:00",
            tags=["example"],
            images=[],
            draft=False,
            body="hello world",
        )

        self.assertIn("date: 2099-12-31T23:59:00+00:00", markdown)
        self.assertIn("tags: [example]", markdown)
        self.assertTrue(markdown.endswith("hello world\n"))


class ConfigTest(unittest.TestCase):
    def test_rejects_unreplaced_template_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                '{"repo":"REPLACE_WITH_OWNER_REPO","branch":"main",'
                '"site_url":"https://example.com","image_base_url":"https://images.example.com",'
                '"r2_account_id":"REPLACE_WITH_R2_ACCOUNT_ID","bucket":"example"}',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(module.PublishError, "placeholder"):
                module.load_config(path)


class DatePartsTest(unittest.TestCase):
    def test_uses_configured_timezone(self):
        parts = module.site_date_parts(
            "Asia/Kolkata",
            datetime(2099, 12, 31, 20, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(parts.date, "2100-01-01")
        self.assertEqual(parts.time, "0130")
        self.assertTrue(parts.frontmatter.endswith("+05:30"))


if __name__ == "__main__":
    unittest.main()
