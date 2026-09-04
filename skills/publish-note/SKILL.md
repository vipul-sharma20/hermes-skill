---
name: publish-note
description: "Publish microblog notes through GitHub and Cloudflare R2."
version: 1.0.1
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux, macos]
required_environment_variables:
  - name: PUBLISH_NOTE_R2_ACCESS_KEY_ID
    prompt: Dedicated Cloudflare R2 access key ID
    help: Create an R2 token restricted to the target bucket.
    required_for: photo uploads
    optional: true
  - name: PUBLISH_NOTE_R2_SECRET_ACCESS_KEY
    prompt: Dedicated Cloudflare R2 secret access key
    help: Use the secret paired with the dedicated R2 access key ID.
    required_for: photo uploads
    optional: true
metadata:
  hermes:
    tags: [Blog, Microblog, GitHub, Cloudflare-R2, Photos]
    related_skills: [optimize-image]
---

# Publish Note

Turn a chat message and optional images into one microblog Markdown file, upload optimized images to Cloudflare R2, and commit the note through GitHub. The workflow is deterministic after the user confirms the exact text and attachments.

## When to Use

- The user asks to publish a short note or photo post to a GitHub-backed microblog.
- The site stores Markdown notes under a date-based `content/micro` path.
- Optional images should be optimized and stored in Cloudflare R2.

Don't use for long-form posts, sites with an incompatible content model, or publication when the user has not clearly separated their instruction from the public text.

## Prerequisites

- `gh` authenticated with write access to the configured repository.
- `uv` available on `PATH`.
- A private JSON config based on `templates/config.example.json` for text-only notes or `templates/config.images.example.json` for photo notes.
- For photo posts, optional `PUBLISH_NOTE_R2_ACCESS_KEY_ID` and `PUBLISH_NOTE_R2_SECRET_ACCESS_KEY` values configured securely for the target R2 bucket.

The R2 account ID, bucket, repository, and URLs belong in the local config. Dedicated secret access keys belong only in Hermes's secure environment, never in the config, skill, request file, command line, or chat. Text-only publication requires no R2 fields or credentials.

## Setup

### 1. Confirm GitHub access

```python
terminal(command="gh auth status", timeout=60)
```

Done when `gh` identifies an account with write access to the target content repository.

### 2. Create a private config

For text-only publication, start from `templates/config.example.json`. For photo publication, start from `templates/config.images.example.json` and replace every image/R2 placeholder. Save the selected config outside the skill directory, such as:

```text
${HERMES_HOME}/publish-note/config.json
```

Set mode `0600`. The config contains deployment metadata but no secret access key. Done when no `REPLACE_WITH` value remains and only the owner can read it.

### 3. Test with a shell-safe dry run

Write the exact note body with `write_file` to:

```text
${HERMES_HOME}/cache/publish-note-body-${HERMES_SESSION_ID}.txt
```

Start from `templates/request.example.json` and use `write_file` to create a request at `${HERMES_HOME}/cache/publish-note-${HERMES_SESSION_ID}.json`. Put the fixed config path, note-text path, and any user-controlled image paths inside that JSON. Set `dry_run` to `true`.

Run only the fixed request path; never interpolate note text or image paths into the command:

```python
terminal(
    command='uv run --with "boto3>=1.40,<2" --with "pillow>=11,<13" --with "pillow-heif>=1,<2" "${HERMES_SKILL_DIR}/scripts/publish_note.py" --request "${HERMES_HOME:-$HOME/.hermes}/cache/publish-note-${HERMES_SESSION_ID}.json"',
    timeout=180,
)
```

Inspect the generated path, frontmatter, tags, body, and image metadata before enabling real publication. Done when the output matches the site's content schema and the body matches the intended text after documented whitespace trimming and trailing-tag extraction.

## Procedure

### 1. Separate instruction from public content

- Quoted text is the body exactly as quoted.
- After a colon, everything following it is the body when the message uses an instruction prefix.
- Never rewrite grammar, expand abbreviations, add a title, or invent hashtags.
- Leave user-provided hashtags in the text; trailing tags are lifted into frontmatter.
- Ask when the publication text is ambiguous.

Done when the exact public body and ordered attachment list are explicit.

### 2. Choose draft or publication

Set `draft` in the request only when requested. Set `dry_run` whenever the user asks for a preview or the configuration changed. Done when publication intent is unambiguous.

### 3. Write content and request files

Use `write_file` for the exact public body and for a JSON request based on `templates/request.example.json`. Preserve the requested image order in the `images` array. JSON-encode every path. Never place user-controlled text or paths in a terminal command. Done when the request points to the fixed private config and session text file.

### 4. Run the publisher

```python
terminal(
    command='uv run --with "boto3>=1.40,<2" --with "pillow>=11,<13" --with "pillow-heif>=1,<2" "${HERMES_SKILL_DIR}/scripts/publish_note.py" --request "${HERMES_HOME:-$HOME/.hermes}/cache/publish-note-${HERMES_SESSION_ID}.json"',
    timeout=300,
)
```

Done when the script prints a permalink or draft edit URL.

### 5. Report the result once

Relay the permalink and edit URL without claiming that an asynchronous site build has completed. On `Failed:`, report the failure and stop. Never retry automatically: a successful commit followed by a lost response can otherwise create a duplicate timestamped note.

## Behavior

The publisher in `scripts/publish_note.py` uses the bundled `scripts/image_optimizer.py` helper, so the skill does not depend on a machine-local library.

- Corrects EXIF orientation and converts images to JPEG.
- Flattens transparency onto white.
- Steps JPEG quality down before reducing dimensions.
- Deduplicates identical images within one post.
- Uploads photos to R2 before committing Markdown.
- Uses `gh api` for repository reads and commits.
- Adds a letter suffix when a note already exists for the same minute.

## Pitfalls

- Everything in the body becomes public; do not infer or embellish text.
- JPEG conversion removes transparency and animation.
- Dedicated `PUBLISH_NOTE_R2_*` variables must contain bucket-restricted R2 credentials. The helper ignores standard AWS variables and other ambient credential sources.
- Never interpolate note text or image paths into a shell command; pass them through the text and request files.
- The config template is intentionally invalid until all placeholders are replaced.
- A failed GitHub commit after image upload can leave unreferenced R2 objects.
- The helper launches the authenticated `gh` executable; review repository and branch values before running.
- The default permalink layout assumes `/micro/YYYY/MM/DD/HHMM/`.

## Verification

- [ ] Dry-run Markdown matches the site's expected schema.
- [ ] No credentials or private config are inside the skill directory.
- [ ] GitHub repository and branch are correct.
- [ ] Every image URL uses the configured public image hostname.
- [ ] Published note can be read back from GitHub at the returned edit URL.
- [ ] A failure is not retried until GitHub is checked for an existing note.
