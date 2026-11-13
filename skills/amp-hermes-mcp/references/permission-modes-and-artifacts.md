# Permission-mode inspection and private artifact handoffs

## Inspect actual permissions without granting them

This public recipe remains scoped, zero-tool consultation plus queued requests
requiring separate owner approval. Inspecting an existing deployment gives no
authorization to change trust mode, grant tools, weaken approvals or run a
privileged canary. It is not a migration to a more permissive service.

1. Through authorized read-only access, inspect the active service factory,
   worker initialization, configured runtime/profile and private owner policy.
   Identify which code/config revision is actually running; a local checkout,
   old canaries, docstrings and tool names alone do not prove current permissions.
   Do not dump process environments or credentials to establish identity.
2. Inspect the runtime tool catalog, schemas and `_meta` annotations along with
   the real handlers and dispatch boundary. Determine whether consultation is
   zero-tool and submission only queues an owner-reviewed request. In particular,
   do not invoke `request_action` to discover whether it executes work.
3. If the service executes actions directly or exposes private context beyond the
   reviewed manifest, treat it as outside this scoped recipe. Stop and obtain
   owner/security review before any privileged verification; do not adapt this
   recipe to justify it or modify the deployment to match an old description.
4. Preserve bearer authentication, per-client authorization, Host/Origin checks,
   redaction, size/concurrency limits, Ask First and separate owner approval.
   Keep **Use in Multiplayer Threads** disabled and read back the setting. UI
   exclusion is accident-prevention, not adversarial server-side authorization.
5. Document the observed permission mode and uncertainty without publishing
   private code, config or context. Remember that returned private data enters the
   caller's model context; centrally held credentials do not make the client a
   sandbox. Distinct workers can start distinct sessions; polling a status tool
   is not proactive owner notification.

Read-only catalog inspection is not end-to-end proof. Inspect an old verification
helper for privileged effects and obsolete catalog assumptions before running it.
Continue to enforce the main skill's fail-closed compatibility startup gate and
private canary visibility checks; this reference supplies no execution shortcut.

## Verify a private artifact handoff

This is an owner-authorized handoff procedure, not another privileged MCP tool.
It does not change the bridge's artifact schema: deployment requests still accept
only the approved plain HTTPS repository/full-commit reference. An orb-local path
or private attachment is not silently promoted to an accepted execution input.

1. Confirm the exact owner-authorized attachment and purpose. Inspect
   `amp files get --help` through `terminal` on the target host. Where that version
   supports private downloads, use the owner's existing authenticated CLI and its
   documented output option. If support/authentication is absent or unverifiable,
   stop and request an authorized supported transfer; do not invent an endpoint.
2. Do not assume an anonymous attachment URL is readable, and do not expose the
   artifact to make it downloadable: no public rehosting or visibility downgrade.
   Download only to a protected temporary location outside the repository and
   skill payload. Keep authentication in existing protected CLI storage/environment,
   never token arguments, logs or tool results. Pass the URL/path as separate argv
   data in a reviewed adapter, not interpolated shell text; redact temporary URLs.
3. Obtain the expected full SHA-256 and intended exact full commit reference from
   a trusted owner channel. Compute the downloaded bytes' full SHA-256 with
   `terminal` and compare before parsing, importing or executing anything from
   the artifact. A matching filename, HTTP status, short hash or agent summary is
   not proof. A mismatch or missing trusted digest blocks the handoff; preserve
   diagnostic evidence privately without dumping private content.
4. For a Git bundle, obtain only the authorized prerequisite public history in an
   isolated verification repository, then use `git bundle verify` through
   `terminal`. It checks format and prerequisite commits in that repository; it
   does not approve code, deployment scope or trustworthiness. If prerequisites
   are missing, report exactly that rather than inventing equivalent patches.
5. Inspect advertised refs and verify the intended exact full commit and reviewed
   changes. Preserve commit identity; use only the owner's authorized fast-forward
   workflow after checking the destination and existing work. Do not force-reset,
   force-push, recreate commits or execute artifact code just to make import work.
   Deployment, publication and any privileged verification still require separate
   owner approval and real result verification.

Do not fabricate equivalent content after failed authentication, download, hash or
bundle verification. Report the blocker and stop. Keep artifact bytes, temporary
links, private history and logs out of public packages; remove only this handoff's
protected temporary files when their authorized retention period ends.

## Sources and attribution

- Procedure synthesis: Vipul Sharma (vipul-sharma20), Hermes Agent; adapted from
  reviewed permission-inspection lessons, without a deployed bridge implementation.
- [Public scoped recipe](../SKILL.md) — consultation boundaries, approval queue,
  compatibility gate, authentication and private-canary contract remain normative.
- [Amp MCP documentation](https://ampcode.com/docs/customize/mcp) — remote tool
  policies, `anthropic/requiresUserInteraction`, scopes and multiplayer limits.
  Inspect installed CLI help and signed-in settings before relying on
  version-sensitive flags or labels; unknown support is a blocker, not permission
  to weaken privacy or approvals.
- Installed Amp CLI help (`amp files get --help`) — inspected support for downloading
  a private attachment with an output path; this is a local capability check, not
  evidence that a given artifact is accessible or that every Amp version supports it.
- [Git bundle documentation](https://git-scm.com/docs/git-bundle) — verification of
  bundle format and prerequisite history; integrity and owner approval remain
  independent checks.
