---
name: container-storage-migration
description: "Move Docker storage with explicit integrity gates."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Docker, Storage, Migration, SELinux, Recovery]
    related_skills: []
---

# Container Storage Migration

Plan and execute an explicitly authorized Docker storage relocation while preserving workload identity and data. This is a gated Linux operator procedure, not a one-command migration script. It does not authorize formatting, pruning or changing storage drivers.

## When to Use

- Docker images/layers/volumes fill a system disk.
- Relocate engine storage to an existing attached local filesystem.
- Recover a move with empty-looking state, mount-order or SELinux failures.

Do not apply the classic-root recipe to a different image store without a separate plan.

## Prerequisites

- Exact host, source, destination UUID, outage window and cleanup authorization.
- Existing approved operator transport with strict host-key verification.
- Protected configuration/data backup and a rollback/consistency plan.
- Read [storage topology and cutover](references/cutover.md) (`references/cutover.md`) and [verification and recovery](references/verification.md) (`references/verification.md`) before any write.

## Procedure

1. **Discover live topology.** Through `terminal`, inspect hostname, mounts, source/destination realpaths, filesystem capacity, Docker root/driver/store, containerd root, live-restore, service/socket activation and SELinux. Do not format a usable destination. Done when physical backing and actual storage mode are proven.
2. **Capture exact inventory.** Save container/image IDs, volume names, normalized mount mappings, running set, health/restart policy and representative route responses. Keep secrets out of evidence. Test serialization round trips before trusting a persisted validator. Done when counts and identity-level comparison both work.
3. **Agree the mount plan.** Choose supported data-root configuration or a compatible bind mount; preserve driver and application host binds. Require the underlying data disk before the bind and Docker; fail closed on missing mount. Done when persistent dependency/rollback design is reviewed.
4. **Preflight the execution context.** Check remote interpreter/tool versions, permissions, xattrs and SELinux domain using harmless scoped probes. An SSH disconnect must not destroy the phase journal or leave outcome unknowable. Do not weaken global policy. Done when the approved runner and observer distinguish queued, running, failed and completed.
5. **Stage without claiming consistency.** Pre-copy into a dedicated operation-owned directory with ownership, hardlinks, ACLs, xattrs, sparse files and filesystem boundaries preserved. A live pre-copy is not a consistent database backup. Done when destination identity and available rollback space are rechecked.
6. **Quiesce and cut over once.** Save the exact running IDs; gracefully stop them, engine and activation socket. Account for live-restore/other runtimes and verify no source consumers or child mounts remain. Final-sync only into the proven owned destination; retain a quiescent rollback copy before writes resume. Done when logical root resolves to the intended physical filesystem and source remains intact.
7. **Restore the original running set.** Start engine and explicitly start previously-running workloads, including restart=no and deliberately stopped unless-stopped cases. Poll prior health and application baselines. Done when exact identities/mappings match and deviations are classified.
8. **Prove integrity before cleanup.** Compare two frozen cutover copies, not active databases against old copies. Validate persistent mounts, units and SELinux labeling. A reflink is useful rollback state, not an independent disk-loss backup. Done when successful comparison reports no differences and the proof still applies.
9. **Delete only if separately included.** Recheck the obsolete original's exact non-symlink path, filesystem, absence of mounts/children and approved ownership. Preserve rollback unless its removal was authorized. Done when measured space is reclaimed and service baselines still pass.

## Pitfalls

- Docker data-root does not necessarily move containerd images/snapshots.
- Switching storage backend can hide existing images; do not confuse this with data deletion or use it as a migration shortcut.
- `nofail` permits host boot, not safe engine fallback onto an empty root-disk directory.
- Preserve SELinux labels/MCS categories; blanket recursive relabeling can damage volume access.
- A zero exit from a dry-run comparison is not equality when differences were printed.
- After new writes, blindly switching to an older snapshot can lose data. Preserve both states and plan consistent recovery.
- Cleanup is destructive; a validator defect is not permission to bypass its gate.

## Verification

- [ ] Live source, destination UUID, storage mode and ownership checked at each critical boundary.
- [ ] Exact IDs, mounts, volumes, running set and health reconciled, not merely counts.
- [ ] Frozen-copy integrity passed; live writes excluded from that comparison.
- [ ] Missing-disk startup fails closed; source/bind/engine ordering validated.
- [ ] SELinux remains enforcing where applicable; no broad policy downgrade.
- [ ] Source/rollback retention and after-write recovery limits documented.
- [ ] Real checks and measured reclaimed space reported; no unperformed reboot/restore test claimed.
