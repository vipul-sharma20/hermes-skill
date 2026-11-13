"""Offline documentation regressions; not runtime or deployment security proof."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
OWNED = ("optimize-image", "publish-note", "amp-hermes-mcp")


class LearningDocumentationUpdatesTest(unittest.TestCase):
    def main(self, skill):
        return (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")

    def reference(self, skill, name):
        relative = f"references/{name}.md"
        path = SKILLS / skill / relative
        self.assertTrue(path.is_file(), f"Missing documented workflow: {relative}")
        self.assertIn(f"`{relative}`", self.main(skill))
        return " ".join(path.read_text(encoding="utf-8").split())

    def require(self, text, phrases):
        for phrase in phrases:
            with self.subTest(contract=phrase):
                self.assertTrue(phrase in text, f"Missing documentation contract: {phrase}")

    def test_owned_main_docs_remain_bounded_attributed_and_link_support(self):
        for skill in OWNED:
            with self.subTest(skill=skill):
                text = self.main(skill)
                self.assertLessEqual(len(text.splitlines()), 220)
                self.assertIn("author: Vipul Sharma (vipul-sharma20), Hermes Agent", text)
                self.assertIn("license: MIT", text)
                for folder in ("references", "scripts", "templates"):
                    for path in (SKILLS / skill / folder).glob("*"):
                        if path.is_file():
                            self.assertIn(f"`{folder}/{path.name}`", text)
                self.assertIsNone(re.search(r"/(?:opt/data|home/[^/\s`]+|Users/[^/\s`]+)/", text))

    def test_image_verification_reads_encoded_metadata_and_orientation(self):
        text = self.reference("optimize-image", "metadata-and-upload-verification")
        self.require(text, (
            "Reopen every encoded output",
            "getexif()",
            "`exif`, `xmp`, `XML:com.adobe.xmp` and `icc_profile`",
            "`EXIF`, `XMP ` and `ICCP`",
            "EXIF orientation before metadata removal",
            "visually inspect",
            "actual decoded format",
            "`.webp`",
            "`.jpg` or `.jpeg`",
            "byte size and decoded dimensions",
            "Create the explicit `out` parent",
            "originals unchanged",
            "## Sources and attribution",
            "https://pillow.readthedocs.io/",
        ))

    def test_image_upload_only_requires_separate_scope_and_public_byte_proof(self):
        text = self.reference("optimize-image", "metadata-and-upload-verification")
        self.require(text, (
            "An upload-only request does not authorize a blog post",
            "no uploader",
            "publishing entrypoint",
            "separately reviewed",
            "Content-Type",
            "full SHA-256",
            "ETag",
            "public GET failure does not prove an origin write failed",
            "inspect the exact existing object before retrying",
            "credentials out of commands, logs and chat",
        ))
        self.assertIn("Upload-only authorization", self.main("optimize-image"))

    def test_edited_note_rereads_original_and_corrects_existing_file_once(self):
        text = self.reference("publish-note", "publishing-followups")
        self.require(text, (
            "re-read the original live source",
            "exact post ID",
            "edit timestamp",
            "transcript can be stale",
            "If the original source is inaccessible",
            "existing repository file",
            "same path",
            "not an update command",
            "do not rerun the publisher",
            "An edited message is not itself authorization to publish",
            "## Sources and attribution",
        ))
        self.assertIn("`references/publishing-followups.md`", self.main("publish-note"))

    def test_publish_status_distinguishes_commit_build_and_public_page(self):
        text = self.reference("publish-note", "publishing-followups")
        self.require(text, (
            "A commit, build/deploy result and public page are separate outcomes",
            "exact commit SHA",
            "run ID",
            "deployment pending",
            "public page and its media",
            "404 is not permission to republish",
            "does not guarantee a build was queued",
            "does not call a deployment provider",
            "Do not promise a fixed build duration",
        ))

    def test_media_removal_separates_exact_origin_keys_and_cdn_purge(self):
        text = self.reference("publish-note", "publishing-followups")
        self.require(text, (
            "Upload-only or media-replacement authorization does not authorize a note",
            "no upload-only, delete or purge command",
            "separate explicit authorization",
            "exact bucket and object keys",
            "old and replacement keys are disjoint",
            "origin absence",
            "CDN cache",
            "exact public URLs",
            "correct zone",
            "purge API result",
            "original URL",
            "404/410",
            "Never purge an entire zone",
            "cannot recall downloaded copies",
            "https://developers.cloudflare.com/cache/how-to/purge-cache/purge-by-single-file/",
            "https://developers.cloudflare.com/r2/objects/delete-objects/",
        ))

    def test_followups_preserve_public_credentials_requests_and_limit_precedence(self):
        text = self.reference("publish-note", "publishing-followups")
        self.require(text, (
            "dedicated `PUBLISH_NOTE_R2_ACCESS_KEY_ID` and `PUBLISH_NOTE_R2_SECRET_ACCESS_KEY`",
            "no secrets in config or request files",
            "ignores ambient AWS",
            "not a credential-discovery source",
            "session-specific request JSON",
            "positive request override, then config, then bundled defaults",
            "500000 bytes and 1920px",
            "standalone optimizer's 950000-byte default",
        ))
        main = self.main("publish-note")
        self.require(main, (
            "Explicit request fields",
            "take precedence over config",
            "Preserve existing explicit limits unless the user authorizes a change",
            "Text-only publication requires no R2 fields or credentials",
            "Never place user-controlled text or paths in a terminal command",
        ))
        self.assertNotIn("Tools/cloudflare.md", main + text)

    def test_amp_permission_inspection_never_inherits_historic_trust(self):
        text = self.reference("amp-hermes-mcp", "permission-modes-and-artifacts")
        self.require(text, (
            "service factory",
            "worker initialization",
            "runtime tool catalog",
            "`_meta`",
            "owner policy",
            "old canaries",
            "do not invoke `request_action` to discover",
            "outside this scoped recipe",
            "no authorization to change trust mode",
            "returned private data enters the caller's model context",
            "Read-only catalog inspection is not end-to-end proof",
            "## Sources and attribution",
        ))
        main = self.main("amp-hermes-mcp")
        self.require(main, (
            "zero-tool central-runtime consultation",
            "Never execute the request",
            "pending_owner_approval",
            "separate owner approval",
            "Ask First",
            "anthropic/requiresUserInteraction",
            "abort startup before any model request",
        ))
        self.assertNotRegex(main + text, r"--(?:yolo|dangerously[-\w]*)\b")

    def test_private_amp_artifact_handoff_verifies_integrity_before_import(self):
        text = self.reference("amp-hermes-mcp", "permission-modes-and-artifacts")
        self.require(text, (
            "`amp files get --help`",
            "existing authenticated CLI",
            "anonymous attachment URL",
            "protected temporary location",
            "full SHA-256",
            "trusted owner channel",
            "before parsing, importing or executing",
            "`git bundle verify`",
            "prerequisite public history",
            "exact full commit",
            "fast-forward",
            "Do not fabricate equivalent content",
            "does not change the bridge's artifact schema",
            "no public rehosting",
            "separate owner approval",
            "https://git-scm.com/docs/git-bundle",
        ))


if __name__ == "__main__":
    unittest.main()
