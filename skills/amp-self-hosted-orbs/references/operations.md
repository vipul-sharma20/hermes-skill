# Amp orb operations and verification

This is an operator-adapted Linux recipe, not an unattended installer. Discover existing files/services before changing them; obtain approval for the exact host, paths, image pull, provider registration and private canary. Never copy a personal Hermes/Amp home, Git credentials or cloud credentials into an orb.

## Configuration contract

Read `templates/resources.example.json` with `read_file`, then write an approved deployment copy with `write_file`. The parser accepts exactly these keys; extra keys are refused:

| Key | Accepted value |
|---|---|
| `provider` | Unique lowercase slug, beginning with a letter, at most 63 characters. Stable for the lifetime of this provider. |
| `platform` | `linux/amd64` or `linux/arm64`. |
| `cpus` | Integer 1–128; booleans/fractions are not accepted. |
| `memory_mib` | Integer 1024–1048576. Budget OS/container/browser headroom, not just the application's heap. |
| `max_running_orbs` | Integer 1–64. This portable variant deliberately does not support `0`/unlimited admission. |

CPU/RAM settings are ceilings, not reservations. The dispatcher sets equal memory/swap limits, a 1024-PID limit, 1 GiB shared-memory ceiling, drops `NET_RAW`, and rotates container logs. It does not pin cores or reserve idle RAM. Paused disks and snapshots still occupy storage; there is no disk quota or automatic garbage collection.

The process environment must provide absolute `AMP_ORB_RESOURCES` and `AMP_ORB_STATE_DIR` paths. The state directory must be owned by the dispatcher user, mode 0700, and not a symlink. Its ancestors, the executable, config and `PATH` must be administrator-controlled. Exactly one provider/token and all its local lifecycle calls share that state directory. Do not configure orb types: nonempty `ORB_TYPE` is refused.

## Prepare the image before starting the provider

Use the current official image matching the host:

- x64: `us-central1-docker.pkg.dev/amp-prod-0/amp-orb/amp-orb:latest`
- ARM64: `us-central1-docker.pkg.dev/amp-prod-0/amp-orb/amp-orb-arm64:latest`

Discover and set `AMP_ORB_PLATFORM` and `AMP_ORB_IMAGE_REF` in the operator environment; these are recipe placeholders, not additional Amp settings. Pull only after approval, outside the lifecycle budget:

```python
terminal(
    command='docker --host unix:///var/run/docker.sock pull --platform "${AMP_ORB_PLATFORM}" "${AMP_ORB_IMAGE_REF}"',
    timeout=600,
)
terminal(
    command='docker --host unix:///var/run/docker.sock image inspect --format "{{.Os}}/{{.Architecture}} user={{.Config.User}} volumes={{json .Config.Volumes}} digests={{json .RepoDigests}}" "${AMP_ORB_IMAGE_REF}"',
    timeout=30,
)
```

Review the actual public image digest, platform, default user and declared volumes, then set provider `ORB_IMAGE` to the verified repository-qualified digest. Do not invent a digest or silently refresh it on every run. The image must be cached on the same local Docker daemon; `--pull=never` prevents an accidental lifecycle download. A missing image is a refusal, not permission to use another image.

Stock Amp images use `user` with working passwordless sudo **inside the container**. The dispatcher also accepts `user:user`, but refuses root-default images, mismatched platforms and declared volumes. Do not add `no-new-privileges` to the orb: it breaks the documented stock-image sudo requirement. This is not VM-grade isolation or a secure multi-tenant sandbox. Root inside a container is not permission to mount the host; a runtime/kernel escape remains possible.

Image updates affect new orbs only. Existing disks and host-local project snapshots keep their original contents. Test a new digest with a disposable project before changing a production provider.

## Install an owner-approved service

The following paths are conventional example deployment locations, not facts about the operator's machine. Inspect for existing services/files and adapt the recipe rather than overwriting another deployment. Determine the actual absolute Amp/Python executable locations. `AMP_ORB_SKILL_DIR` below means the discovered installed skill directory.

Create approved directories and an executable copy through `terminal`:

```python
terminal(command='install -d -m 0755 /opt/amp-orbs && install -d -m 0700 /etc/amp-orbs /var/lib/amp-orbs', timeout=30)
terminal(command='install -m 0755 "${AMP_ORB_SKILL_DIR}/scripts/dispatch.py" /opt/amp-orbs/dispatch.py', timeout=30)
```

Use `write_file` for the reviewed nonsecret resource copy at `/etc/amp-orbs/resources.json`. Through a private secret-management path, place only the provider credential in the root-owned mode-0600 `/etc/amp-orbs/provider.env`, under the name `AMP_ORB_PROVIDER_TOKEN`. Do not put the value in a captured terminal command, `write_file` argument, source repository, log or chat. Amp displays it once during authorized provider registration; never regenerate an existing provider token merely to inspect it.

Use `write_file` to create a reviewed service definition such as this at `/etc/systemd/system/amp-orb-provider.service`. Replace the example Amp executable path and image placeholder before enabling it:

```ini
[Unit]
Description=Single-host Amp orb provider
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
Type=simple
User=root
UMask=0077
StateDirectory=amp-orbs
StateDirectoryMode=0700
WorkingDirectory=/var/lib/amp-orbs
Environment=HOME=/var/lib/amp-orbs
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=AMP_ORB_RESOURCES=/etc/amp-orbs/resources.json
Environment=AMP_ORB_STATE_DIR=/var/lib/amp-orbs
Environment=ORB_IMAGE=REPLACE_WITH_VERIFIED_IMAGE_DIGEST
EnvironmentFile=/etc/amp-orbs/provider.env
ExecStart=/usr/local/bin/amp orb provider /opt/amp-orbs/dispatch.py
Restart=on-failure
RestartSec=5
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

This root provider controls the Docker daemon and therefore has host-admin authority. The orbs do **not** receive its socket, host mounts or provider token. Do not present Docker-group membership as a restricted security role. Avoid broad inherited environment files or copying account/profile authentication into the service.

Validate the actual adapted unit with `terminal(command='systemd-analyze verify /etc/systemd/system/amp-orb-provider.service', timeout=30)`. Only after approval, apply that unit with `terminal(command='systemctl daemon-reload && systemctl enable --now amp-orb-provider.service', timeout=60)`. Do not restart Docker, other providers or the personal Hermes gateway.

For nonsecret status, use `terminal(command='systemctl show amp-orb-provider.service -p ActiveState -p SubState -p MainPID -p NRestarts', timeout=30)`. Inspect sensitive provider logs privately and report a redacted diagnosis; never dump environment settings or broad journals into a group conversation. Stopping the provider stops job receipt, not the existing orb containers: never infer that its CPU/RAM or disks have been reclaimed.

## Network and data boundary

The provider needs outbound HTTPS; orb tools/bootstrap, portals, Terminal and Desktop also use HTTPS/WSS and Amp Tunnel. No published Docker port is needed. Consult the current official destination allowlist for Git, CLI updates and downloads. Preserve unrelated firewall/proxy rules.

Default Docker bridge networking is **not egress isolation**. Orbs can potentially reach the host, LAN, cloud metadata and credential endpoints. Keep Public Portals off and use a separately approved host/cloud egress and metadata policy for sensitive work. This recipe does not modify firewall rules.

Self-hosting does not move the agent loop/model inference into the host. File contents read by tools, command outputs, diffs, screenshots and attachments go to Amp and are stored with the thread. Snapshots may also contain secrets written by tools; keep them private. Pricing and model/subscription coverage are plan-dependent, and infrastructure, storage and egress costs remain the operator's responsibility.

## Private canary checklist

Offline tests are not evidence of live Docker cgroups, Amp bootstrap, account access or successful billing/model inference. Only after separate live approval:

1. Record unrelated container IDs and running states privately. Use a disposable nonproduction project, a covered model mode, a private thread and the specific newly registered provider. Read back actual visibility and provider selection before sending private content.
2. Verify real thread setup and a tool command that writes/reads a harmless canary file and checks architecture. A detached `docker exec` success alone does not prove bootstrap connected.
3. Read back only the canary's required container fields: ownership labels, running state, CPU/memory/swap/PID ceilings, default user, absence of mounts/published ports/privileged mode. Do not print its complete environment or filesystem. Verify effective cgroup behavior under an approved bounded probe, not just a stored config value.
4. Archive the canary thread; archiving means **pause**, not delete. Confirm its exact labelled container stopped and the disk remains. Resume the same thread, verify the marker survives, and accept that terminal sessions/desktop processes do not: Docker saves disk, not memory.
5. Trigger the project's normal snapshot preparation. Verify the requested local snapshot has this provider's ownership and snapshot-kind labels; use a fresh disposable thread to prove reuse without setup. Do not manually overwrite an existing image tag to force the result.
6. Deliberately delete only disposable canary threads, verify their exact owned containers/disks are removed, and preserve snapshots still referenced by other work. Never substitute a broad Docker prune for scoped cleanup.
7. Compare unrelated container identities/state to baseline. Report actual offline/live results separately, plus account/model blockers. Do not buy credits, upgrade plans or reboot a host to make a smoke test pass without approval.

## Timeout, capacity and recovery

All cooperating dispatcher calls share a private filesystem lock, with a 270-second total budget including lock waits and at most 60 seconds per Docker CLI call. A Docker daemon can still finish an operation after the client times out. Before retrying, inspect the exact owned container/snapshot and determine whether the operation completed; do not claim rollback or automatically delete uncertain work.

Resource edits do not resize old containers: spawn refuses a mismatch without deleting the disk. Restore the old resource configuration or plan a separately approved backup/migration/recreation. A positive admission cap counts running containers with this provider label; paused disks/snapshots do not count. Other host administrators and callers using a different lock can bypass admission, so this is coordination, not an adversarial host-level quota.

Keep unique per-host provider tokens and stable provider labels/state paths. Never run the same token on multiple independent hosts: the next lifecycle job can otherwise land on a host with no matching disk. Back up private provider state/disks under an owner-approved policy; do not publish deployment evidence, tokens, real workspace identifiers or machine-specific runbooks with this skill.
