---
name: state-change-monitoring
description: "Build private, bounded monitors with change-only alerts."
version: 0.1.0
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Monitoring, State, Privacy, Scheduling, Alerts]
    related_skills: []
---

# State-change Monitoring

Design deterministic collectors and state machines for external statuses or metered-cloud evidence. This package supplies a procedure and test contracts, not an untested watcher executable. Use an existing tested provider-specific monitor when one already meets the need.

## When to Use

- Monitor reservation, shipment, application, service or availability transitions.
- Turn a permitted semi-structured status flow into a low-noise scheduled collector.
- Collect cloud inventory/usage without confusing missing evidence with measured zero.

Do not use for booking/cancellation, CAPTCHA bypass, aggressive polling, automatic billing remediation or an unsolicited schedule. A one-off lookup does not imply a watch.

## Prerequisites

- Approved source, subject identity, source terms and private disclosure consent.
- Requested cadence, alert fields, delivery destination and finite horizon/terminal condition.
- Protected runtime storage outside source control; identifiers and state must not enter prompts or job names.
- Read current scheduler docs and the installed schema/help before scheduling. This procedure does not assume a scheduler tool is available in every session.

## Procedure

1. **Define the contract.** Record exact subject/date/route or account, source, stable identity fields, normalized observation, meaningful transitions, failure policy and expiry. Done when two different subjects cannot share state accidentally.
2. **Qualify access.** Prefer documented first-party API/webhook, then approved partner, then consented permitted webpage flow. Probe with dummy identifiers first. Stop at login/CAPTCHA/human-verification gates. No automatic fallback may disclose private identifiers to an unapproved provider. Done when authorization and privacy trade-offs are explicit.
3. **Establish one live baseline.** Exercise the exact recurring request path with bounded timeouts, validate required fields and entity multiplicity, and distinguish retrieval time from source-update time. HTTP 200 alone is insufficient. Done when identity and completeness match the intended subject.
4. **Normalize and test.** Use stable IDs/order and meaningful fields; exclude refresh timestamps, ads and request metadata from fingerprints. Preserve identical-valued distinct entities. Write isolated synthetic tests for baseline/change/no-change/error/expiry before implementation changes. Done when replay decisions are deterministic.
5. **Persist last-good state.** Use owner-restricted files and atomic replacement in one filesystem; serialize overlapping runs. Failures update error metadata, never replace successful observations. Keep the last successful subscription baseline separately from the latest collection. Done when interruption/error tests retain readable prior state.
6. **Choose one delivery owner.** Prefer scheduler delivery of stdout with no model when the decision is deterministic. Successful unchanged ticks exit zero with empty stdout; emit only approved changes or throttled failures. Do not also post directly. Local state persistence alone cannot guarantee exactly-once delivery. Done when retry/loss/duplicate behavior is documented.
7. **Schedule only on request.** Use `terminal(command="hermes cron --help", timeout=30)` and inspect the installed create/edit help; if the tool catalog exposes `cronjob_manage`, use its current schema. Older examples may call it `cronjob`. Resolve the absolute active profile home before file writes; use the scheduler's supported script filename, not a shell command. Done when job readback matches cadence, destination, script, enabled state and finite lifetime.
8. **Verify the deployed path.** Exercise the actual no-argument launcher/config resolution, unchanged silence, one change, failure/recovery and terminal no-op. Read back one authorized delivered message where supported. A post is not proof of phone push. Done when tests, live source and delivery evidence are separately recorded.
9. **Stop narrowly.** Identify the job from live listing and subject/date, then pause/remove exactly that returned ID when requested. Report source failures as unknown/stale, not fresh status. No watch continues querying after terminal state or safety expiry.

## References

- [Page normalization and delivery contracts](references/parser-and-delivery.md) (`references/parser-and-delivery.md`).
- [Travel identity and lifecycle checks](references/travel-contracts.md) (`references/travel-contracts.md`): complements existing railway monitors; no duplicate provider runtime.
- [Cloud usage evidence](references/cloud-usage.md) (`references/cloud-usage.md`): pagination, units, billing and baseline coverage.

## Pitfalls

- A fresh check time does not make cached provider data fresh.
- Combining refreshed and stale HTML lists duplicates entities; value deduplication can erase real items.
- A finite execution count is not an exact wall-clock expiry; enforce the deadline in the script.
- Writing a notification fingerprint before delivery can lose an alert; writing it afterward can duplicate one. State the chosen at-least/at-most-once behavior or use an acknowledged outbox.
- Never store full booking IDs, channel IDs, cloud account details, response dumps or real itineraries in reusable fixtures.
- Script-only collection can still incur provider request/storage charges.

## Verification

- [ ] Consent, identity, source freshness and complete entity count verified.
- [ ] Real baseline is distinct from synthetic fixture results.
- [ ] Stable fingerprint; failed parse preserves last-good observation.
- [ ] Required timezone, hard expiry and no-network terminal state tested.
- [ ] Runtime script/config paths work through the actual scheduler invocation.
- [ ] One delivery mechanism; unchanged silence and error policy verified.
- [ ] No claim of future delivery, phone push or exactly-once delivery without evidence.
