# Metadata and destination verification

## Verify the encoded artifact

1. Keep originals unchanged unless replacement was explicitly requested. The public
   helper applies EXIF orientation before metadata removal, converts pixels to RGB
   (flattening transparency onto white), then encodes a still image without passing
   source metadata to the encoder. Encoder settings alone are not verification.
2. Create the explicit `out` parent before running: the helper writes `out` directly
   but creates the directory in `out_dir` mode. Review the JSON request with
   `read_file`; keep user-controlled paths in JSON, not shell interpolation.
3. Reopen every encoded output with Pillow and fully load it. Record the actual
   decoded format, byte size and decoded dimensions against the effective request
   limits. Require WebP bytes for `.webp`, or JPEG bytes for `.jpg` or `.jpeg`.
   Renaming a file is not conversion; preserve the helper's extension mismatch check.
4. When metadata stripping is required, require empty `getexif()` and no source
   `exif`, `xmp`, `XML:com.adobe.xmp` and `icc_profile` payloads in the reopened
   image's info. GPS can live in EXIF or XMP; checking only EXIF tag names is not
   enough. Do not print private source metadata into the response or logs.
5. For strict WebP verification, walk the length-delimited RIFF chunks, accounting
   for padding and rejecting malformed lengths. Require no `EXIF`, `XMP ` and `ICCP`
   chunks; a substring search of compressed bytes is not a chunk parser. JPEG needs
   its corresponding format-aware metadata checks, not WebP chunk assumptions.
6. Use `vision_analyze` to visually inspect orientation and appearance, especially
   a portrait phone photo whose stored pixels were landscape. An empty orientation
   tag does not prove the pixels were rotated correctly. Check color changes too:
   omitting an ICC profile is not color-managed profile conversion.

Report the measured output format, bytes, dimensions and metadata/orientation
checks for each input. If a check fails, stop delivery and report the limitation;
do not silently relax the byte budget or claim that all metadata is gone.
Container/encoder fields may remain. Metadata stripping does not anonymize visible
content, a filename or an object key. Document attachment delivery preserves the
generated artifact better than a platform-recompressed image preview.

## Upload-only boundary

An upload-only request does not authorize a blog post, repository commit, deployment
or deletion. This package has no uploader. Use only a separately reviewed upload
adapter and an approved destination; never invoke a publishing entrypoint merely
to obtain an image URL. Preserve the adapter's dedicated credential and private
config rules; keep credentials out of commands, logs and chat.

Before an authorized upload, record the exact destination bucket/key, public URL,
format, bytes and full SHA-256 of each optimized copy in a private manifest. Use
content-addressed keys when supported; never silently overwrite an unrelated asset.
Match extension, decoded bytes and upload Content-Type (`image/webp` or
`image/jpeg`). Verify the stored object separately from a public full GET, then
compare the public response bytes and full SHA-256 with the local artifact. A HEAD
response, ETag or truncated digest in a filename is not full byte-integrity proof.

A public GET failure does not prove an origin write failed. Diagnose authentication,
CDN/WAF response and any documented User-Agent handling; do not bypass access
controls. After an interrupted or ambiguous upload, inspect the exact existing
object before retrying. Report encoding, origin storage and public delivery as
separate outcomes; do not claim successful publication from storage alone.

## Sources and attribution

- Procedure synthesis: Vipul Sharma (vipul-sharma20), Hermes Agent; adapted from
  reviewed image-verification lessons, without copying a private implementation.
- Public behavior: [bundled optimizer](../scripts/image_optimizer.py), especially
  `to_rgb`, `encode_jpeg`, `encode_webp` and `run`. Its standalone defaults remain
  950000 bytes, 1920px and JPEG; use the user's effective constraints, not another
  site's image policy.
- [Pillow image formats](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html)
  — content-based decoding and JPEG/WebP metadata fields. Check the installed,
  bounded Pillow version when depending on a version-specific metadata API.
