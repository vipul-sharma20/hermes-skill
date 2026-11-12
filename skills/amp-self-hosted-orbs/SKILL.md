---
name: amp-self-hosted-orbs
description: "Run single-host Amp orbs with bounded Docker resources."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Amp, Orbs, Docker, Self-Hosting, Resource-Limits]
    related_skills: []
---

# Self-Hosted Amp Orbs

Operate one Amp orb provider on an authorized Linux Docker host. This package includes a standard-library Python dispatcher, not a fleet installer, a VM boundary, or a secure multi-tenant sandbox. Its lifecycle design derives from a working Docker-backed implementation, but **this portable variant has offline tests only**; historical private deployment results are not live verification of this package.

## When to Use

- An owner wants Amp tool execution and paused orb disks on their infrastructure.
- A single host needs repeatable spawn, pause, delete and host-local project snapshots.
- Existing providers need ownership, resource, lifecycle and credential handling reviewed.

Don't use for hostile/untrusted tenants, Kubernetes, remote/rootless Docker, memory snapshots, fleet migration, GPU access, or shared provider state across hosts. The bundled dispatcher supports one fixed resource size and refuses nonempty `ORB_TYPE`; do not configure advertised orb types for it.

## Prerequisites

- Owner approval for the **specific host**, provider scope, service changes, resource ceilings and canary project. Discover before changing; preserve unrelated containers/services.
- Linux, Python 3.9+, an authenticated Amp CLI, rootful Docker with cgroup memory enforcement and the local socket at `/var/run/docker.sock`. The Python dispatcher uses `fcntl`; macOS Docker Desktop and Windows are outside this recipe.
- A dedicated operator-controlled script/config location and private state directory. Root or Docker-group access is **host-admin** authority, not a restricted deployment role. Keep the dispatcher, its trusted `PATH`, configuration and all state-path ancestors unwritable by orb users.
- A locally cached, operator-reviewed Amp image for the host architecture. No runtime pull occurs. Stock images use default user `user`, no declared volumes, and working passwordless sudo **inside the container**. Container root is not permission to administer the host, but a container escape remains possible.
- Provider token supplied privately as `AMP_ORB_PROVIDER_TOKEN`, preferably through a root-owned mode-0600 systemd `EnvironmentFile`. Never place token values in argv, source control, chat, shell tracing or captured tool output.

Read `references/operations.md` for the service recipe, configuration bounds, local-image preparation, timeout reconciliation and canary checklist. The resource template is `templates/resources.example.json`; the executable lifecycle program is `scripts/dispatch.py`. No other deployment files or private configuration are required.

## Procedure

### 1. Discover and approve the boundary

Use `terminal` for read-only discovery and `read_file` for an existing private runbook. Consult the current [official self-hosted orb docs](https://ampcode.com/docs/orbs/self-hosted) with `web_extract` before configuring an account; use the installed CLI's help rather than assuming newer optional flags exist:

```python
terminal(command='amp --version', timeout=30)
terminal(command='amp orb provider --help', timeout=30)
terminal(command='python3 --version', timeout=30)
terminal(command='docker --host unix:///var/run/docker.sock info --format "{{json .}}"', timeout=30)
terminal(command='docker --host unix:///var/run/docker.sock ps -a --no-trunc', timeout=30)
```

Do not print a running provider's environment or broad process command lines. Record the initial container IDs/state privately. Confirm Docker reports `MemoryLimit=true`; missing enforcement is a hard stop, not a reason to remove limits or reboot without approval. Check host capacity with headroom for the OS and other workloads. Done when scope, rollback, architecture and a protected runtime location are explicit.

### 2. Prepare bounded resources and a trusted image

Use `read_file` on `templates/resources.example.json`, then `write_file` to create the **nonsecret** deployment copy in the approved location. Set a unique stable provider slug, matching `linux/amd64` or `linux/arm64`, integer CPU/MiB ceilings and a positive concurrent-orb ceiling. They are **ceilings, not reservations**; idle orbs do not reserve those CPUs/RAM, and the host may still be overcommitted.

Keep state outside the skill/source tree. Set absolute `AMP_ORB_RESOURCES` and `AMP_ORB_STATE_DIR` in the provider's service environment. All invocations for this provider on this Docker daemon must share exactly that state directory and label identity; changing either can bypass admission accounting. Do not reuse this provider slug for another provider on the same daemon.

Prepare/pin the official image as described in `references/operations.md`. ARM64 needs **both** the ARM64 image and `linux/arm64`; Amp otherwise defaults to x64. Changing `ORB_IMAGE` affects new orbs only, not existing disks/snapshots. Done when a local image's platform, default user and absent volumes are verified and the resource copy is reviewed.

### 3. Register exactly one provider and supervise it

In signed-in Amp **Settings → Orbs**, choose the intended workspace **Add Orb Provider**, or personal **Add Provider** for personal scope. Give it a distinguishable name and capture its one-time token directly into protected host configuration using a private secret-management path, never a captured `terminal` command or `write_file` argument containing the secret. Preserve other providers and workspace defaults unless changing them was approved.

Run **exactly one** `amp orb provider` per token. Never duplicate the token across a fleet, launch a second foreground instance beside a service, or use multiple-provider overrides with host-local state. Install an executable copy of `scripts/dispatch.py`; use its absolute path as the provider's sole positional argument. Use `references/operations.md` to adapt an owner-approved service, not to blindly overwrite an existing unit. Its startup environment must contain `AMP_ORB_PROVIDER_TOKEN`, `AMP_ORB_RESOURCES`, `AMP_ORB_STATE_DIR` and the chosen `ORB_IMAGE`.

Keep **Public Portals off** (the default). A public portal is an anonymous tunnel to a service inside a network-reachable orb. Signed-in thread access is not authorization to expose unrelated internal services. Done when the saved provider scope is checked, the single service is connected and private logs contain no copied tokens.

### 4. Understand the dispatch contract before sending jobs

Amp invokes the program with no arguments and jobs in environment variables:

| Variable | Handling |
|---|---|
| `ORB_OPERATION` | Only `spawn`, `pause`, `delete`. |
| `ORB_ID` | Stable `amp-…` container name; validated before any Docker action. |
| `ORB_IMAGE` | Required on spawn; locally cached image fallback. |
| `ORB_SNAPSHOT_ID` | Optional image tag to load on spawn/save on pause; validated before mutations. Existing unowned/foreign image tags are refused, never overwritten. |
| `ORB_TOKEN` | Required on spawn; short-lived bootstrap credential passed by exec environment name only, never argv or container creation config. |
| `AMP_URL` | Optional nondefault Amp endpoint passed by exec environment name. |
| `ORB_TYPE` | Nonempty value refused: single-size provider only. |

Spawn creates/resumes the same labelled container, then starts detached `amp orb bootstrap` as the image's default user. A running orb can reconnect even at capacity; a stopped orb needs a free admission slot. Every spawn checks memory support and actual container limits/isolation before bootstrap; resource edits do not silently resize old containers. Do not relabel/import existing containers to bypass this check.

Pause stops processes and keeps the writable disk; a requested project snapshot becomes a labelled local Docker image. Docker preserves **disk, not memory**: terminal sessions, desktop apps and running services do not survive the pause. Snapshots work only on this host and may contain source and credentials written inside the orb. Delete removes only the exact owned container/disk, not shared project snapshots. **Archiving** a thread sends pause, not delete; use thread deletion only for deliberately disposable work. Done when the operator accepts retention and recovery semantics.

### 5. Prove one private canary, then stop it

Run offline tests first (Verification). Only with explicit live approval, select this provider in a new private disposable-project thread. Confirm setup/bootstrap, execute a harmless file write/read plus architecture check, archive, verify the exact owned container is stopped, resume and read the file back. Separately verify a project snapshot and deliberate canary deletion using the checklist in `references/operations.md`. Do not use a real project/thread as a destructive test.

Compare unrelated container identities/state against the baseline. Do not infer connectivity from a successful detached Docker exec; check actual thread setup/tool results. Report model/account/billing blockers without buying credits or upgrading a plan. Done when canary evidence is real, scoped cleanup is complete and unrelated workloads are unchanged—or a precise blocker is recorded.

## Pitfalls

- **Self-hosting is not local inference.** Amp's agent loop and model inference run on Amp servers. File contents read by tools, command outputs, diffs, screenshots and attachments are sent to Amp and stored with the thread. Review that data boundary before using private code.
- Only **outbound HTTPS** is needed for provider jobs; orb bootstrap/tools also use HTTPS/WSS. Portals, Terminal and Desktop use Amp Tunnel, not a published Docker port. Git, CLI update and other downloads need their own outbound destinations; see the official allowlist.
- No inbound port publishing, host mounts, Docker socket mounts, host network/PID namespace or privileged mode is added. **This is not egress isolation:** default Docker networking may reach the host, LAN, cloud metadata and credentials endpoints. Restrict egress/metadata access through separately reviewed host/cloud policy before sensitive use; this package changes no firewall.
- No per-orb disk quota, total stopped-disk/image cap, backup system or automatic snapshot garbage collection is included. Avoid broad prune commands; review exact provider-owned resources and snapshot references before deleting anything.
- The script uses a **270-second** total lifecycle budget, including lock waits, with at most 60 seconds per Docker CLI call and a 20-second stop grace. Images must be pre-pulled. Docker daemon operations can continue after a CLI timeout: reconcile before retry, never infer rollback or automatically delete uncertain work.
- The token still exists in bootstrap process memory/environment and is visible to sufficiently privileged host/container users. Logs and snapshots may contain credentials generated by tools; label scoping is not protection from a host admin.
- Resource mismatches refuse spawn without deleting the old disk. Restore the prior configuration or plan an approved backup/migration/recreation; do not force-start it out of band. Admission is serialized only among cooperative callers sharing the same lock, not arbitrary host administrators.
- Self-hosted orb fees and model access are **plan-dependent**; check current pricing and infrastructure/storage/egress costs. No zero-cost or subscription-coverage promise is made.

## Verification

From the repository root, run the real script against fake Docker, without root/network/Amp:

```python
terminal(
    command="PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p 'test_amp_self_hosted_orbs*.py' -v",
    timeout=120,
)
```

The tests exercise memory refusal, labelled ownership, resource/argv construction, no-sudo-breaking flags, input validation, idempotent pause/delete, snapshot collision/reuse, stale container limits, concurrent admission, private lock paths, deadlines and redacted Docker errors. Packaging tests validate the resource template through the real parser and check linked files/examples. They do **not** prove live Docker cgroups, Amp bootstrap, account permissions, network policy, image contents or billing. Report offline and live results separately; no live deployment is performed merely by loading this skill.
