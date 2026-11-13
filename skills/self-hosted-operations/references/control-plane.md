# Management, preservation and backup evidence

## Safe access and API projections

Resolve current base URL/version and exact resource IDs before calls. Use `terminal` with an existing approved client; privately load credentials, verify TLS and allowlist fields before printing. Never dump raw settings/Compose/environment/key records. A read:sensitive response may contain nested tokens unrelated to the task.

For Coolify consult https://coolify.io/docs/api/overview and match the installed version. Common discovery surfaces are `/api/v1/version`, `/servers`, individual server records, `/resources`, `/projects` and individual services. Server detail can include relationships absent from list responses. Reachability may be nested under settings; retained validation logs and collected metadata may be stale.

Use existing operator SSH. Exporting a management key is a separate sensitive act: only when authorized and necessary, match exact server key ID to key UUID, treating zero as a valid ID. Use a private temporary directory/key with permissions set at creation, strict trusted known-host verification, batch mode and bounded timeouts. Resolve bastion/target users separately; no key/agent forwarding into a worker. Clean up on normal/error exits and reconcile operation-owned remnants after interruption. Never invent an arbitrary remote-execute API.

## Lifecycle is version-sensitive

Inspect documented method/body/encoding and actual implementation before mutation. A start/restart/deploy/stop action can differ in cleanup or container preservation. For retain-in-place shutdown verify that the chosen operation keeps exact IDs, writable layers, mounts and volumes. Some Coolify Stop implementations remove containers; a scoped operator Docker stop can be narrower only when that specific path is authorized. Do not use down/rm/prune as synonyms for stop.

Inventory every component of the named deployment, including workers, apps and tunnels; exclude shared ingress/personal agents. A user pausing work is not necessarily asking to stop all runtime components. Recheck exact IDs before action, submit once, then independently inspect state and untouched neighbors. Unreachable targets remain unverified. Restart policies/controller reconciliation can bring work back; do not change unrelated policy or create a retry/restart schedule silently.

For app readiness test health and data-bearing authentication endpoints separately. A public version page can be intentional; it does not prove data access is protected. Never transmit credentials over public HTTP or use an untrusted certificate just because a generated hostname exists. Persistent volume mapping, backup coverage and pin policy need explicit checks.

## Backup audit

Inventory workload databases, control-plane database and persistent files/volumes separately. A project database list may omit platform system state. A source default is not the configured schedule. A schedule is not a successful artifact. An artifact is not a restore test.

Use current read-only backup/schedule/execution endpoints where supported. For storage evidence use maintained authorized clients and metadata listing only: paginate, compare several consecutive timestamps, sizes and destination recency without downloading sensitive dumps. Copy/migration modification times can mislead; retain provenance. Distinguish configured retention from observed object count, and cron/server time from timezone conversions.

Report schedule/observed cadence, latest success, destination and gaps. No triggering backup, restore, schedule/retention edit or private-note update is implied. If a system setting lacks a supported API, stop rather than tunneling through scheduled tasks, sockets or exported keys.

## Staged proxy upgrades

Inventory all hosts including unreachable/no-proxy cases. Verify running binary version in addition to configured tag and cached control-plane metadata. Capture representative routes, SNI/auth response semantics, logs and readiness first.

With approval, canary materially different architecture/configuration using copies of required state and an appropriately isolated runtime. A `:ro` Docker socket is still host-admin authority; no unreviewed helper is included. Do not mount live ACME/dynamic state or send secrets to an unreviewed image. A network-none syntax/startup canary cannot prove public routing or ACME behavior.

Save through the owning platform, validate exact one-change diff, restart once, poll actual process/version/health, then test routes before next failure domain. Control-plane ingress last. Re-read update metadata; a patch notice can become a branch notice. Roll back through supported configuration paths and stop the rollout on a regression. No certificate bypass is accepted as successful TLS verification.
