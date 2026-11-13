---
name: skill-library-maintenance
description: "Audit and consolidate skills with reversible changes."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Skills, Learning, Maintenance, Provenance, Publication]
    related_skills: []
---

# Skill Library Maintenance

Review saved learning, consolidate overlapping procedures and prepare portable skill releases. This is a procedure-only package: it does not install a curator, replay approvals or publish anything by being loaded.

## When to Use

- Audit whether learning is proposed, actually saved or subsequently reused.
- Review accumulated skill proposals and conflicting variants.
- Compare installed packages with their distribution repository.
- Prepare an explicitly authorized consolidation or public release.

Do not use for general Hermes setup, model training, legal clearance or an unrelated deployment. A recommendation request is read-only; it is not permission to apply the recommendation.

## Prerequisites

- Resolve the active profile and actual Hermes home from the runtime; it can differ from the shell home.
- Identify exact source roots, repository/revision, ownership and authorized read/write boundaries.
- Consult current [official Hermes documentation](https://hermes-agent.nousresearch.com/docs/), installed help and native tool schemas before using version-sensitive commands.
- Use `read_file` and `search_files` for inspection, `write_file`/`patch` for authorized artifacts, native skill operations for installed packages, and `terminal` for Git and safe offline tests.
- Treat read, edit, install, queue retirement, commit and push as separate permissions. Determine which the user actually granted.

## Procedure

1. **Establish actual state.** Inspect settings, applied memory/skills, pending records, usage telemetry and maintenance reports. Distinguish configured learning, staged proposals, successful writes and real reuse; no one metric proves the rest. A result containing `staged: true` is not an applied change. Done when each claim has a direct evidence source.
2. **Freeze scope and back up.** Record the complete input manifest with hashes, actions, target paths and dependencies. Snapshot the relevant installed library and original proposals before mutation. Exclude recursive backup trees, runtime caches and Git internals. Protect private audit material and make scoped recovery possible. Done when originals are recoverable without overwriting later work.
3. **Inventory before judging.** Count readable and malformed records separately. Group canonical payload duplicates, same-name variants and semantic families. A create plus supporting writes can be one package, not duplication. Check patch preconditions against both installed files and pending dependencies. Done when exact accounting and unresolved inputs are explicit.
4. **Review actual payloads.** Read complete bodies, scripts, supporting files, patch text and conflicting versions in bounded batches. Preserve omitted spans for further inspection. Review both `content` and `file_content` when inconsistent. Never execute proposal-supplied commands merely to inspect them. The newest draft is not automatically the best; preserve older verified lessons. Done when every original has a substantive ID-keyed review note.
5. **Consolidate by task class.** Prefer an existing suitable skill or a focused reusable procedure over synonym skills. Preserve references, scripts, templates and transitive dependencies. Remove task diaries, private case facts, stale results and unsupported historical success claims. Reject, repair/test or explicitly defer unsafe helpers; replacing code with prose narrows the deliverable. Done when destinations and limitations are explained per original ID.
6. **Prepare the complete overlay.** Assemble unchanged installed files plus explicit updates, or a self-contained new package. Preserve authorship, licence and verified ownership. Autonomous maintenance must not adopt, unpin or bypass protected skills; stop when native ownership/provenance guards refuse a write. Done when package closure and authority are both known.
7. **Validate before applying.** Parse metadata, check platforms/paths/references, inspect private information and run appropriate offline tests/security scans. Obtain an independent bounded review of the final overlay. Static validation, native installation and live workflow execution are different milestones. Done when concrete blockers are resolved and unrun checks remain explicit.
8. **Apply narrowly within scope.** Recheck current bytes immediately before each write. Compare frozen/current/proposed states, preserve intervening valid additions and treat an already satisfied result as a no-op. Use supported skill/file operations and verify actual saved bytes, not only success flags. If a permission prompt timed out, stop that operation: obtain fresh consent before retrying or switching execution routes. Never disable unrelated command approvals to finish learning maintenance.
9. **Reconcile and retire.** Maintain one disposition per original: `applied`, `merged`, `superseded`, `rejected` or `deferred`. Require exact ID-set equality, no duplicates and agreement between destinations and source IDs. Archive originals and any deferred work before retiring only the processed, hash-matching active records. New or changed pending records stay untouched. Done when installed state, remaining queue and recoverable history agree.
10. **Publish only when requested.** Compare complete packages and consumer behavior, not version strings alone. Preserve public hardening when porting private changes. Scan final outbound files and history, exercise package-specific tests and obtain a fresh release review before commit/push. Verify the actual remote ref/content afterward. Done when every publication claim names the milestone actually proved.

## Supporting references

- `references/hermes-learning-approvals.md` — future-save settings, native approvals and read-only queue interpretation.
- `references/draft-consolidation-validation.md` — exhaustive review, ID-keyed reports, dependencies, overlays and live drift.
- `references/distribution-audit-patterns.md` — provenance and complete caller-chain comparisons.
- `references/release-packaging.md` — metadata, installability, offline parity and release gates.
- `references/publishing-contracts.md` — exact content, ambiguous attempts and source/build/public-page boundaries.
- `references/trust-boundary-review.md` — privileged file/subprocess regression requirements, not an implementation.
- `references/provenance-privacy.md` — exact source pins, conservative privacy exceptions and truthful freshness.

## Pitfalls

- Matching text proves patch applicability, not correctness; matching IDs prove accounting, not full review.
- Zero exact duplicates can coexist with extensive semantic overlap.
- Automatic future saving does not process existing pending proposals or prevent poor-quality duplication.
- A local version may be older or less safe than the public package; do not overwrite hardened code wholesale.
- A read-only audit does not authorize history rewriting, credential discovery, live canaries or publication.
- A copied/relocated bundle is not proof of the real installer's behavior. A procedure is not a deployed automation.
- Rollback is scoped: compare recorded after hashes and preserve later edits instead of unpacking an old whole-library snapshot over live state.
- Do not store current queue totals, commits, test counts or task outcomes as permanent skill rules.

## Verification

- Original inputs, complete-payload review and disposition accounting are separately evidenced.
- Every original is assigned once; dependencies and deferred work remain recoverable.
- Ownership, authority, private-data handling and native guards remain intact.
- Applied files are read back; intervening additions and unrelated runtime code are preserved.
- Offline/static, installation, live workflow and remote-publication results are reported separately.
- Final report states changed packages, verification, untouched scope and remaining decisions without dumping private audit contents.
