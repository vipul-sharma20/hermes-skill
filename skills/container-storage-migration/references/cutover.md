# Storage topology and cutover

## Discover before choosing a recipe

Read current https://docs.docker.com/engine/storage/containerd/ and https://docs.docker.com/engine/storage/drivers/overlayfs-driver/ . Classic overlay2 and the containerd image store have different roots; Docker data-root alone may not move containerd images/snapshots. Backend changes may hide old images/containers. Do not combine relocation with backend/engine upgrade.

Use `terminal` through the authorized target transport for live `docker info`, `lsblk`, `findmnt`, service/socket definition and SELinux state; project only necessary fields. Measure filesystem-bounded usage without traversing running overlay mounts. Inspect actual root/configuration rather than assuming conventional paths. Check source mount/symlink status, destination UUID/type/free space and existing files; never format or overwrite unexplained data. XFS classic overlay2 requires compatible d_type/ftype support; confirm with installed tooling.

## Mount and execution design

A compatible bind mount can retain the logical engine path while moving physical storage. Merge approved fstab/drop-ins, never replace unrelated configuration. Derive mount unit names with systemd-escape for actual paths. Dependencies must order data disk -> bind -> engine; engine precondition must refuse an empty fallback directory. nofail only permits the host to remain administrable. Validate fstab and actual generated units with the target systemd version; distinguish pre-existing warnings from new failures.

Test remote tools/interpreter and the exact service execution domain before downtime. SELinux SSH/admin and transient-service domains may differ. Use harmless scoped context/xattr/dry-run probes; keep enforcing and require explicit authorization for any job-scoped context exception. Do not prescribe a universal unconfined context or recursive restorecon over layers/volumes.

Choose an owner-approved durable runner with private phase/status files and bounded observation. A long oneshot can remain activating; queued/ExecMainStatus=0 is not completion. Verify actual timeout semantics and cleanup/interruption behavior. No runner script is included; do not execute unreviewed helpers.

## Gated sequence

1. Prove target identity and owned destination; capture exact source/running inventory and baseline faults.
2. Online pre-copy preserving numeric ownership, hardlinks, ACLs, xattrs, sparse files and filesystem boundaries. Treat active-source changes as staging, not consistency proof.
3. Revalidate paths/disk/space and record the exact running IDs immediately before outage. Gracefully stop them, engine and activation socket; account for live-restore/other consumers, open source users and child mounts.
4. Final offline sync. Stale-file deletion is allowed only in the exact dedicated destination/direction already approved; never use a generic recursive deletion command against a guessed path.
5. Keep source unchanged as OLD and create a quiescent ROLLBACK from final DEST before activation. A reflink must genuinely succeed on the same supported filesystem; otherwise budget a real copy/snapshot.
6. Preserve labels/MCS and reviewed persistent equivalences, switch logical mount/configuration and validate UUID/mount ordering. Compare device/inode identities for a bind, not path strings alone.
7. Start engine and the exact prior-running set explicitly. A deliberate stop can suppress normal restart-policy behavior. Restore dependencies before applications where necessary.
8. Verify services and frozen-copy integrity using [integrity and recovery gates](verification.md) before any source reclamation.

Retain a recoverable configuration copy. Do not restart the whole workflow blindly after an unknown phase or auto-delete source on a merely successful copy exit.
