# Outage evidence and state-preserving restoration

## Outages

Define one deterministic red/green symptom probe and retain first-bad/last-good times. Compare external, management, same-LAN peer, outbound telemetry and console evidence. These paths have different failure domains; two views derived from the same broken collector are not independent.

Find last real samples using raw range vectors, not dashboard render time or evaluation timestamps. Compare peers across the same window and final CPU/PSI, memory/OOM, disk, temperature, power and physical-interface signals. Normal final metrics do not prove clean shutdown or exclude a sudden panic/power/sleep/interface event after samples stopped.

A FAILED neighbor entry is not power-off proof. Existing DHCP/known-MAC evidence can support address drift. Subnet sweeps, management validation and Wake-on-LAN can trigger activity: obtain the necessary scope; do not treat them as universally side-effect-free reads. Never restart a shared bastion/ingress just to probe another host. Exact cause can require prior-boot logs after separately approved recovery.

## Restore retained application state before replacing it

Match manager record, actual container and retained data; they can disagree after cleanup. Capture raw-versus-rendered configuration privately, version/digest, mount ownership, host listeners, account roles and existing connections.

Before a newer image can migrate schema, create a consistent supported DB backup and settings snapshot. For SQLite prefer its backup API; a live main-file copy is insufficient. A stopped offline copy must include applicable WAL/SHM and prove quiescence. Test local integrity/readability under the approved scope; this is not a full restore rehearsal.

Pin a current supported release using publisher evidence and actual architecture; do not use historical stable versions. Preserve identities, content, saved connections and credential-array correspondence. Some settings are stored in DB after initial environment defaults; inspect supported admin APIs instead of assuming env changes take effect. A retained companion omitted from raw Compose may reappear in manager-rendered output; recheck actual containers/ports after each full-stack action.

Compare IDs and canonical content across intended schema migrations, not just table counts. A move to a new table can look like loss; validate the explicit mapping and union without printing sensitive content. An unexpected count change is an investigation, never automatic acceptance or rollback.

## Reboot proof

Only after specific maintenance approval: capture hostname, boot ID, exact running IDs, mounts/failed units/application baselines and access dependency. Submit a graceful reboot once; perform bounded readiness in a separate call. A lost SSH connection is expected but not completion. Require changed host boot ID, correct identity, expected mounts, engine, critical services and baseline health. Do not issue another reboot while recovery is uncertain.

## Connection acceptance

Verify negative auth, saved backend from the frontend's actual network, real response/tool event, owner access and non-owner denial, authenticated frontend route and signed-in browser separately. Do not inject a session token to bypass a login wall. If no authorized browser session exists, ask for participation and mark UI acceptance untested.

A streaming tool result echoed by a model is not independent execution proof; inspect real tool events. Long task completion, reconnect persistence, durable recovery, approvals, unsolicited delivery and phone push are separate capabilities.

Refresh sources before implementation:
- https://hermes-agent.nousresearch.com/docs/user-guide/messaging/open-webui
- https://docs.openwebui.com/reference/env-configuration/
- https://coolify.io/docs/api/overview
