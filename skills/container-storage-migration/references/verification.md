# Integrity, cleanup and recovery gates

## Identity comparison

Capture full container/image IDs, volume names and each mount type/source/destination. Normalize only representation/order, not values: JSON tuples become lists. Test persisted versus live inventories with a nonempty mount fixture; negative tests must still reject a different source path/image, missing ID or volume. Avoid raw environments in evidence.

Compare originally-running set and critical health/routes, including baseline redirects/denials. Running is not application-ready. Existing unhealthy checks are baseline faults, not silently repaired migration regressions. Check volume existence, owner/labels, engine root physical backing, mount dependency and missing-disk fail-closed configuration. Do not claim a reboot rehearsal from a unit syntax check.

## Integrity without active-write false positives

OLD is the quiescent source; ROLLBACK is the frozen final destination before applications resume. Compare those two for bytes and metadata after services restart, not the active DEST where legitimate new writes occur. Require a successful comparison and no reported differences; an exit-zero dry run alone is not equality. Retain proof with exact snapshot identity/hash/phase. Summary/statistics output must not be mistaken for file differences.

A reflink has distinct file identity and copy-on-write contents but shares a physical filesystem: not an offsite/independent backup. Retained extents can grow as live writes diverge. Do not establish or delete retention silently.

## Destructive source reclamation

All gates required:
- Explicit source-removal authorization and a current approved change window.
- Exact IDs/mounts/volumes, baseline health and representative applications recovered.
- Live logical root on intended data UUID, not OLD/ROLLBACK.
- OLD is the exact owned non-symlink/non-special path on the original filesystem, not mounted and without child mounts or active users.
- Frozen-copy proof still applies; source and rollback not altered since comparison.
- Rollback location and after-write recovery limits accepted.

Delete only the verified obsolete original, bounded by filesystem and ownership; never broad prune/glob. Recheck reclaimed bytes using a tool, actual mounts and application health. Keep rollback until its deletion is separately authorized.

## Recovery

Before activation, restore only this operation's changed config/mounts and exact prior-running set; refuse nonempty unexpected mountpoints. After activation new database writes make automatic switchback potentially destructive. Preserve original and current state, identify writes/affected bind mounts and choose a consistency-preserving recovery plan.

A validator bug can reject identical persisted data; fix its representation regression with tests, do not remove identity/integrity gates. An unknown/interrupted phase requires reconciliation, not blind reexecution. Report verified source/data identities, measured space, tests, services, retention and remaining faults without private topology.
