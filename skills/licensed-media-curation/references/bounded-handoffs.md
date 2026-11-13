# Bounded, resumable curation handoffs

## Start with durable state

Create the required handoff on claim/start, not at the last tool call. Record
exact labels, authoritative catalog checkpoint/hash, owner, permissions, phase,
budgets, artifact paths, source backlog, process state and genuine next action.
Initialize a review for every label but never call an unattempted placeholder
completed research. Preserve previousReview/history separately from current state.

Reserve time/tool capacity for review, final validation, handoff and ownership
cleanup. Count failed and nested requests conservatively. Before a slow request
or lock wait, ensure its worst-case duration fits the remaining global deadline.
An acquisition cap is not permission to exceed an elapsed-time or tool-call cap.

## Scheduling and recovery

- Use the designated coordinated fetch/cache path for discovery as well as media.
- Persist origin-wide cooldown/not-before state; Retry-After can be seconds or an
  HTTP date. Restarting a worker must not reset it. Don't route around limits.
- Coordinate workers at the shared origin; more threads around one serialized
  request path do not create throughput. Do not change lock protocols in one
  worker while others still use the old protocol.
- Small adaptive batches let actual pixels redirect the acquisition plan. Editing
  a running script does not update its in-memory targets or imported screening code.
- Keep one writer per manifest or merge immutable per-label/batch files under a
  lock. Never let stale history fetchers overwrite later review notes.
- Key caches by request semantics/URL, not result count. Empty results must not
  collide. Check recorded failures as well as success caches before retrying.
- Reuse verified originals and completed review receipts when still applicable;
  update only the genuinely missing gate. Resolve paths from stored records,
  never guessed hash-derived directories.
- Read helper signatures and return contracts before use. Avoid executing script
  prefixes or importing top-level orchestration; it can recurse, rerun acquisition
  or reset manifests. Avoid local module names that shadow standard libraries.

## Consumer-compatible output

Adapt filenames to the task schema; a useful split is:

- Scope/reviews: one exact-label record each, prior evidence, current stage,
  selected IDs/order, old/final counts, additions/removals, mandatory gaps and
  optional refinements. Specific rejected, withheld and unattempted findings.
- Canonical per-source decisions: identity, rights, review evidence, role, alt,
  location evidence, selection reason, timestamps and reviewer as required.
- Catalog overlay: full changed entries when the consumer expects them, no
  out-of-scope edits or empty public entries for withheld labels.
- Variants: only selected delivered outputs, real paths, keys, hashes and dimensions.
- Original/source verification: archives and exact digest/revision bindings.
- Verification/result: checks actually executed, counts, stop reason, publication
  state, next action and owned process/lease disposition.

Preserve retained baseline fields. Where the actual schema requires enrichment,
retrieve evidence; don't either drop old metadata or invent missing credit. Keep
extra creator notices through regeneration, not merely in a sidecar the consumer
will discard. Distinguish expected source names from broader discovery aliases;
when a consumer cannot represent an approved narrow bridge, propose an isolated
reviewable adapter change rather than weakening shared identity permissions.

## Read-back gate

Compute exact scope equality, unique reviews and source IDs; reconcile acquired,
reviewed, selected, withheld and derived counts. Verify final gallery ID order
matches reviews, variants point to selected files, original integrity and each
required pixel stage are supported. Reconcile additions/removals against the
baseline using stable IDs, not candidate-list positions.

If a project consumer is available and authorized, exercise its nonpublishing
path against real archives. Relevant negative checks include wrong subject,
missing grant/review/notice, altered original or derivative, wrong license and
scope leaks. Synthetic fixtures test software, not the real source's authenticity.
Do not set persisted selected=true merely to satisfy a temporary preparation test.

Finalize decisions before validation/hashing; a later edit invalidates dependent
records and must regenerate their checksums/preflight consistently. Stage a new
generation before replacing last known-good outputs. Seal static outputs only
after final reconciliation; don't self-hash a mutable manifest.

Write readiness only after every required gate passes. Interrupted work reports
last verified artifacts separately from newer unverified edits, live jobs and
unreleased ownership. Release only owned leases through the authorized queue
interface; artifact regeneration must not accidentally replay queue transitions.
