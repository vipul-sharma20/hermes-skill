# Actual pixel review and derivative integrity

## Viewing discipline

Generate small, stable-ID-labeled comparison sheets containing the actual
original, actual detail and native-sized thumbnail when all three are required.
A generated sheet is not a viewing event. Record the inspected sheet hash, row,
source ID and original/variant hashes. If a later download changes sheet row
assignments, generate a new immutable sheet/index rather than invalidating old
review references. Avoid giant sheets that downscale native thumbnails globally.

Use `vision_analyze` on local files. Inspect attached browser screenshots directly.
When clipping, texture, source marks or identity plausibility determines a verdict,
open the relevant original/detail or a native-resolution inspection crop. Save
crop coordinates and label it inspection-only; it must not replace an uncropped
production variant. State the resolution actually inspected.

Record concrete visible anatomy, attached/detached context, subject dominance,
framing, focus/exposure, occlusion, original softness, marks and derivative losses.
Don't pretend a source defect was repaired by encoding. Don't invent an alternate
species or disease diagnosis to explain a rejection. A source-flagged condition
can be relevant to suitability without independently diagnosing it.

A strict whole-tree assessment checks crown extremities and base independently.
Passing one cannot compensate for the other. Medium branching or anatomy can
still be valuable when the contract does not require strict whole-tree coverage.

## Transformation and checks

Use current task limits, not inherited byte/edge defaults. Unless authorized
otherwise: contain-resize, no crop/upscale, preserve aspect ratio and visible marks,
apply orientation explicitly, archive metadata before stripping delivery metadata.
Don't force-square discovery previews and then infer natural architecture.

For each derivative, record format, key/path, source ID, SHA256, bytes, width,
height, quality/encoder, variant role, budget, maximum edge and transformations.
Decode the actual bytes and compare these descriptors, including extension/MIME.

For orientation-normalized original dimensions `(ow, oh)` and an uncropped
proportional derivative `(w, h)`, check no upscale and the rounding tolerance:

```text
w <= ow and h <= oh
abs(w * oh - h * ow) <= max(ow, oh)
max(w, h) <= requested maximum edge
actual bytes <= requested byte budget
```

These are structural checks, not a visual pass. Retain encoded dimensions and
orientation separately when source metadata reports display dimensions. Do not
weaken hash/byte checks because an orientation-only dimension check failed.

If an optimizer's coarse geometric step skips an allowed intermediate size,
inspect its actual interface/policy. An authorized isolated, bounded finer search
may help; don't modify a shared helper or cross a safety floor silently. Quality
numbers are encoder-specific, not universal visual equivalence.

Review final detail and native thumbnail after encoding. If bytes change after
approval, re-inspect or establish exact deterministic byte equality. An original
review cannot approve an unseen derivative. Preserve retained delivered assets
when the contract freezes them; audit-local links/descriptors can aid review
without renaming or regenerating the originals.
