# Page parsers and delivery contracts

## Dynamic pages

Inspect the permitted page's own public refresh flow with `web_extract` or an authorized browser. Use the same legitimate cookie/CSRF/origin context; no bypass of human verification, auth or rate limits. Treat undocumented endpoints as fragile and consented, not official APIs.

Normalize authoritative refreshed fragments before stale base HTML. Select one complete logical repeated-entity container; use base fields only when absent from fresh data. Never globally collect rows from fresh+base documents. Never deduplicate equal values: two passengers/items can legitimately match.

Server-generated JavaScript strings are not necessarily JSON. A narrowly validated decoder may need to handle JavaScript-only escaping, including escaped apostrophes. Do not evaluate arbitrary returned JS, globally unescape strings or apply one regex transformation to every grammar. Preserve the exact edge as a sanitized fixture and reject malformed/unrecognized formats.

Required tests: one list; duplicate whole containers still one list; two equal rows in one list still two entities; refreshed fragment precedence; missing/partial required fields fail; escaped-string regression; reordered metadata stable; changed identity rejected. Real HTML can contain PII—store only minimal synthetic/sanitized fixtures.

## State and delivery

Atomic state writes and locks prevent partial overlap, not transactional network delivery. For stdout-owned scheduling the script cannot infer that a message reached a phone. Choose duplicate/loss semantics explicitly; use a durable outbox with actual acknowledgments if needed. Never mark delivery confirmed solely because stdout was printed.

Prefer one scheduler delivery path. If the owner specifically needs platform-native posting/mentions, separately authorize it, use private runtime credentials and keep normal stdout silent to avoid duplicate delivery; retain an explicit error channel. Do not scrape tokens from a private note into logs. Never assume an unverified username mention triggers push.

Read back a sent message by stable ID when available and verify destination, author, approved text and identifier masking. Phone push additionally depends on server, channel, account, app, OS and mute/DND settings. Report the device boundary as user-observable.

Resolve the absolute profile home before `write_file`; file tool paths do not perform shell variable expansion. The no-agent cron script is normally a filename under the active profile scripts directory, not arbitrary argv; inspect the installed version. Multiple watches need distinct config/state and a tested launcher/dispatcher, not an implicit default that selects the wrong subject.

Current source: https://hermes-agent.nousresearch.com/docs/user-guide/features/cron . Current docs name the management tool cronjob_manage, while older examples may name cronjob; always use installed schema. Verify semantic Installed output for any separately approved skill installation; never pipe blanket yes through a security review or treat cancellation with exit 0 as install success.
