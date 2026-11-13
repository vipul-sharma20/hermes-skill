---
name: self-hosted-operations
description: "Audit and operate self-hosted Linux services safely."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Self-Hosting, Diagnostics, Coolify, Prometheus, Safety]
    related_skills: []
---

# Self-hosted Operations

Diagnose Linux hosts and containerized services through existing monitoring and management paths. This is an operator procedure, not an unattended fleet installer; no helper scripts or private deployment configuration are included.

## When to Use

- Audit capacity, backup evidence, service health or an outage.
- Attribute CPU, memory, disk, thermal or external-browser pressure.
- Perform an explicitly requested lifecycle change, restoration or staged upgrade.
- Diagnose slow uploads across client, ingress, application and storage boundaries.

A health-check request is not permission to install tools, retrieve unrelated secrets, restart services, prune data or edit a private knowledge base.

## Prerequisites

- Authorized target set, existing operator transport and trusted host keys.
- A current inventory/runbook, management identifiers and monitoring labels, if available.
- Protected storage for minimal evidence and rollback material. Credentials stay in the approved secret source; never in skills, command arguments or captured output.
- Consult the installed product's official documentation with `web_extract`; inspect exact-version source when behavior is ambiguous. Missing API support is not permission for a privileged workaround.

## Procedure

1. **Resolve identity and scope.** Use `read_file`/`search_files` on the narrow runbook and `terminal` for live discovery. Verify the target hostname, execution namespace, host role and allowed change. A reachable bastion or agent container is not necessarily the named host. Done when every target has an exact identity and unrelated resources are excluded.
2. **Capture a safe baseline.** Record time, uptime/boot ID, mounts, critical services and container IDs/state; project only required API fields. Use `comm` in broad process inventories, not full command lines. Done when evidence is attributable, timestamped and contains no credentials.
3. **Select the source that measures the claim.** Control-plane registration, SSH reachability, application behavior and fresh exporter telemetry answer different questions. Prefer an existing read-only API for observation; use operator SSH for process-level gaps. Done when source and freshness match the requested noun.
4. **Measure and interpret.** Compare at least two interval samples or a bounded history window; calculate units/rates in code. Use available memory, distinguish CPU execution from I/O wait, and separate host, container and child-process totals. Done when the strongest supported cause and remaining blind spots are explicit.
5. **Change only when authorized.** Re-read exact IDs/configuration, save rollback material and use the owning control plane. Explain failure-domain impact first. An approval denial/timeout is a stop, not an invitation to change transport. Done when only the authorized operation was submitted once.
6. **Reconcile asynchronous outcomes.** Queued/accepted is not completed. Poll with per-request and total deadlines; inspect child state when aggregate state lags. A timeout does not imply rollback; inspect before retrying. Done when actual terminal state or a precise unresolved outcome is recorded.
7. **Verify independently.** Compare critical applications, mounts and unrelated container identities against baseline. Prove a host reboot with a different host boot ID, not a container start time. Done when the original symptom's probe passes or the remaining failure is stated without overclaiming.
8. **Report and clean up.** Remove only operation-owned temporary credentials/artifacts; preserve incident evidence and stopped disks. Report live versus historical facts, exact changed scope, real checks and untested coverage. No publication or note edits are implied.

## Reference Selection

Load the matching relative reference with `read_file` (or the installed skill's reference loader) before detailed work:

- [Metrics and historical timestamps](references/metrics.md) (`references/metrics.md`): Grafana UID proxy, Linux memory, container identity and raw samples.
- [Linux and browser diagnostics](references/diagnostics.md) (`references/diagnostics.md`): interval semantics, GPU/thermal gaps, CDP accounting and safe cleanup.
- [Management, lifecycle and backup audits](references/control-plane.md) (`references/control-plane.md`): credentials, scoped access, preserve-in-place stops, backup evidence and staged upgrades.
- [Outages and restoration](references/recovery.md) (`references/recovery.md`): multiple vantage points, consistent data backups, migrations and reconnect checks.
- [Upload boundary diagnosis](references/uploads.md) (`references/uploads.md`): size versus duration, protocol and client deadlines.
- [Temporary immutable-runtime overlays](references/runtime-overlays.md) (`references/runtime-overlays.md`): exact-version imports, auth/resource discovery, boundary probes and durability.

## Pitfalls

- A wiki specification is not utilization; exporter `up` is not complete application health.
- A running container without a healthcheck is not automatically healthy or unhealthy.
- A high-ranked process may consume little absolute capacity; high RSS alone is not a leak.
- A management Stop action may remove containers. Check implementation when writable-layer retention matters.
- A Docker socket mounted `:ro` still gives Docker API authority; it is not a read-only canary boundary.
- Do not weaken TLS/SSH verification, copy operator keys into workers, or use blanket prune/relabel commands.
- Resource limits are ceilings, not idle reservations or guarantees of headroom. Shared workloads retain priority.

## Verification

- [ ] All targets reconciled; missing/unreachable ones remain unknown, not verified healthy/stopped.
- [ ] Samples identify source time, label/namespace, units and freshness.
- [ ] Process versus container attribution and observation versus hypothesis are separate.
- [ ] Required mutation approval, rollback and independent readback exist.
- [ ] Unrelated services and retained data match baseline.
- [ ] Temporary credentials removed; no secret or private topology in reusable artifacts.
- [ ] Static review, offline tests and live behavior are reported separately.
