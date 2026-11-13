# Evidence model and provider-neutral acquisition

These are requirements to check against actual task files, not prevalidated
provider behavior or a ready-to-run importer.

## Independent evidence tracks

| Track | Minimum useful record | Does not prove |
|---|---|---|
| Requested identity | Literal label, authored/ranked concept, authority evidence | This photo depicts it |
| Image identification | Exact source ID, caption/description/category and caveats | Expert authentication |
| Rights | Image-bound elected grant, scope/version, credit, source chain, notices | Visual usefulness |
| Original integrity | Source representation, source digest where available, local SHA256, decode | Ownership or species |
| Original review | Actual viewed file/hash, observations and resolution limits | Final derivative quality |
| Derivative review | Actual selected output/hash, stage-specific inspection | Publication |
| Selection | Explicit useful role and all required gates | Exhaustive search |
| Preparation | Consumer-compatible record and successful read-only checks | Public bytes |
| Publication | Authorized upload plus verified destination response | Recipient browser cache freshness |

Use pending, blocked, rejected, withheld, not-attempted and complete per track;
never one blanket boolean that launders unfinished work. A source can be legally
eligible but visually rejected, or useful but archive/rights-pending.

## Minimal per-source receipt

- Stable provider/item identity; aliases and upstream imported IDs where relevant.
- Source page and original-rendition locators, retrieval time and its basis.
- Archived metadata, description, relevant histories and rights notices.
- Pinned description revision separately from binary upload timestamp/hash.
- Raw original path, byte count, SHA256 and available source digest/encoding.
- Decoded format, encoded dimensions, orientation and display-oriented dimensions.
- Supplied creator/uploader credits, elected license URL/version and change notices.
- Independent identity, rights, original-review and derivative-review records.
- Selection/rejection reason, actual reviewed paths/hashes, stage and current gaps.

Archive source metadata before derivative stripping. Hash integrity is not legal
clearance. Do not equate an ETag with SHA256 or a filesystem mtime with first
upstream retrieval. Reuse requires matching evidence and bytes, not a filename.

## Public photo-share acquisition

1. Inspect the actual supplied source and its final provider URL after redirects.
2. Determine single item versus album and intended subset; record visible order.
3. Use only ordinary authorized public retrieval, not private APIs or guessed
   credentials. Provider-specific extraction is not bundled here.
4. Prefer the best exposed rendition for the task; label it accurately rather
   than calling a social thumbnail or largest rendition an original.
5. Download to task-local temporary storage. Check nonempty bytes, actual media
   type, successful decode and plausible dimensions; don't trust extensions.
6. Dedupe underlying provider IDs and, where useful, content digests; changing
   thumbnail URLs do not establish distinct album items.
7. Compare extracted IDs/count/order to the visible album. If the public page
   exposes only an ambiguous subset, ask for attachments or a clarified subset.
8. Return exact local paths. Acquisition must not trigger an upload or note commit.

Treat share URLs and originals as potentially private even when publicly reachable.
Do not persist access-bearing links in skills or long-lived memory. Keep originals
only as authorized; retain a secure task archive when evidence retention requires it.
