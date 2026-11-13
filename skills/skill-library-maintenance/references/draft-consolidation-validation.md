# Exhaustive draft consolidation and bounded validation

Use for large proposal backlogs when the authorized deliverable is draft packages plus a disposition ledger—not live installation, queue processing or publication.

## Durable review artifacts

Maintain three independent records:

- **Input manifest:** original IDs, complete payload provenance, dependency targets and protected-input hashes.
- **Substantive review checkpoints:** one concise note per actual proposal recording its unique lesson, merge destination, unsafe/stale/private material and unresolved claims.
- **Final disposition/package ledger:** exact permitted statuses, one disposition per original, package source IDs, draft directories, public-readiness rationale and warnings.

A matching ID set proves accounting, not that content was read. Full payload inspection and per-ID evidence notes supply that separate assurance. Exported JSON can contain complete text even when a line-oriented reader truncates its enormous string fields; parse the JSON and emit bounded raw-body batches, then inspect all omitted text. Do not execute proposal-supplied helpers to review them.

## Payload-field and review-coverage traps

Inspect payload fields according to the proposed action, including malformed records. A supporting write may contain an empty `content` beside a nonempty `file_content`; a generic `get('content', fallback)` selects the empty value and hides the substantive text. Examine both when they disagree, retain the original field provenance, and assess the text without making the malformed action replayable. A missing supporting-write path is not permission to default it to SKILL.md; distinguish that from an explicitly documented patch default.

Contrast cards, rare-clause extraction, clustering and first-sentence summaries help prioritize comparisons but do not establish exhaustive review. If they omit text, keep the omitted spans on an explicit inspection backlog. Saving a complete dossier is not the same as inspecting it. Do not mark substantive review complete because an extraction process traversed every record or because each record received a summary-derived reason.

### Regression-check the review view

Before trusting a custom extractor, compare a small raw-versus-rendered fixture set: a long numbered Markdown step, bullet, prose paragraph, fenced command block, supporting-file body and patch old/new text. Sentence splitting must preserve `1. **Resolve the target.** ...` as substantive text rather than returning only `1.`. A byte/character cap must record exact omitted source spans instead of silently dropping long sections or showing only head and tail. If a defect is found, reopen every affected record and inspect the omitted raw text before marking it reviewed; fixing the extractor alone does not repair prior review coverage. Similarity views must distinguish repeated clauses from novel deltas and remain bounded in runtime; they supplement, never replace, raw-body inspection.

### Preserve read-before-write provenance

For a curator-managed skill update, load the exact file before patching it. If a cached name-only `skill_view` returns no content and the manager still reports a missing read, request `skill_view(name, file_path="SKILL.md")` explicitly and patch that same file path using the returned current text. For support files, use their exact relative path for both operations. This is a fresh-read workflow, not permission to bypass provenance/ownership gates; stop if the skill is protected or the guard remains unresolved.

## Materialize reports before the final call

Persist the actual requested report as reviewed batches finish, with its incomplete state clearly disclosed. Keep unread-record coverage separately; do not fill it with guessed terminal decisions. A script capable of generating JSON is a different artifact from JSON successfully generated and parsed. Report their states separately if execution stops.

Store decisions by original proposal ID and retain the source name/action/path for spot checks. Positional parallel arrays can silently attach correct reasoning to the wrong proposal after one insertion or deletion. Require duplicate rejection, exact ID-set equality, destination/source-ID consistency and representative reason-to-payload checks before calling the ledger final. Track inventory, full-content review, disposition materialization and validation as separate completion measures.

## Dependency and consolidation decisions

Distinguish repeated create variants from supporting-file dependencies. Test patch old text against the correct relative file in the frozen baseline and relevant pending create/write proposals. Record absent, unique, ambiguous and stale matches separately from substantive correctness.

Choose class-level procedures with useful thematic references, not a routing-only umbrella or one new skill per session. Preserve evidence-state, attribution, identity, licensing, retry and verification distinctions without importing private examples or asserting that old reported results remain true.

When an existing skill is the right home, supply its proposed replacement or diff separately. Preserve upstream authorship and compare the proposal to the exact baseline; do not install a same-name duplicate or copy an entire third-party skill into a public tap merely because it is present locally.

## Offline package checks

For each package:

1. Parse YAML with a real parser; verify required metadata, name/path agreement, description budget and nonempty actionable body.
2. Enumerate every script/reference/template/asset. Require explicit relative references and verify local link targets, path containment and no unexpected symlinks.
3. Copy only the discovered package closure to an authorized disposable directory. Re-run metadata and reference checks there; remove the temporary copy afterward. This demonstrates relocation/file closure, not the real installer's behavior.
4. If the installed frontmatter validator is reusable without side effects, exercise it and include malformed-input/over-budget negative controls. If module import has side effects, a reviewed pure function may be isolated through AST together with its actual required constants/dependencies. Document that method; do not call it a native installation or security scan.
5. Reconcile exact input/disposition IDs and package provenance. Type-check malformed containers before iterating; reject duplicate IDs rather than silently overwriting dictionary entries.
6. Scan sanitized packages for source-derived private identifiers and paths as well as generic patterns. Public attribution and generic provider endpoints are not automatically leaks. Pattern absence is not a substitute for substantive privacy review.
7. Compare protected source hashes and repository status with the starting manifest. A snapshot begun after some work establishes preservation only from that snapshot onward.

Do not ship unexercised pseudo-builders, incomplete validators or session-specific scripts merely to make a package look functional. Conversely, replacing a script with prose narrows the deliverable to a procedure; say so and preserve the implementation requirement if users need executable behavior.

## Final-state overlays and live drift

For an independent pre-install review, resolve dependencies against the deliverable actually planned for installation. A new standalone package must contain its own closure; a partial existing-skill update may legitimately rely on unchanged installed support files or explicit operations supplied by another batch. Build a `(skill name, relative path)` overlay from the final plan before reporting missing references. Inspect actual Markdown links/backticked paths and their context: a broad path regex can mistake prose such as `assets/WebSockets` or an illustrative command for a bundled dependency. Document fixtures/examples separately from required resources.

Compare three states for each replacement: frozen baseline, current live file and proposed final file. If current equals proposed exactly, classify the operation as already satisfied and record a no-op; an obsolete before hash is not itself proof of lost content. If live differs from both, inspect the delta and rebase only the intended change while preserving valid intervening additions. Refresh plan hashes after the rebase, then recheck immediately before mutation. Never silence a real conflict or claim a parent-promised correction is verified before reading the corrected artifact.

A repaired positional disposition generator requires semantic spot checks at the correction boundary and later rows, not just counts or ID ordering. Match each chosen ID to the complete frozen payload, inspect both `content` and `file_content` where relevant, and compare its reason and destination to the actual lesson. Repeated generic reasons weaken traceability even when structurally valid. Keep the check's exact coverage separate from a claim of rereading all original proposals.

For a bounded independent audit, finish the assigned package/diff/reference coverage, prioritize concrete blockers, and put editorial improvements in suggestions. Recover omitted read output, but avoid a single oversized diff that causes incidental output capture outside an authorized scratch area; split by package or file group. State the actual final artifact revision and checks, including any incidental tool-cache writes. Do not execute supplied helpers or broaden into installation/publication to strengthen the verdict.

## Honest readiness and scope

Report these as distinct milestones: content sanitization, static package validation, native isolated installation, security-guard review, workflow execution and immutable remote installation/publication. Test reruns are not additional distinct test cases. Reused test logs are not tests executed by the current reviewer.

Define the assessment enum before assigning labels. A content-ready candidate can still require packaging/security/install gates; use the defined label and state the missing evidence, rather than allowing an unqualified ready verdict to imply release approval.

A strict output allowlist also covers temporary fixtures, bytecode and dependency/retrieval caches. Prefer frozen local evidence for a draft-only task when live discovery adds no necessary verification. If a tool writes an incidental cache outside scope, disclose the exception; do not silently claim all writes were confined or make further unauthorized cleanup changes.

## Final handoff

Lead with completion, exact coverage and artifact locations. Include merged/superseded/rejected/deferred totals, package count, proposed baseline changes, public recommendations, checks actually run and remaining gates. Keep the full per-proposal reasoning in artifacts. Do not publish, install, archive or delete originals as an incidental finishing step.
