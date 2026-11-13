# Publishing follow-ups

## Edited original source and existing-file correction

1. When asked to publish or correct an edited message, re-read the original live
   source through its authorized platform interface. Match the exact post ID,
   conversation and current edit timestamp; the transcript can be stale. Keep
   platform credentials private. An edited message is not itself authorization to
   publish: confirm the requested public body and ordered attachments.
2. If the original source is inaccessible, say so and ask for the exact current
   text or renewed access. Do not silently substitute session history or an old
   downloaded attachment for a source that may have changed.
3. Inspect the configured repository and branch for an existing repository file
   representing that source. Match the original permalink/edit path, body,
   attachments and commit history; do not guess from a similar title or timestamp.
4. If an obsolete version already exists, obtain authorization to correct that
   same path through the site's reviewed Git workflow. Preserve unrelated edits,
   frontmatter, date and URL. Read the latest revision first and use the current
   file SHA for an authorized Contents API update (or the reviewed Git equivalent)
   so a concurrent edit is not silently overwritten. Read back the committed file.
5. The bundled publisher creates a new timestamped note; it is not an update
   command. For an existing note, do not rerun the publisher to make a correction.
   After a lost response, inspect GitHub before any retry: a committed note can
   exist even when the caller received no success message.

Completion means the confirmed current source matches the intended existing file,
not that a second timestamped post was created. Report the exact corrected path
and commit separately from any later deployment evidence.

## Commit, build and public delivery

A commit, build/deploy result and public page are separate outcomes. Record only
what was actually checked:

| Outcome | Required evidence |
|---|---|
| Committed | Read back the exact path on the configured branch and record the exact commit SHA. The returned edit link alone is not a content read-back. |
| Build/deploy verified | Inspect the site's actual pipeline and the run ID tied to that commit, its status and any deployment result. A green run for another commit is not evidence. |
| Public delivery verified | Fetch the intended public page and its media; confirm the expected current body and assets, not just an HTTP success status or an old cached page. |

A successful commit does not guarantee a build was queued. The helper does not
call a deployment provider; its `publication triggered` text is not proof that a
site workflow ran or deployed. Until independently verified, report the commit
as saved and deployment pending (or deployment unverified/failed as appropriate).
Do not promise a fixed build duration or say that a returned permalink is live.

A transient public 404 is not permission to republish. Diagnose the exact
commit/run first. If the site uses Actions, inspect that run's logs and relevant
workflow, dependency/lockfile or cache changes, not an unrelated successful run.
Use installed CLI help before choosing log-download flags; sanitize escape codes
and secrets before quoting logs. A later successful upstream request does not
prove what an earlier failed build received. Any dependency, cache or deployment
change needs its own authorized scope and verification; this guide grants none.

## Media-only upload, replacement and removal

Upload-only or media-replacement authorization does not authorize a note,
repository commit or deployment. The bundled publisher has no upload-only, delete
or purge command: do not run its publication entrypoint to get a URL. A separately
reviewed adapter must preserve the public package's dedicated-credential/private-
config rules and use only the configured bucket/base URL and approved keys.

For an authorized upload, optimize copies to the effective requested limits and
verify decoded format, extension, MIME, pixel orientation and stripped source
metadata. Record local full SHA-256, byte count and exact bucket/key/URL mapping in
a private manifest. Prefer new content-addressed keys for immutable caching; a
truncated key digest or ETag is not a full-integrity check. Compare stored bytes
and public full GET bytes with the local digest. A public GET failure does not
prove the origin write failed; inspect the exact existing object after any
interruption before deciding whether a retry is safe.

Removal and CDN purge each require separate explicit authorization:

1. Confirm the exact bucket and object keys, their public URLs, ownership and any
   remaining references. Inspect old and replacement objects and prove the old
   and replacement keys are disjoint before deleting anything. Explain effects on
   other notes; deletion permission does not authorize editing those notes.
2. Delete only the approved exact keys through an authorized origin operation.
   Never use wildcard/prefix deletion or empty the bucket as a shortcut. Read back
   origin absence using the authenticated object API; distinguish an absent object
   from denied access, a network failure or an unverified delete response.
3. Origin deletion does not retract a CDN cache. Verify the original URL separately
   without a cache-busting query; a fresh variant says nothing about the URL that
   was shared. Record whether each original URL returns 404/410 or still serves
   the asset; redirects and custom cache keys may need separate diagnosis.
4. Only if explicitly authorized and a supported purge interface is available,
   discover the correct zone and purge only the exact public URLs in scope. R2
   S3 credentials do not imply CDN purge authority. Review query strings,
   redirect destinations and required custom cache-key headers; do not silently
   expand scope when exact-URL purge cannot address a variant.
5. Verify the purge API result and then the original URL response. Never purge an
   entire zone or change cache rules as a shortcut. Without authorization, access
   or supported exact-URL purge, report origin removal separately and say cached
   copies may remain. Even a verified origin deletion and CDN purge cannot recall
   downloaded copies, browser caches, third-party mirrors or screenshots.

Completion reports must distinguish encoded/uploaded, origin removed, purge
requested/accepted and public response verified. Do not promise universal erasure.

## Public configuration and limits

Use the dedicated `PUBLISH_NOTE_R2_ACCESS_KEY_ID` and
`PUBLISH_NOTE_R2_SECRET_ACCESS_KEY` from the protected environment for photo
uploads. The public helper ignores ambient AWS credentials and other credential
providers. Keep no secrets in config or request files, command arguments, logs or
chat. A wiki is not a credential-discovery source for this public workflow. If
these dedicated credentials are missing, stop and request authorized secure setup.
Text-only publication needs no R2 fields or credentials; do not add them as a
prerequisite for a text-only correction.

Retain the private mode-0600 config outside the skill directory. Keep exact body
text in its session text file and all user-controlled paths in session-specific
request JSON; run the fixed request-file command from the main skill. Do not
replace it with interpolated text/image paths or copy a personal wrapper.

For `max_image_bytes` and `max_image_edge`, use a positive request override, then
config, then bundled defaults. These public publisher defaults are already
500000 bytes and 1920px, starting at quality 88 for WebP, unlike the standalone
optimizer's 950000-byte default and JPEG format. Omitted or zero request limits
fall through to config/default in the current publisher; use positive values
rather than treating zero as unlimited. Preserve a site's explicit limits unless
the user authorizes a change; do not impose a different owner's policy or rewrite
configs just to match defaults. Verify actual output against the effective limits.

## Sources and attribution

- Procedure synthesis: Vipul Sharma (vipul-sharma20), Hermes Agent; adapted from
  reviewed publishing-follow-up lessons, without a private publisher or credential
  discovery implementation.
- Public behavior: [publisher](../scripts/publish_note.py), especially
  `resolve_free_path`, `commit_file` and `run`. This helper creates notes; it does
  not provide an arbitrary existing-file update command.
- [GitHub Contents API](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents)
  — read current content and revision SHA before updating the same file. Inspect
  installed CLI help and the site's workflow before selecting version-sensitive
  flags; no deployment provider or recovery command is assumed here.
- [Cloudflare R2 object deletion](https://developers.cloudflare.com/r2/objects/delete-objects/)
  — exact origin-object operations, distinct from CDN caching.
- [Cloudflare single-file purge](https://developers.cloudflare.com/cache/how-to/purge-cache/purge-by-single-file/)
  — exact-URL purge, redirects and custom-cache-key limitations. This procedure
  deliberately does not adopt broader purge alternatives without separate scope.
