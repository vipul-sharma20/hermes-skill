---
name: amp-hermes-mcp
description: "Use when connecting Amp to scoped central Hermes tools."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Amp, MCP, Agent-Integration, Privacy, Approvals]
    related_skills: []
---

# Scoped Amp–Hermes MCP Integration

Build, register and verify a narrow remote bridge from Amp to an existing central Hermes. This is a tested workflow skill, not a turnkey server or a first-party Amp–Hermes connector. It deliberately does not ship another user's deployed runtime, credentials, knowledge exports or infrastructure configuration.

## When to Use

- Amp needs selected personal/project conventions without copying a private Hermes profile into orbs.
- Coding agents should request privileged work from the owner, not receive deployment credentials.
- An existing bridge needs its permissions, context scope, lifecycle or end-to-end behavior checked.

Don't use for connecting an external MCP server *into* Hermes, duplicating a profile, exposing the entire private wiki, or granting unattended administrative access. The Linux gate covers the central runtime/supervision recipe; Amp clients may run elsewhere.

## Prerequisites

- An existing central Hermes with working provider authentication, its actual `HERMES_HOME`, source location and Python interpreter discovered with `terminal`/`search_files`.
- An authenticated Amp account and a deliberately selected personal/workspace/project scope. Reuse existing authorization privately; ask for necessary sign-in, never guess credentials.
- The MCP SDK with StreamableHTTP support in the selected runtime; inspect installed signatures before adding dependencies.
- An authorized HTTPS route, separately generated MCP bearer credential and a private owner-review destination. No new paid service is implied.
- Owner approval of the specific knowledge sections and the allowed action-request categories. Keep settings in private configuration and secrets in protected files/environment; never put either into this skill.

`HERMES_MCP_URL`, `HERMES_MCP_TOKEN_FILE`, `AMP_SMOKE_PROJECT` and `AMP_COVERED_MODE` below are operator-supplied command placeholders, not invented Hermes configuration keys. Quote them and discover their values; use reserved example domains only in reusable documentation.

## Tool Contract

| Tool | Scope |
|---|---|
| `get_context(topic, project)` | Return only explicitly reviewed, source-cited knowledge sections. No arbitrary path input or recursive private-vault search. |
| `ask_hermes(question, project)` | Answer from approved excerpts in a fresh zero-tool central-runtime consultation. No private memories/history, shell, or privileged actions. |
| `request_action(action, project, artifact, details)` | Queue a request and notify a fixed private owner destination. Never execute the request. |
| `get_action_status(request_id)` | Read one known unguessable request ID. No enumeration, remote approval or execution endpoint. |

## Procedure

### 1. Discover before changing anything

Read the current official docs below and the actual host's runbook. Identify existing gateways, reverse-proxy routes, profile ownership, ports and service supervision. Inspect installed `AIAgent`, provider resolver and MCP interfaces; do not assume private APIs are stable across versions. A read-only prompt sent to a full-power API agent is **not** a permission boundary.

The official `mcp-serve` plugin is primarily a stdio conversation/tool bridge; it is not automatically a scoped “ask personal Hermes” interface. Choose a custom bridge only for the missing behavior. Done when the actual consumer, deployment boundary and authorized changes are explicit.

### 2. Approve knowledge without cloning it

Use an owner-controlled manifest of `{id, path, start_line, end_line, sha256}` entries. Review exact text first. Resolve only manifest IDs; reject symlink components, nonregular/oversized files and invalid line ranges. Hash the selected UTF-8 text with original newline bytes preserved, not newline-normalizing `read_text()` defaults. Reread and verify SHA256 on every retrieval.

Bound question length, results and total excerpt size; rank meaningful domain terms rather than question boilerplate. A changed section must fail closed until reviewed again—never blindly refresh hashes or follow links into credential notes. Local checkout content is not proof of live infrastructure or remote freshness. Done when private/unlisted files are unreachable and ordinary natural-language queries retrieve the relevant approved sources.

### 3. Make consultation structurally powerless

Launch a fresh process using the central profile's existing provider resolution; never copy its profile/auth into an orb. Set `HERMES_SAFE_MODE=1` before importing Hermes and remove kanban/delegation worker markers. Resolve the server-owned configured model, not a client-supplied provider, credential, base URL or system prompt.

Use these constructor options and verify their installed meanings:

```python
consult_options = dict(
    enabled_toolsets=[],
    skip_memory=True,
    skip_background_review=True,
    skip_context_files=True,
    load_soul_identity=False,
    save_trajectories=False,
    checkpoints_enabled=False,
    session_db=None,
    quiet_mode=True,
    max_iterations=2,
)
```

Constructor flags alone are insufficient. In the dedicated adapter:

- Own **both** `_build_system_prompt_parts` and `_build_system_prompt`; ordinary appended system instructions do not replace private prompt assembly.
- Reject the entire `_execute_tool_calls` dispatch seam. Blocking only `_invoke_tool` misses sequential/special dispatch paths.
- Refuse any nonempty tools/valid-name snapshot or loaded private memory store/manager; do not expose deferred `tool_search`/`tool_call` helpers.
- Set `_skip_mcp_refresh=True`, `_persist_disabled=True`, `_session_json_enabled=False`; keep session history bridge-owned and never resume the user's normal session.
- Accept only the built-in `compressor` context engine. General safe mode does not disable separately discovered provider modules or every context engine; installed provider/runtime code remains trusted.
- Pass only selected excerpts as data. Return final answer, citations, completion/mode and tool count—not reasoning, raw messages, runtime objects or provider errors.

**Compatibility startup gate:** Before any model request, verify the installed constructor options, private prompt/tool-dispatch hooks, and zero-tool/privacy invariants above. If any are absent, changed, unsupported or unverifiable, abort startup before any model request. Never silently ignore unsupported options or fall back to a normal `AIAgent`.

Bound admission, iterations, output and child lifetime. Use `json.dumps(..., ensure_ascii=False)` with UTF-8 and a serialized-size budget that also accounts for escaping/control characters and metadata. Check `completed`, `failed`, `partial` and interruption/error fields, not just a nonempty final string. OAuth refresh may write internal auth state; read-only model actions are not OS isolation or a promise of zero internal writes. Done when an attempted tool call cannot dispatch and no private prompt/memory reaches the model.

### 4. Separate request submission from execution

Allowlist request categories such as `preview_deploy`, `publish_site`, `save_knowledge`; bound every field. For deployments, accept a plain HTTPS repository/full-commit reference, not an orb-local path, URL credentials or arbitrary upstream URL. Validate the artifact separately before execution; URL syntax alone proves neither existence nor authorization.

Queue UUID4 admissions in private durable storage with status `pending_owner_approval`. Notify only a server-configured private owner destination; client input must not select the recipient. Label submitted details as untrusted data and prevent mention/formatting abuse. Return notification failure explicitly without autoexecuting or blindly retrying a side effect.

Advertise `_meta["anthropic/requiresUserInteraction"]=true` for `request_action`. Amp's **Ask First** permits submission only; actual work requires **separate owner approval** through the trusted Hermes chat. After approved work is genuinely verified, an owner-only path may record immutable `completed`, `failed` or `declined` outcomes and a shareable result. No remote approve/execute shortcut or background autoexecutor. Done when a test request can be delivered/read back and declined without performing work.

### 5. Expose only the bridge over HTTPS

Generate a dedicated strong bearer token into a protected file, never print it or reuse the full-power Hermes API key. Bind loopback unless an authorized container/proxy topology needs a private network listener. Keep Host/Origin protection, constant-time token comparison, duplicate-authorization rejection, request-size/time limits and bounded model concurrency. Missing/incorrect authentication must fail closed.

Use native MCP structured results. Some SDK versions cannot infer structured output from a bare `dict` return annotation; use an explicitly supported model/schema and test the actual wire result. Preserve all existing dashboard/API routes; do not reroute a broad `/api` prefix or expose the general agent API. Done when TLS validates, exact bridge tools are discoverable, and unrelated routes retain their authentication.

### 6. Supervise only the bridge

Use existing operator-managed supervision. Never restart the main Hermes gateway from its own agent process or recreate unrelated containers to apply bridge code. With `systemd` plus `docker exec`, stopping the Docker CLI alone may leave the in-container server alive: add and test a stop operation restricted to the **exact bridge argv/process**, not a broad process match.

Keep runtime state outside the skill directory. Test a deliberate bridge-process replacement and compare the personal gateway/container identity and start state before/after. Do not claim full container-recreation recovery without testing it under explicit authorization. Done when the bridge recovers and the personal agent is unchanged.

### 7. Register the correct Amp scope

Inspect before adding, so reruns do not duplicate or overwrite an unrelated integration:

```python
terminal(command='amp mcp remote --personal list --json', timeout=60)
terminal(
    command='amp mcp remote --personal add Hermes "${HERMES_MCP_URL}" --auth bearer --bearer-token-file "${HERMES_MCP_TOKEN_FILE}" --json',
    timeout=90,
)
terminal(command='amp mcp remote --personal check Hermes --json', timeout=90)
terminal(command='amp mcp remote --personal tools Hermes --refresh --json', timeout=90)
```

Use workspace/project scope only if requested. Personal remote definitions are stored by Amp and work across clients/orbs; a local `amp.mcpServers` entry is not equivalent. Never pass token values in arguments; Amp supports a protected file or stdin.

In the actual signed-in settings UI, disable **Use in Multiplayer Threads** and verify the saved setting after reload. This is accident-prevention, not adversarial server-side authorization; a determined contributor can bypass it. It does not apply to local `amp.mcpServers`. Confirm read-only tools are allowed and action submission is **Ask First**. Preserve existing personal guidance when appending a short routing instruction; do not paste the private wiki or identity into Amp. Existing threads need **Reload MCP** or a fresh thread. Done when both the saved account configuration and the consumer's catalog are verified.

### 8. Prove the complete path and clean up

Run offline boundary tests first: manifest scope/hash changes/symlinks, URL validation, queue persistence/outcomes, no-tool dispatch/private-prompt suppression, Unicode and escape-heavy payloads, auth/Host/Origin/body limits and concurrency. Use a fresh independent reviewer; fix concrete findings and rerun tests.

Before creating the canary, use installed `amp --help` to verify this version supports `--visibility private`; abort if unsupported or unverifiable. Then create an isolated private canary using a user-approved project and an already-covered model mode:

```python
terminal(
    command='amp -ox "Use tool_search and code_exec to call the personal Hermes MCP ask_hermes tool for approved project build constraints. Cite its actual answer. Do not read or edit files, call request_action, or deploy anything." --project "${AMP_SMOKE_PROJECT}" --mode "${AMP_COVERED_MODE}" --visibility private --stream-json',
    timeout=300,
)
```

Read back the created canary thread's actual visibility and confirm it is `private`; the CLI flag alone is not proof. If visibility is not private or cannot be verified, stop the canary and do not make further MCP calls.

Inspect actual tool-use/result events, not merely an agent's success claim. Separately test one clearly labeled queue/notification request, read back the delivered message by ID, and record it declined. Archive only the canary; verify its orb is stopped and leave active user threads alone. Report real results and the initial knowledge scope without implying whole-wiki access. Done when the authenticated consumer, actual consultation, private approval-request delivery and cleanup are all verified.

## Pitfalls

- Broad shell/file/session-search tools, full profile copies and prompt-only restrictions defeat the intended boundary.
- A source-count or token-overlap test alone can hide irrelevant retrieval; use a representative natural-language question.
- Never substitute fake model answers, cached proof from another run, or version/binary checks for an actual end-to-end call.
- A queued action, an Amp submission approval and a verified completed operation are three different states.
- Delayed subagent/process completion messages are not a reason to repeat an already verified side effect.
- A harmless inline Python heredoc can confuse a lifecycle scanner when path operators resemble shell paths. Use a normal reviewed `.py` file; do not disable the guard or restart the gateway to work around it.
- This skill is the reusable procedure, not the deployed bridge implementation. Reuse an explicitly reviewed runtime when available; otherwise build/test a version-compatible adapter before claiming installation.

## Verification

- [ ] Correct Amp account/scope and exactly the intended four tools; no shell, approval or execute tool.
- [ ] Private profile, history, credentials and unreviewed source sections remain inaccessible to clients.
- [ ] Invalid/missing token, hostile Origin/Host, oversized bodies and busy model admission are refused.
- [ ] Model completion is genuine, zero-tool, source-cited and not a partial/failed result.
- [ ] Multiplayer privacy and action-tool Ask First policy persist after settings reload.
- [ ] Request notification is read back, its outcome is explicit, and no test work is executed.
- [ ] Bridge replacement leaves personal Hermes unchanged; the canary is archived/stopped.
- [ ] No machine-local config, private transcript, token, identity store or test artifact is published with the skill.

## References

- https://ampcode.com/docs/customize/mcp — remote scopes, bearer files, tool policy, multiplayer privacy and reload behavior.
- https://hermes-agent.nousresearch.com/marketplace/mcp-serve — what the official server exposes and does not expose.
- https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration — supported agent-host protocols; inspect installed internals for adapter details.
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills — installation, progressive loading and skill-write approval.
