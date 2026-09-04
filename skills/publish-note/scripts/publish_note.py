#!/usr/bin/env python3
"""Publish one text-or-photo microblog note through GitHub and R2."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import NamedTuple
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from image_optimizer import OptimizeError, optimize_image  # noqa: E402

TAG_PATTERN = re.compile(r"(?:^|\s)#([\w-]+)", re.UNICODE)
TRAILING_TAGS_PATTERN = re.compile(r"(?:\s*#[\w-]+)+\s*$", re.UNICODE)
SUFFIX_ALPHABET = "abcdefghijklmnopqrstuvwxyz"


class PublishError(RuntimeError):
    """Expected publication failure with an actionable message."""


class DateParts(NamedTuple):
    year: str
    month: str
    day: str
    date: str
    time: str
    frontmatter: str


class PreparedImage(NamedTuple):
    key: str
    url: str
    data: bytes
    width: int
    height: int
    quality: int


def load_config(path: Path, *, require_images: bool = False) -> dict:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PublishError(f"Configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise PublishError(f"Configuration is not valid JSON: {exc}") from exc
    if not isinstance(config, dict):
        raise PublishError("Configuration must be a JSON object")

    required = ["repo", "branch", "site_url"]
    if require_images:
        required.extend(["image_base_url", "r2_account_id", "bucket"])
    missing = [key for key in required if not str(config.get(key, "")).strip()]
    if missing:
        raise PublishError(f"Configuration is missing: {', '.join(missing)}")
    if any("REPLACE_WITH" in str(value) for value in config.values()):
        raise PublishError("Configuration still contains an unreplaced placeholder")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(config["repo"])):
        raise PublishError("repo must use owner/repository format")
    url_keys = ["site_url"]
    if require_images:
        url_keys.append("image_base_url")
    for key in url_keys:
        parsed = urlparse(str(config[key]))
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise PublishError(f"{key} must be an absolute HTTP(S) URL")
    content_directory = PurePosixPath(str(config.get("content_directory", "content/micro")))
    if content_directory.is_absolute() or ".." in content_directory.parts:
        raise PublishError("content_directory must be a safe repository-relative path")
    try:
        ZoneInfo(str(config.get("timezone", "UTC")))
    except ZoneInfoNotFoundError as exc:
        raise PublishError("timezone must be a valid IANA timezone name") from exc
    return config


def site_date_parts(
    timezone_name: str,
    when: datetime | None = None,
) -> DateParts:
    moment = (when or datetime.now(timezone.utc)).astimezone(ZoneInfo(timezone_name))
    return DateParts(
        year=moment.strftime("%Y"),
        month=moment.strftime("%m"),
        day=moment.strftime("%d"),
        date=moment.strftime("%Y-%m-%d"),
        time=moment.strftime("%H%M"),
        frontmatter=moment.isoformat(timespec="seconds"),
    )


def parse_note_text(raw: str | None) -> tuple[str, list[str], bool]:
    text = (raw or "").replace("\r\n", "\n").strip()
    draft = bool(re.match(r"^/draft\b", text, re.IGNORECASE))
    if draft:
        text = re.sub(r"^/draft\b[ \t]*", "", text, flags=re.IGNORECASE)
    tags: list[str] = []
    for match in TAG_PATTERN.finditer(text):
        tag = match.group(1).lower()
        if tag not in tags:
            tags.append(tag)
    body = TRAILING_TAGS_PATTERN.sub("", text).strip()
    return body, tags, draft


def note_slug(parts: DateParts, suffix: str = "") -> str:
    return f"{parts.time}{suffix}"


def note_file_path(
    parts: DateParts,
    content_directory: str,
    suffix: str = "",
) -> str:
    base = str(PurePosixPath(content_directory)).rstrip("/")
    return f"{base}/{parts.date}-{note_slug(parts, suffix)}.md"


def note_permalink(site_url: str, parts: DateParts, suffix: str = "") -> str:
    return (
        f"{site_url.rstrip('/')}/micro/{parts.year}/{parts.month}/{parts.day}/"
        f"{note_slug(parts, suffix)}/"
    )


def image_object_key(prefix: str, parts: DateParts, suffix: str, digest: str) -> str:
    clean_prefix = prefix.strip("/") or "micro"
    return f"{clean_prefix}/{parts.year}/{parts.date}-{note_slug(parts, suffix)}/{digest[:16]}.jpg"


def build_note_markdown(
    frontmatter_date: str,
    tags: list[str],
    images: list[PreparedImage],
    draft: bool,
    body: str,
) -> str:
    lines = ["---", f"date: {frontmatter_date}"]
    if tags:
        serialized_tags = ", ".join(json.dumps(tag, ensure_ascii=False) for tag in tags)
        lines.append(f"tags: [{serialized_tags}]")
    if draft:
        lines.append("draft: true")
    if images:
        lines.append("images:")
        for image in images:
            lines.extend(
                [
                    f"  - src: {image.url}",
                    '    alt: ""',
                    f"    width: {image.width}",
                    f"    height: {image.height}",
                ]
            )
    lines.extend(["---", "", body, ""])
    return "\n".join(lines)


def resolve_gh_binary() -> str:
    found = shutil.which("gh")
    if not found:
        raise PublishError("gh CLI was not found on PATH")
    return found


def gh_json(args: list[str]) -> dict | None:
    result = subprocess.run(
        [resolve_gh_binary(), "api", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        combined = f"{result.stdout}\n{result.stderr}"
        if "404" in combined or "Not Found" in combined:
            return None
        raise PublishError(f"gh api failed: {result.stderr.strip() or combined.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def remote_file_exists(repo: str, branch: str, path: str) -> bool:
    return gh_json([f"/repos/{repo}/contents/{path}?ref={branch}"]) is not None


def resolve_free_path(
    repo: str,
    branch: str,
    parts: DateParts,
    content_directory: str,
) -> tuple[str, str]:
    for suffix in ["", *SUFFIX_ALPHABET]:
        path = note_file_path(parts, content_directory, suffix)
        if not remote_file_exists(repo, branch, path):
            return path, suffix
    raise PublishError("too many notes in the same minute")


def commit_file(repo: str, branch: str, path: str, markdown: str, message: str) -> None:
    encoded = base64.b64encode(markdown.encode("utf-8")).decode("ascii")
    result = gh_json(
        [
            "--method",
            "PUT",
            f"/repos/{repo}/contents/{path}",
            "-f",
            f"message={message}",
            "-f",
            f"content={encoded}",
            "-f",
            f"branch={branch}",
        ]
    )
    if not result or not result.get("content", {}).get("html_url"):
        raise PublishError("GitHub did not confirm the note commit")


def r2_client(account_id: str):
    try:
        import boto3
        from botocore.credentials import EnvProvider
    except ImportError as exc:
        raise PublishError("boto3 is required when publishing images") from exc

    provider = EnvProvider(
        mapping={
            "access_key": "PUBLISH_NOTE_R2_ACCESS_KEY_ID",
            "secret_key": "PUBLISH_NOTE_R2_SECRET_ACCESS_KEY",  # pragma: allowlist secret -- variable name only
            "token": "PUBLISH_NOTE_R2_SESSION_TOKEN",
        }
    )
    credentials = provider.load()
    if credentials is None:
        raise PublishError(
            "dedicated R2 credentials are missing; configure "
            "PUBLISH_NOTE_R2_ACCESS_KEY_ID and PUBLISH_NOTE_R2_SECRET_ACCESS_KEY"
        )
    frozen = credentials.get_frozen_credentials()
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=frozen.access_key,
        aws_secret_access_key=frozen.secret_key,
        aws_session_token=frozen.token,
        region_name="auto",
    )


def prepare_images(
    paths: list[Path],
    *,
    prefix: str,
    parts: DateParts,
    suffix: str,
    image_base_url: str,
    max_image_bytes: int,
    max_image_edge: int,
) -> list[PreparedImage]:
    prepared: list[PreparedImage] = []
    seen: set[str] = set()
    for path in paths:
        if not path.is_file():
            raise PublishError(f"Image does not exist: {path}")
        encoded, width, height, quality = optimize_image(
            path,
            max_bytes=max_image_bytes,
            max_edge=max_image_edge,
        )
        digest = hashlib.sha256(encoded).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        key = image_object_key(prefix, parts, suffix, digest)
        prepared.append(
            PreparedImage(
                key=key,
                url=f"{image_base_url.rstrip('/')}/{key}",
                data=encoded,
                width=width,
                height=height,
                quality=quality,
            )
        )
    return prepared


def upload_images(client, bucket: str, images: list[PreparedImage]) -> None:
    for image in images:
        client.put_object(
            Bucket=bucket,
            Key=image.key,
            Body=image.data,
            ContentType="image/jpeg",
            ContentDisposition="inline",
            CacheControl="public, max-age=31536000, immutable",
            Metadata={"sha256": image.key.rsplit("/", 1)[-1].split(".")[0]},
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, help="JSON request file for shell-safe invocation")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--text", default="", help="Note text for direct CLI use")
    parser.add_argument("--text-file", type=Path, help="Read exact note text from a file")
    parser.add_argument("--image", action="append", default=[], dest="images")
    parser.add_argument("--draft", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-image-bytes", type=int)
    parser.add_argument("--max-image-edge", type=int)
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.request:
        if args.config or args.text or args.text_file or args.images or args.draft or args.dry_run:
            raise PublishError("--request cannot be combined with publication arguments")
        try:
            request = json.loads(args.request.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise PublishError(f"Could not load request file: {exc}") from exc
        if not isinstance(request, dict) or not request.get("config"):
            raise PublishError("request must contain a config path")
        args.config = Path(str(request["config"]))
        args.text_file = Path(str(request["text_file"])) if request.get("text_file") else None
        args.images = [str(value) for value in request.get("images", [])]
        args.draft = bool(request.get("draft", False))
        args.dry_run = bool(request.get("dry_run", False))
        args.max_image_bytes = request.get("max_image_bytes")
        args.max_image_edge = request.get("max_image_edge")
    if args.config is None:
        raise PublishError("--config or --request is required")
    if args.text and args.text_file:
        raise PublishError("use either --text or --text-file, not both")
    if args.text_file:
        try:
            note_text = args.text_file.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise PublishError(f"Note text file not found: {args.text_file}") from exc
    else:
        note_text = args.text

    image_paths = [Path(value).expanduser() for value in args.images]
    config = load_config(args.config, require_images=bool(image_paths))
    body, tags, draft_from_text = parse_note_text(note_text)
    draft = draft_from_text or args.draft
    if not body and not image_paths:
        raise PublishError("Nothing to publish: no text and no images")

    parts = site_date_parts(str(config.get("timezone", "UTC")))
    content_directory = str(config.get("content_directory", "content/micro"))
    if args.dry_run:
        path, suffix = note_file_path(parts, content_directory), ""
    else:
        path, suffix = resolve_free_path(
            str(config["repo"]),
            str(config["branch"]),
            parts,
            content_directory,
        )

    images = []
    if image_paths:
        images = prepare_images(
            image_paths,
            prefix=str(config.get("key_prefix", "micro")),
            parts=parts,
            suffix=suffix,
            image_base_url=str(config["image_base_url"]),
            max_image_bytes=args.max_image_bytes
            or int(config.get("max_image_bytes", 950_000)),
            max_image_edge=args.max_image_edge
            or int(config.get("max_image_edge", 1_920)),
        )
    markdown = build_note_markdown(parts.frontmatter, tags, images, draft, body)
    if args.dry_run:
        print(f"--- would commit {path}", file=sys.stderr)
        print(markdown)
        return 0

    if images:
        upload_images(r2_client(str(config["r2_account_id"])), str(config["bucket"]), images)
    commit_file(
        str(config["repo"]),
        str(config["branch"]),
        path,
        markdown,
        f"note: {parts.date} {parts.time}",
    )

    edit_url = (
        f"https://github.com/{config['repo']}/edit/{config['branch']}/{path}"
    )
    if draft:
        print(f"Saved as draft.\n{edit_url}")
        return 0
    lines = [note_permalink(str(config["site_url"]), parts, suffix)]
    if images:
        lines.append(f"{len(images)} photo{'' if len(images) == 1 else 's'} uploaded")
    lines.extend(["publication triggered", edit_url])
    print("\n".join(lines))
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except (PublishError, OptimizeError) as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
