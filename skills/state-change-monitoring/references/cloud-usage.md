# Cloud usage evidence and accounting

A collector-only assignment does not authorize scheduling, sending messages, provisioning or changing plans. Use read-only documented APIs and separately approved query-only GraphQL POST; prohibit mutations. Keep authentication on exact approved official origins and do not forward it on redirects. Listing/analytics requests may themselves be metered.

## Evidence contract

Each source records status (ok/no_records/partial/unavailable), observation/coverage times, units, completeness and safe errors. Genuine zero requires an actual zero measurement or complete empty inventory. No rows, permission denial, truncation and timeout are not zero.

Fatal invalid credentials/no usable primary evidence/persistence failure must exit nonzero with sanitized failure JSON; expected secondary gaps can produce a usable exit-zero snapshot with gaps plainly visible. Never timestamp a stale snapshot as newly collected.

Independent sources fail independently. Bound pagination, concurrency, request timeouts and one monotonic total budget. Missing/repeated cursors, a result at row cap and incomplete pages are coverage findings. Thread-pool cancellation alone may not bound process exit/DNS waits; use an approved process-level bound. POSIX signal/lock methods are not portable Windows recipes.

## Separate accounting dimensions

- Instantaneous inventory/storage is not request usage, historical daily peak or invoice total.
- Keep daily records for daily quotas; a weekly average cannot prove daily compliance.
- Group by service, billing period, currency and unit. Use decimal arithmetic for monetary quantities.
- Sum interval quantities/costs only when semantics support it. Select latest cumulative values by coverage date; never sum cumulative daily costs.
- One recent service ledger row does not make every service current.
- Decimal GB, GiB and integrated GB-month differ. A cleanup now cannot erase earlier daily peaks/accrued storage.
- Zero base fee, usage-based plan and paid invoice are distinct evidence; current official terms decide billability.

## Cloudflare revalidation map

Refresh https://developers.cloudflare.com/api/ and https://developers.cloudflare.com/analytics/graphql-api/ for the selected account's permissions/schema. Candidate read surfaces include subscriptions, billable usage, billing history, R2 bucket metadata and service inventories. Check each returned pagination/container shape rather than freezing a historical page-size limit.

GraphQL services may have different date/datetime filters and aggregation semantics. Query separately so one inaccessible dataset does not hide all results; inspect schema/row limits for Workers, R2, D1 and AI analytics before use. No undocumented field is assumed by this package.

For R2 current storage metadata, use a maintained S3 client when available, paginate every authorized bucket and store only aggregate counts/bytes/storage class. Do not download object contents. Continuation tokens must round-trip exact bytes/URL encoding; + is not a space. Bucket-scoped credentials can leave gaps despite account-level discovery. Object keys and top-level prefixes can disclose private information; allowlist/aggregate them.

Refresh https://developers.cloudflare.com/r2/pricing/ rather than encoding old rates. Read-only ListObjects is a Class A operation under current published pricing; GetObject/HeadObject are Class B examples. The published free-operation examples include DeleteObject, DeleteBucket and AbortMultipartUpload, but cost classification is not permission to invoke them. Keep unknown operation names as explicit accounting gaps rather than invent aliases. Storage billing uses daily-peak averaging and storage-class minimum-duration rules; do not equate a live byte snapshot with accrued GB-month.

## Persistence and tests

Keep the last successful subscription baseline separate from a failed/latest snapshot. Atomic private output, overlap lock and bounded dated retention are explicit contracts; do not silently establish retention policy. A stdout size limit must not discard necessary sanitized on-disk daily evidence.

Test the real collector orchestration/CLI/persistence with fake HTTP and synthetic fixtures: no credentials from operator environment, pagination failure/repetition, zero/no-records/partial, cumulative/interval accounting, units, independent failures, fatal exits, baseline retention, privacy and archive limits. Live authorized CLI output must be separately measured; no historical private collector path or claimed past pass count is a reusable dependency.
