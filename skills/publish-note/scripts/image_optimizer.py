#!/usr/bin/env python3
"""Shrink images to a byte budget while preserving useful quality."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass


DEFAULT_MAX_BYTES = 950_000
DEFAULT_MAX_EDGE = 1_920
DEFAULT_QUALITY = 88
MIN_QUALITY = 45
MIN_EDGE = 320
SUPPORTED_EXTENSIONS = {
    ".avif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


class OptimizeError(RuntimeError):
    """Expected image-processing failure with an actionable message."""


def to_rgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA"} or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def fit_max_edge(image: Image.Image, max_edge: int) -> Image.Image:
    if max(image.size) <= max_edge:
        return image.copy()
    resized = image.copy()
    resized.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
    return resized


def encode_jpeg(image: Image.Image, quality: int) -> bytes:
    output = io.BytesIO()
    image.save(
        output,
        format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
    )
    return output.getvalue()


def quality_steps(start_quality: int) -> list[int]:
    steps = list(range(start_quality, MIN_QUALITY, -5))
    if not steps or steps[-1] != MIN_QUALITY:
        steps.append(MIN_QUALITY)
    return steps


def optimize_image(
    source: Path,
    max_bytes: int = DEFAULT_MAX_BYTES,
    max_edge: int = DEFAULT_MAX_EDGE,
    start_quality: int = DEFAULT_QUALITY,
) -> tuple[bytes, int, int, int]:
    """Encode source as a JPEG and return bytes, width, height, and quality."""
    if max_bytes <= 0:
        raise OptimizeError("max_bytes must be positive")
    if max_edge < MIN_EDGE:
        raise OptimizeError(f"max_edge must be at least {MIN_EDGE}")
    if not MIN_QUALITY <= start_quality <= 95:
        raise OptimizeError(f"quality must be between {MIN_QUALITY} and 95")

    try:
        with Image.open(source) as opened:
            working = fit_max_edge(to_rgb(opened), max_edge)
    except UnidentifiedImageError as exc:
        raise OptimizeError(
            f"Unsupported or invalid image: {source}. Install pillow-heif for "
            "HEIC or HEIF input."
        ) from exc
    except OSError as exc:
        raise OptimizeError(f"Could not decode image {source}: {exc}") from exc

    while True:
        for quality in quality_steps(start_quality):
            encoded = encode_jpeg(working, quality)
            if len(encoded) <= max_bytes:
                return encoded, working.width, working.height, quality

        if min(working.size) <= MIN_EDGE:
            raise OptimizeError(
                f"Could not reduce {source} below {max_bytes} bytes without "
                f"shrinking below {MIN_EDGE}px"
            )

        new_size = (
            max(MIN_EDGE, int(working.width * 0.85)),
            max(MIN_EDGE, int(working.height * 0.85)),
        )
        if new_size == working.size:
            raise OptimizeError(f"Optimizer stopped making progress for {source}")
        working = working.resize(new_size, Image.Resampling.LANCZOS)
        start_quality = min(start_quality, 82)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path, help="Input image files")
    parser.add_argument("--out", type=Path, help="Output path for one input")
    parser.add_argument("--out-dir", type=Path, help="Output directory for one or more inputs")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--max-edge", type=int, default=DEFAULT_MAX_EDGE)
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY)
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    if args.out and len(args.sources) > 1:
        raise OptimizeError("--out takes one input; use --out-dir for several")
    if not args.out and not args.out_dir:
        raise OptimizeError("pass --out or --out-dir")
    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    for source in args.sources:
        if not source.is_file():
            raise OptimizeError(f"Not a file: {source}")
        encoded, width, height, quality = optimize_image(
            source,
            max_bytes=args.max_bytes,
            max_edge=args.max_edge,
            start_quality=args.quality,
        )
        destination = args.out or (args.out_dir / f"{source.stem}.jpg")
        destination.write_bytes(encoded)
        before = source.stat().st_size
        print(
            f"{source.name}: {before / 1024:.0f} KiB → {len(encoded) / 1024:.0f} KiB "
            f"({width}x{height}, q{quality})",
            file=sys.stderr,
        )
        print(destination.resolve())
    return 0


def main() -> None:
    try:
        raise SystemExit(run())
    except OptimizeError as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
