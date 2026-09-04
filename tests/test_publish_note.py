import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import yaml

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
        self.assertIn('tags: ["example"]', markdown)
        self.assertTrue(markdown.endswith("hello world\n"))

    def test_reserved_looking_tags_remain_strings(self):
        markdown = module.build_note_markdown(
            frontmatter_date="2099-12-31T23:59:00+00:00",
            tags=["true", "null", "123", "2099-12-31"],
            images=[],
            draft=False,
            body="tag types",
        )
        frontmatter = yaml.safe_load(markdown.split("---", 2)[1])

        self.assertEqual(frontmatter["tags"], ["true", "null", "123", "2099-12-31"])


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

    def test_text_only_config_does_not_require_r2_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                '{"repo":"example/site","branch":"main",'
                '"site_url":"https://example.com","timezone":"UTC"}',
                encoding="utf-8",
            )

            config = module.load_config(path, require_images=False)

            self.assertEqual(config["repo"], "example/site")

    def test_text_only_dry_run_does_not_access_r2_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "config.json"
            path.write_text(
                '{"repo":"example/site","branch":"main",'
                '"site_url":"https://example.com","timezone":"UTC"}',
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = module.run([
                    "--config", str(path), "--text", "text only", "--dry-run"
                ])

            self.assertEqual(code, 0)
            self.assertIn("text only", output.getvalue())


class RequestFileTest(unittest.TestCase):
    def test_shell_metacharacters_in_note_text_are_not_executed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config = root / "config.json"
            text_file = root / "note.txt"
            request = root / "request.json"
            config.write_text(
                '{"repo":"example/site","branch":"main",'
                '"site_url":"https://example.com","timezone":"UTC"}',
                encoding="utf-8",
            )
            text_file.write_text("hello $(touch SHOULD_NOT_EXIST)", encoding="utf-8")
            request.write_text(
                json.dumps({
                    "config": str(config),
                    "text_file": str(text_file),
                    "images": [],
                    "dry_run": True,
                }),
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                code = module.run(["--request", str(request)])

            self.assertEqual(code, 0)
            self.assertIn("hello $(touch SHOULD_NOT_EXIST)", output.getvalue())
            self.assertFalse((root / "SHOULD_NOT_EXIST").exists())


class R2CredentialTest(unittest.TestCase):
    def test_rejects_unrelated_ambient_aws_credentials(self):
        aws_secret_name = "AWS_" + "SECRET_ACCESS_KEY"  # pragma: allowlist secret -- synthetic name
        ambient = {
            "AWS_ACCESS_KEY_ID": "ambient-placeholder",
            aws_secret_name: "ambient-placeholder",  # pragma: allowlist secret -- synthetic value
        }
        with patch.dict(os.environ, ambient, clear=True):
            with self.assertRaisesRegex(module.PublishError, "dedicated R2 credentials"):
                module.r2_client("example-account")

    def test_passes_only_dedicated_credentials_to_boto3(self):
        aws_secret_name = "AWS_" + "SECRET_ACCESS_KEY"  # pragma: allowlist secret -- synthetic name
        r2_secret_name = "PUBLISH_NOTE_R2_" + "SECRET_ACCESS_KEY"  # pragma: allowlist secret -- synthetic name
        values = {
            "AWS_ACCESS_KEY_ID": "ambient-placeholder",
            aws_secret_name: "ambient-placeholder",  # pragma: allowlist secret -- synthetic value
            "PUBLISH_NOTE_R2_ACCESS_KEY_ID": "dedicated-placeholder",
            r2_secret_name: "dedicated-placeholder",  # pragma: allowlist secret -- synthetic value
        }
        with patch.dict(os.environ, values, clear=True):
            with patch("boto3.client", return_value="client") as client:
                result = module.r2_client("example-account")

        self.assertEqual(result, "client")
        kwargs = client.call_args.kwargs
        self.assertEqual(kwargs["aws_access_key_id"], "dedicated-placeholder")
        self.assertEqual(kwargs["aws_secret_access_key"], "dedicated-placeholder")
        self.assertNotIn("ambient-placeholder", kwargs.values())


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
