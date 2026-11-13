# Optional authorized asset delivery

These are destination-neutral safeguards, not an upload implementation. Use an
existing maintained storage/publishing integration; do not copy private helper
names or invoke a complete note publisher for an image-only request. No live
storage operation was performed while authoring this reference.

## Boundary before writes

Confirm user authority, exact account/bucket/destination, intended object and
whether the request is new upload, same-URL replacement, copy or deletion.
Use only explicitly configured credentials through the approved integration;
never hunt wiki notes, print secrets or rely on unspecified ambient credentials.
No repository commit, site deployment, DNS change or bucket creation is implied.

Discover the current destination organization read-only through the authorized
client, with pagination. Follow existing project prefixes rather than guessing a
competing folder or confusing project illustrations with licensed reference
assets. Local curation URLs remain prospective until public bytes are verified.

## Immutable new assets and copies

- Validate the encoded file's format/MIME, dimensions, byte budget, orientation,
  intended metadata policy and digest. Avoid re-encoding when only copying an
  already valid object.
- Prefer a descriptive, content-addressed key; retain the full digest in a manifest.
  An abbreviated digest is a naming aid, not proof against all collisions.
- If the destination exists, compare actual bytes and refuse unexpected collisions.
- Set public content type, inline disposition and cache policy deliberately.
  Long immutable caching belongs only to immutable keys.
- A server-side copy may need explicit metadata replacement. Verify source bytes
  against the current expected digest before copying and destination bytes afterward.
- Keep old URLs alive unless deletion/migration is explicitly authorized. Say
  'copied/stored under' rather than 'moved' if the original remains.

## Same-URL replacement is exceptional

Require explicit approval to replace already-shared bytes. Compare current content
to the expected old digest or the intended new digest for an idempotent repeat;
an unexpected third version is a concurrency conflict. A check-then-write can race:
use supported conditional operations where available, otherwise disclose the limit
and coordinate ownership before the write.

Use a revalidating cache policy rather than falsely promising immutable contents
at a changed URL. If a CDN purge is authorized, scope it to the exact URL and
confirm provider success; never purge a whole zone to replace one image. Do not
embed vendor account IDs, tokens or API recipes in this generic procedure.

Verify the canonical public URL without a cache-busting query. Compare returned
bytes/digest, MIME, dimensions and delivered cache headers. An origin update,
CDN purge and fresh client response are different results; a browser's existing
cache may remain stale even when the provider accepted a purge.

## Receipt and report

Record object key/public URL, old/new digests where applicable, bytes, dimensions,
authorized operation, origin read-back and public verification. ETags need not be
content SHA256. Report exact success versus stale-public-delivery limitations and
whether the prior URL was retained. Public URL verification must not expose
credentials or an access-bearing signed URL in a shareable report.
