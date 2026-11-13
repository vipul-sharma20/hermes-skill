# Hermes Learning Approvals and Proposal Audits

## Scope and evidence

This reference describes version-sensitive configuration and read-only audit procedures, not a bundled migration or script executor. Every actual migration, semantic review, archive/restore and workflow execution needs its own authorization and evidence.

Authoritative references:

- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills
- https://hermes-agent.nousresearch.com/docs/user-guide/features/curator

Recheck current documentation and installed behavior before relying on version-sensitive details, especially background replacement/removal rules and protected-skill policy.

## Automatic future saves

Resolve the active `$HERMES_HOME` first. An agent home can differ from the shell user's `HOME`; the active profile owns its own configuration, skills, pending records, and memory.

Use `terminal` to execute the supported configuration CLI, after verifying the requested scope:

```text
hermes config set memory.write_approval false
hermes config set skills.write_approval false
hermes config get memory.write_approval
hermes config get skills.write_approval
```

Both resolved values should read `false`. In the inspected installation, the write gate resolves its setting from config on use, and a subsequent genuine `memory` addition applied without staging. Prefer read-back and runtime evidence over an unnecessary restart assumption. Do not promise immediate reload behavior on other versions without checking.

Do not change `approvals.mode` to enable learning. General command approval is independent of these learning gates. Changing the gates leaves existing pending records untouched. Some versions may retain additional safeguards for particular background mutation types even with the ordinary gate off.

Where a useful verification save is appropriate, inspect the tool result for actual application rather than just `success`. Do not invent personal preferences, create a dummy skill, or write sensitive content merely to test the gate.

## Persisted evidence sources

Under the active home, the inspected implementation used:

- `memories/MEMORY.md` and `memories/USER.md`: applied built-in memory.
- `skills/.usage.json`: per-skill use/view/patch counters, provenance fields, and maintenance state.
- `pending/skills/*.json` and `pending/memory/*.json`: staged proposals.
- `logs/curator/<run>/REPORT.md`: maintenance outcomes and whether a model pass actually ran.

These paths are implementation details to confirm against the installed version. Do not treat absence of an optional ledger as proof that no learning happened. Curator pruning, skill-content consolidation, and learning review are distinct activities; a deterministic prune run does not demonstrate a semantic review.

A pending record in the inspected version contained `id`, `subsystem`, `action`, `summary`, `origin`, `created_at`, and `payload`; no `status` field was required. Payload shapes differed between operations. In particular, supporting-file records could use `file_content`, while create records used `content`. Inventory actual payload keys before assuming a uniform schema.

## Reproducible read-only analysis

The exercised audit used Python aggregation rather than loading all proposal contents into the conversation:

1. Read all JSON records, explicitly tracking parse/read failures; preserve originals.
2. Count action, origin, and `payload.name` using `collections.Counter`/grouping.
3. Canonically serialize `payload` with sorted JSON keys and hash it to identify exact duplicate operations. Do not hash the whole record, since IDs/timestamps make equivalent operations appear different.
4. Compare repeated names and related task families separately. Reworded content can generate many unique payloads while teaching essentially the same process.
5. Locate installed packages, including category nesting, while excluding archives and hidden/internal directories. Verify ambiguous names instead of selecting one arbitrarily.
6. For patches, resolve `file_path` or `SKILL.md`, test target existence, count exact occurrences of `old_string`, and inspect whether `new_string` is already present. Record the classifications without writing.
7. Flag missing write-file paths and create proposals whose name has since become installed. These checks identify review work; they do not establish a definitive reject decision.

Do not silently skip malformed records and then claim the entire backlog was audited. Record raw file count, readable record count, and rejected/unreadable count separately.

## Correct interpretation

- Many create proposals may be alternative drafts for the same named skill, not many distinct skill ideas.
- A create proposal and a reference/script write can be a valid dependency pair.
- No byte-identical duplicates does not rule out semantic repetition.
- Old text matching exactly once means the patch is mechanically applicable now, not factually correct or desirable.
- Replacement text already present is a review flag, not proof the entire requested change has been applied.
- Missing patch targets can be explained by an unapproved create; inspect the dependency graph before rejecting.
- The newest draft is not automatically the best draft; retain verified lessons from older variants where appropriate.
- Configuring future automatic saves is separate from approving historical proposals.

## Communication

Answer "is it learning?" with three separate facts: which mechanisms are enabled, which changes demonstrably applied, and which proposals remain staged. Explain saved runbooks/context rather than weight updates. Report uncertain telemetry limitations plainly.

For a backlog question, recommend content review and class-level consolidation rather than mass approval, but do not silently turn that advice into writes. If cleanup is authorized, preserve reversibility and produce per-record dispositions; describe unperformed migrations/tests as unperformed.

Keep snapshots and counts in a task audit artifact or session history, not in this evergreen skill. Do not embed private machine paths, account details, or the current backlog size into the reusable procedure.
