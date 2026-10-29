import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import yaml
from PIL import Image, ImageCms, TiffImagePlugin

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

    def test_image_defaults_match_microblog_policy(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "photo.png"
            Image.new("RGB", (2048, 1024), "blue").save(source)
            config = Path(__file__).parent / "fixtures" / "publish-note-config.json"
            output = io.StringIO()

            with (
                patch.object(module, "prepare_images", wraps=module.prepare_images) as prepare,
                patch.object(module, "r2_client", side_effect=AssertionError("offline")),
                patch.object(module, "gh_json", side_effect=AssertionError("offline")),
                redirect_stdout(output), redirect_stderr(io.StringIO()),
            ):
                code = module.run([
                    "--config", str(config), "--image", str(source), "--dry-run"
                ])

            self.assertEqual(code, 0)
            prepare.assert_called_once()
            self.assertEqual(prepare.call_args.kwargs["max_image_bytes"], 500_000)
            self.assertEqual(prepare.call_args.kwargs["max_image_edge"], 1_920)
            frontmatter = yaml.safe_load(output.getvalue().split("---", 2)[1])
            image = frontmatter["images"][0]
            self.assertTrue(image["src"].endswith(".webp"))
            self.assertEqual((image["width"], image["height"]), (1920, 960))

    def test_image_example_uses_microblog_policy(self):
        example = MODULE.parents[1] / "templates" / "config.images.example.json"
        config = json.loads(example.read_text(encoding="utf-8"))

        self.assertEqual(config["max_image_bytes"], 500_000)
        self.assertEqual(config["max_image_edge"], 1_920)

    def test_explicit_image_limits_override_defaults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "photo.png"
            Image.new("RGB", (1024, 512), "blue").save(source)
            config = json.loads(
                (Path(__file__).parent / "fixtures" / "publish-note-config.json")
                .read_text(encoding="utf-8")
            )
            config.update(max_image_bytes=200_000, max_image_edge=960)
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            cases = (
                ("config", 200_000, 960),
                ("cli", 75_000, 640),
                ("request", 100_000, 800),
            )
            for via, budget, edge in cases:
                with self.subTest(via=via):
                    args = [
                        "--config", str(config_path), "--image", str(source), "--dry-run"
                    ]
                    if via == "cli":
                        args.extend([
                            "--max-image-bytes", str(budget), "--max-image-edge", str(edge)
                        ])
                    elif via == "request":
                        request = root / "request.json"
                        request.write_text(json.dumps({
                            "config": str(config_path), "images": [str(source)],
                            "dry_run": True, "max_image_bytes": budget,
                            "max_image_edge": edge,
                        }), encoding="utf-8")
                        args = ["--request", str(request)]
                    output = io.StringIO()
                    with (
                        patch.object(module, "optimize_image", wraps=module.optimize_image) as optimize,
                        patch.object(module, "r2_client", side_effect=AssertionError("offline")),
                        patch.object(module, "gh_json", side_effect=AssertionError("offline")),
                        redirect_stdout(output), redirect_stderr(io.StringIO()),
                    ):
                        code = module.run(args)

                    self.assertEqual(code, 0)
                    optimize.assert_called_once()
                    self.assertEqual(optimize.call_args.kwargs["max_bytes"], budget)
                    self.assertEqual(optimize.call_args.kwargs["max_edge"], edge)
                    frontmatter = yaml.safe_load(output.getvalue().split("---", 2)[1])
                    image = frontmatter["images"][0]
                    self.assertTrue(image["src"].endswith(".webp"))
                    self.assertEqual((image["width"], image["height"]), (edge, edge // 2))


class PreparedImageTest(unittest.TestCase):
    def test_prepare_images_produces_metadata_free_webp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "camera.webp"
            exif = Image.Exif()
            exif[274] = 6  # Rotate the landscape pixels into portrait orientation.
            exif[315] = "synthetic-test-artist"
            exif[34853] = {
                1: "N",
                2: tuple(TiffImagePlugin.IFDRational(n) for n in (12, 34, 56)),
                3: "E",
                4: tuple(TiffImagePlugin.IFDRational(n) for n in (78, 9, 10)),
            }
            xmp = (
                b'<x:xmpmeta xmlns:x="adobe:ns:meta/">'
                b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                b'<rdf:Description xmlns:exif="http://ns.adobe.com/exif/1.0/" '
                b'exif:GPSLatitude="12,34,56N"/>'
                b'</rdf:RDF></x:xmpmeta>'
            )
            icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
            Image.new("RGB", (2048, 1024), (100, 150, 200)).save(
                source, format="WEBP", lossless=True,
                exif=exif, xmp=xmp, icc_profile=icc,
            )
            # Prove these are genuine source metadata, not empty test inputs.
            with Image.open(source) as original:
                self.assertEqual(original.getexif()[274], 6)
                self.assertEqual(original.getexif()[315], "synthetic-test-artist")
                self.assertEqual(original.getexif().get_ifd(34853)[1], "N")
                self.assertEqual(original.info["xmp"], xmp)
                self.assertEqual(original.info["icc_profile"], icc)

            parts = module.site_date_parts(
                "UTC", datetime(2099, 12, 31, 23, 59, tzinfo=timezone.utc)
            )
            images = module.prepare_images(
                [source], prefix="/micro/", parts=parts, suffix="a",
                image_base_url="https://images.example.com/",
                max_image_bytes=500_000, max_image_edge=1_920,
            )

            self.assertEqual(len(images), 1)
            image = images[0]
            digest = hashlib.sha256(image.data).hexdigest()[:16]
            expected_key = f"micro/2099/2099-12-31-2359a/{digest}.webp"
            with self.subTest(contract="WebP byte signature"):
                self.assertEqual(image.data[:4], b"RIFF")
                self.assertEqual(image.data[8:12], b"WEBP")
            with self.subTest(contract="object key"):
                self.assertEqual(image.key, expected_key)
            with self.subTest(contract="public URL"):
                self.assertEqual(image.url, f"https://images.example.com/{expected_key}")
            with self.subTest(contract="policy constraints"):
                self.assertLessEqual(len(image.data), 500_000)
                self.assertEqual((image.width, image.height), (960, 1920))
                self.assertEqual(image.quality, 88)
            with Image.open(io.BytesIO(image.data)) as result:
                with self.subTest(contract="decoded format"):
                    self.assertEqual(result.format, "WEBP")
                with self.subTest(contract="decoded dimensions"):
                    self.assertEqual(result.size, (image.width, image.height))
                with self.subTest(contract="source metadata omitted"):
                    self.assertFalse(result.getexif())
                    self.assertNotIn(34853, result.getexif())
                    for name in ("exif", "xmp", "XML:com.adobe.xmp", "icc_profile"):
                        self.assertNotIn(name, result.info)
                    for marker in (b"Exif", b"synthetic-test-artist", xmp, icc):
                        self.assertNotIn(marker, image.data)

    def test_upload_images_sends_webp_content_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "photo.png"
            Image.new("RGB", (64, 32), "purple").save(source)
            images = module.prepare_images(
                [source], prefix="micro",
                parts=module.site_date_parts(
                    "UTC", datetime(2099, 12, 31, 23, 59, tzinfo=timezone.utc)
                ),
                suffix="", image_base_url="https://images.example.com",
                max_image_bytes=500_000, max_image_edge=1_920,
            )
            client = Mock(spec=["put_object"])

            module.upload_images(client, "example-bucket", images)

            client.put_object.assert_called_once()
            uploaded = client.put_object.call_args.kwargs
            with Image.open(io.BytesIO(uploaded["Body"])) as result:
                self.assertEqual(result.format, "WEBP")
            self.assertEqual(uploaded["ContentType"], "image/webp")
            client.put_object.assert_called_once_with(
                Bucket="example-bucket", Key=images[0].key, Body=images[0].data,
                ContentType="image/webp", ContentDisposition="inline",
                CacheControl="public, max-age=31536000, immutable",
                Metadata={"sha256": hashlib.sha256(images[0].data).hexdigest()[:16]},
            )


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
