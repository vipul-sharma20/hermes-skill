# Exact content, attempts and public verification

This reference is a publishing contract, not a bundled publisher or bridge implementation. Use an existing supported implementation only under separate publication authority.

## Direct publication

Separate the instruction from the intended public body and ordered attachments. Preserve requested wording, while checking the publisher's documented whitespace/tag normalization rather than promising byte-exact output it does not support. Prefer a safe request-file interface over shell interpolation. Re-read an edited source message from its live canonical source before deriving public text; a transcript can be stale.

Identify create-note, edit-existing-page, media-only and long-form workflows before acting. A note creator is not a fallback for correcting an existing page. Preserve caption/layout/reference conventions. Do not double-process media when the existing publisher already owns orientation, format, budget and metadata policy.

After successful creation, verify the existing publication; never publish again merely because propagation or a verification fetch failed. Check the exact source commit and content/media first, identify the corresponding build/deployment, then inspect the public page and intended assets. Those are separate milestones. Verify actual media bytes, content type, digest, dimensions and privacy metadata when required. A content-addressed asset does not make timestamped note creation idempotent. Report an orphaned upload after a failed content commit rather than creating another note to hide it.

An empty extractor can require authorized HTML/browser inspection. An uploaded object, accepted build or successful response is not proof of the final visible page. Report each failed or pending boundary honestly.

## Continuous bridges

Require explicit source-channel/user scope, membership review, root-only/bot/system/deleted filters and a start-after boundary to prevent historical auto-publication. Apply configurable edit grace and fetch canonical current state immediately before the side effect. Poll cadence is configuration, not a universal delivery-latency guarantee.

Under exclusive single-writer coordination, persist source-ID keyed attempt/in-progress state before side effects and durable published/failed/unknown state afterward. This can suppress automatic duplicate attempts; it is not an exactly-once recovery guarantee. Ambiguous attempts need explicit reconciliation rather than silent retries. Retain active/unknown states when bounding history.

Public publication and source confirmation are separate effects. A failed confirmation must not republish a note. Late edits need an honest bounded warning or a separately authorized edit, not duplicate creation. Unsupported attachments fail closed.

Use offline fakes to exercise source filters, edit grace, attachment order, lock overlap, crashes across each state/effect, ambiguous outcomes, confirmation failure and late edits. Keep metadata/orientation/size tests separate from source/deploy/page verification. A deterministic implementation may use a no-model scheduler, but its actual no-op, configuration and first authorized post require their own checks. Unchanged silence must never hide an incomplete or failed scan.
