"""Offline contracts for prose packages, not tests of deployed integrations."""

import re
import shutil
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
PACKAGES = {
    "state-change-monitoring": {
        "platforms": ["linux", "macos", "windows"],
        "references": {"parser-and-delivery.md", "travel-contracts.md", "cloud-usage.md"},
    },
    "self-hosted-operations": {
        "platforms": ["linux"],
        "references": {
            "metrics.md", "diagnostics.md", "control-plane.md", "recovery.md",
            "uploads.md", "runtime-overlays.md",
        },
    },
    "licensed-media-curation": {
        "platforms": ["linux", "macos", "windows"],
        "references": {
            "bounded-handoffs.md", "pixel-review.md", "asset-delivery.md",
            "identity-and-coverage.md", "provider-evidence.md", "evidence-model.md",
        },
    },
    "container-storage-migration": {
        "platforms": ["linux"],
        "references": {"cutover.md", "verification.md"},
    },
}


def package_files(root):
    """Reject external dependencies before following package-local links."""
    assert (root / "SKILL.md").is_file(), f"Missing procedure package: {root.name}"
    files = {}
    for path in sorted(root.rglob("*")):
        assert not path.is_symlink(), f"Symlink in procedure package: {path.name}"
        if path.is_file():
            assert path.suffix == ".md", f"Procedure package must be prose-only: {path.name}"
            files[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
    return files


def assert_reference_closure(root, files):
    """Check both Markdown links and the repository's backticked support paths."""
    entry = files["SKILL.md"]
    for relative in files.keys() - {"SKILL.md"}:
        assert f"`{relative}`" in entry, f"Unreferenced support file: {relative}"
    edges = {relative: set() for relative in files}
    for relative, text in files.items():
        targets = re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text)
        targets += re.findall(r"`((?:references|templates|scripts)/[^`\s]+)`", text)
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http"}:
                continue
            if not parsed.path:
                continue
            path = PurePosixPath(unquote(parsed.path))
            assert not parsed.scheme and not parsed.netloc, f"Nonportable link: {target}"
            assert not path.is_absolute(), f"Absolute reference: {target}"
            resolved = (root / relative).parent.joinpath(*path.parts).resolve()
            assert resolved.is_relative_to(root.resolve()), f"Escaping reference: {target}"
            local = resolved.relative_to(root.resolve()).as_posix()
            assert local in files, f"Missing local reference: {target} from {relative}"
            edges[relative].add(local)
    visited, pending = set(), ["SKILL.md"]
    while pending:
        relative = pending.pop()
        if relative not in visited:
            visited.add(relative)
            pending.extend(edges[relative] - visited)
    assert visited == set(files), f"Unreachable support files: {set(files) - visited}"


class ProcedureContract(unittest.TestCase):
    """Inherited checks exercise each copied package, independently of its draft."""

    skill: str

    def payload(self):
        return package_files(SKILLS / self.skill)

    def section(self, relative, *fragments):
        text = re.sub(r"\s+", " ", self.payload()[relative])
        for fragment in fragments:
            self.assertIn(fragment, text, f"Lost safety contract in {self.skill}/{relative}")

    def paragraph(self, relative, *fragments):
        paragraphs = [
            re.sub(r"\s+", " ", paragraph)
            for paragraph in re.split(r"\n\s*\n", self.payload()[relative])
        ]
        self.assertTrue(
            any(all(fragment in paragraph for fragment in fragments) for paragraph in paragraphs),
            f"Safety rule and qualification must stay together: {fragments}",
        )

    def check_portable_metadata_and_prose_only_payload(self):
        files = self.payload()
        text = files["SKILL.md"]
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if match is None:
            self.fail("Missing frontmatter at byte zero")
        metadata = yaml.safe_load(match.group(1))
        required = {"name", "description", "version", "author", "license", "platforms", "metadata"}
        self.assertFalse(required - metadata.keys())
        self.assertEqual(metadata["name"], self.skill)
        self.assertRegex(metadata["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(metadata["license"], "MIT")
        self.assertEqual(metadata["author"], "Vipul Sharma (vipul-sharma20), Hermes Agent")
        self.assertLessEqual(len(metadata["description"]), 60)
        self.assertTrue(metadata["description"].endswith("."))
        self.assertEqual(metadata["platforms"], PACKAGES[self.skill]["platforms"])
        hermes = metadata["metadata"]["hermes"]
        self.assertTrue(hermes["tags"])
        self.assertEqual(hermes["related_skills"], [])
        self.assertLessEqual(len(text.splitlines()), 220)
        for heading in ("## When to Use", "## Prerequisites", "## Procedure", "## Pitfalls", "## Verification"):
            self.assertIn(heading, text)
        expected = {"SKILL.md"} | {f"references/{name}" for name in PACKAGES[self.skill]["references"]}
        self.assertEqual(set(files), expected, "No runtimes or raw review archives belong in these packages")

    def check_isolated_relocation_has_complete_references(self):
        original = self.payload()
        with tempfile.TemporaryDirectory() as temporary:
            relocated = Path(temporary) / "unrelated-location" / self.skill
            shutil.copytree(SKILLS / self.skill, relocated)
            copied = package_files(relocated)
            self.assertEqual(copied, original)
            assert_reference_closure(relocated, copied)

    def check_payload_excludes_private_context(self):
        patterns = {
            "machine path": r"/(?:opt|home|Users|mnt|workspace|root)/[^\s`]+",
            "email": r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}",
            "IP address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "private hostname": r"\b[\w-]+\.(?:local|internal|lan|tailnet)\b",
            "raw UUID": r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b",
            "private key": r"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----",
            "credential value": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|aop_live_[\w-]{16,})\b",
            "raw review provenance": r"skill-backlog-cleanup|skill-publication/|\d{8}T\d{6}Z|@session:",
        }
        for relative, text in self.payload().items():
            for label, pattern in patterns.items():
                with self.subTest(file=relative, check=label):
                    self.assertNotRegex(text, pattern)
            self.assertNotRegex(text, r"https://coolify\.io/docs/api(?=[\s)]|$)")


class StateChangeMonitoringTest(ProcedureContract):
    skill = "state-change-monitoring"

    def test_metadata(self):
        self.check_portable_metadata_and_prose_only_payload()

    def test_relocation(self):
        self.check_isolated_relocation_has_complete_references()

    def test_privacy(self):
        self.check_payload_excludes_private_context()

    def test_consent_last_good_state_and_single_delivery_owner(self):
        self.paragraph("SKILL.md", "one-off lookup", "does not imply a watch")
        self.paragraph("SKILL.md", "Failures", "never replace successful observations")
        self.paragraph("SKILL.md", "unchanged ticks", "empty stdout", "Do not also post directly")
        self.paragraph("references/parser-and-delivery.md", "Atomic state writes", "not transactional network delivery")
        self.paragraph("references/parser-and-delivery.md", "Never mark delivery confirmed", "stdout")
        self.paragraph("references/parser-and-delivery.md", "Phone push", "OS", "user-observable")

    def test_identity_multiplicity_freshness_and_terminal_safety(self):
        self.paragraph("SKILL.md", "Stop at login/CAPTCHA", "unapproved provider")
        self.paragraph("references/parser-and-delivery.md", "refreshed fragments", "Never deduplicate equal values")
        self.paragraph("references/travel-contracts.md", "before interpreting", "Source-update time and check time")
        self.paragraph("references/travel-contracts.md", "after safety deadline/finished => no fetch", "expiry is not arrival")
        self.paragraph("references/travel-contracts.md", "wall-clock deadline", "Preserve last-good state")

    def test_cloud_accounting_and_scheduler_are_not_claimed_runtimes(self):
        self.section("SKILL.md", "procedure and test contracts", "not an untested watcher executable", "installed", "cronjob_manage")
        self.paragraph("references/cloud-usage.md", "does not authorize scheduling", "prohibit mutations")
        self.paragraph("references/cloud-usage.md", "No rows", "are not zero")
        self.paragraph("references/cloud-usage.md", "latest cumulative values", "never sum cumulative daily costs")
        self.paragraph("references/cloud-usage.md", "ListObjects", "cost classification is not permission")
        self.paragraph("references/cloud-usage.md", "fake HTTP", "Live authorized CLI output must be separately measured")


class SelfHostedOperationsTest(ProcedureContract):
    skill = "self-hosted-operations"

    def test_metadata(self):
        self.check_portable_metadata_and_prose_only_payload()

    def test_relocation(self):
        self.check_isolated_relocation_has_complete_references()

    def test_privacy(self):
        self.check_payload_excludes_private_context()

    def test_scope_denials_and_async_outcomes_fail_closed(self):
        self.paragraph("SKILL.md", "health-check request", "not permission", "restart services")
        self.paragraph("SKILL.md", "approval denial/timeout is a stop", "not an invitation to change transport")
        self.paragraph("SKILL.md", "Queued/accepted is not completed", "timeout does not imply rollback", "before retrying")
        self.paragraph("references/control-plane.md", "strict trusted known-host verification", "Clean up on normal/error exits")
        self.paragraph("references/control-plane.md", "schedule is not a successful artifact", "not a restore test")
        self.paragraph("references/control-plane.md", "Stop implementations remove containers", "that specific path is authorized")

    def test_measurement_identity_and_freshness_do_not_become_health_claims(self):
        self.paragraph("references/metrics.md", "Legacy `/api`", "installed", "no exact replacement")
        self.paragraph("references/metrics.md", "actual `values` timestamp/value pairs", "evaluation time")
        self.paragraph("references/metrics.md", "Missing data is unavailable", "never healthy zero")
        self.paragraph("references/diagnostics.md", "Broad inventories", "not argv/environment")
        self.paragraph("references/diagnostics.md", "SystemInfo.getProcessInfo", "measured monotonic interval", "process-churn undercount")
        self.paragraph("references/recovery.md", "changed host boot ID", "Do not issue another reboot")
        self.paragraph("references/diagnostics.md", "Recheck ID, URL and state", "never auto-dismiss unsaved-work warnings")

    def test_recovery_uploads_and_overlays_preserve_the_boundary(self):
        self.section("SKILL.md", "operator procedure", "no helper scripts")
        self.paragraph("references/recovery.md", "SQLite", "live main-file copy is insufficient", "WAL/SHM")
        self.paragraph("references/recovery.md", "ask for participation", "UI acceptance untested")
        self.paragraph("references/uploads.md", "readTimeout", "incoming body reads", "responseHeaderTimeout")
        self.paragraph("references/uploads.md", "not sufficient proof", "trusted TLS and authentication")
        self.paragraph("references/runtime-overlays.md", "exact-installed-version", "test actual module paths")
        self.paragraph("references/runtime-overlays.md", "exact permitted bytes accepted", "one byte above rejected")
        self.paragraph("references/runtime-overlays.md", "image-recreation durability separately", "proves none")


class LicensedMediaCurationTest(ProcedureContract):
    skill = "licensed-media-curation"

    def test_metadata(self):
        self.check_portable_metadata_and_prose_only_payload()

    def test_relocation(self):
        self.check_isolated_relocation_has_complete_references()

    def test_privacy(self):
        self.check_payload_excludes_private_context()

    def test_image_bound_rights_and_independent_evidence_tracks(self):
        self.paragraph("SKILL.md", "exact image", "version/scope", "contradictions")
        self.paragraph("references/evidence-model.md", "never one blanket boolean")
        self.paragraph("references/evidence-model.md", "Hash integrity is not legal", "ETag with SHA256")
        self.paragraph("references/provider-evidence.md", "oldid does not pin the binary", "selected binary revision digest")
        self.paragraph("references/provider-evidence.md", "Observation or dataset licensing", "photograph's grant")
        self.paragraph("references/provider-evidence.md", "numeric", "current provider license definitions")
        self.paragraph("references/identity-and-coverage.md", "requested label", "actually depicted")
        self.section("references/identity-and-coverage.md", "FUZZY", "do not repair spelling", "Require an actual capture statement")

    def test_actual_pixels_derivatives_and_handoff_are_separate_gates(self):
        self.paragraph("references/pixel-review.md", "generated sheet is not a viewing event", "actual detail")
        self.paragraph("references/pixel-review.md", "Review final detail and native thumbnail", "unseen derivative")
        self.section("references/pixel-review.md", "w <= ow and h <= oh", "actual bytes <= requested byte budget")
        self.paragraph("references/bounded-handoffs.md", "exact scope equality", "acquired", "withheld", "original integrity")
        self.paragraph("references/bounded-handoffs.md", "Synthetic fixtures test software", "not the real source's authenticity")
        self.paragraph("references/bounded-handoffs.md", "later edit invalidates", "last known-good outputs")
        self.section("SKILL.md", "not a bundled downloader", "not uploads", "no public-write or queue-mutation")

    def test_rate_limits_privacy_and_optional_storage_mutation_boundaries(self):
        self.paragraph("references/bounded-handoffs.md", "Retry-After", "Restarting a worker must not reset it", "Don't route around limits")
        self.paragraph("references/evidence-model.md", "share URLs and originals as potentially private", "access-bearing links")
        self.paragraph("references/asset-delivery.md", "No repository commit", "bucket creation is implied")
        self.paragraph("references/asset-delivery.md", "explicit approval", "unexpected third version", "conditional operations")
        self.paragraph("references/asset-delivery.md", "exact URL", "never purge a whole zone")
        self.paragraph("references/asset-delivery.md", "without a cache-busting query", "origin update", "different results")


class ContainerStorageMigrationTest(ProcedureContract):
    skill = "container-storage-migration"

    def test_metadata(self):
        self.check_portable_metadata_and_prose_only_payload()

    def test_relocation(self):
        self.check_isolated_relocation_has_complete_references()

    def test_privacy(self):
        self.check_payload_excludes_private_context()

    def test_storage_discovery_and_quiescence_precede_cutover(self):
        self.paragraph("SKILL.md", "not a one-command migration script", "does not authorize formatting")
        self.paragraph("references/cutover.md", "containerd", "different roots", "Do not combine relocation with backend/engine upgrade")
        self.paragraph("references/cutover.md", "data disk -> bind -> engine", "refuse an empty fallback directory")
        self.paragraph("references/cutover.md", "SELinux", "keep enforcing", "not prescribe a universal unconfined context")
        self.paragraph("references/cutover.md", "live-restore", "activation socket", "Final offline sync", "quiescent ROLLBACK")
        self.section("references/cutover.md", "exact prior-running set explicitly", "Do not restart the whole workflow blindly")

    def test_identity_and_frozen_copy_comparison_gate_destructive_cleanup(self):
        self.paragraph("references/verification.md", "JSON tuples become lists", "negative tests", "nonempty mount fixture")
        self.paragraph("references/verification.md", "OLD is the quiescent source", "not the active DEST", "no reported differences")
        self.paragraph("references/verification.md", "Explicit source-removal authorization", "non-symlink/non-special path", "without child mounts", "Frozen-copy proof still applies")
        self.paragraph("references/verification.md", "never broad prune/glob", "Keep rollback", "separately authorized")
        self.paragraph("references/verification.md", "reflink", "not an offsite/independent backup")

    def test_unknown_phase_and_new_writes_require_consistency_preserving_recovery(self):
        self.paragraph("references/verification.md", "new database writes", "Preserve original and current state", "consistency-preserving recovery plan")
        self.paragraph("references/verification.md", "validator bug", "do not remove identity/integrity gates", "not blind reexecution")
        self.paragraph("references/verification.md", "Do not claim a reboot rehearsal", "unit syntax check")
        self.paragraph("references/cutover.md", "No runner script is included", "unreviewed helpers")
        self.paragraph("SKILL.md", "reflink", "not an independent disk-loss backup")


class ProcedureReferenceGuardTest(unittest.TestCase):
    """Mutate disposable copies to ensure positive closure checks fail closed."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name)
        self.root = self.parent / "relocated-procedure"
        shutil.copytree(SKILLS / "state-change-monitoring", self.root)

    def test_missing_reference_is_rejected_after_relocation(self):
        (self.root / "references" / "cloud-usage.md").unlink()
        with self.assertRaisesRegex(AssertionError, "Missing local reference"):
            assert_reference_closure(self.root, package_files(self.root))

    def test_existing_external_reference_cannot_escape_package(self):
        (self.parent / "outside.md").write_text("Not distributed with the package.\n", encoding="utf-8")
        files = package_files(self.root)
        for target in ("../outside.md", "%2e%2e/outside.md"):
            with self.subTest(target=target):
                changed = dict(files)
                changed["SKILL.md"] += f"\n[external local dependency]({target})\n"
                with self.assertRaisesRegex(AssertionError, "Escaping reference"):
                    assert_reference_closure(self.root, changed)

    def test_support_file_requires_literal_entrypoint_reference(self):
        files = package_files(self.root)
        files["SKILL.md"] = files["SKILL.md"].replace("`references/cloud-usage.md`", "cloud usage")
        with self.assertRaisesRegex(AssertionError, "Unreferenced support file"):
            assert_reference_closure(self.root, files)

    def test_procedure_cannot_silently_gain_an_executable_helper(self):
        (self.root / "untested.py").write_text("raise RuntimeError('must never run')\n", encoding="utf-8")
        with self.assertRaisesRegex(AssertionError, "prose-only"):
            package_files(self.root)

    def test_symlink_cannot_supply_a_missing_dependency(self):
        target = self.parent / "outside.md"
        target.write_text("Not a portable dependency.\n", encoding="utf-8")
        link = self.root / "references" / "borrowed.md"
        try:
            link.symlink_to(target)
        except (NotImplementedError, OSError) as error:
            self.skipTest(f"Symlinks unavailable on this test platform: {error}")
        with self.assertRaisesRegex(AssertionError, "Symlink in procedure package"):
            package_files(self.root)
