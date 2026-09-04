import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from PIL import Image

MODULE = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "optimize-image"
    / "scripts"
    / "image_optimizer.py"
)
spec = importlib.util.spec_from_file_location("published_image_optimizer", MODULE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class OptimizeImageTest(unittest.TestCase):
    def test_rgba_image_is_encoded_under_budget(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "input.png"
            Image.new("RGBA", (640, 480), (100, 150, 200, 128)).save(source)

            encoded, width, height, quality = module.optimize_image(
                source,
                max_bytes=100_000,
                max_edge=320,
            )

            self.assertLessEqual(len(encoded), 100_000)
            self.assertEqual((width, height), (320, 240))
            self.assertGreaterEqual(quality, module.MIN_QUALITY)
            with Image.open(io.BytesIO(encoded)) as result:
                self.assertEqual(result.mode, "RGB")
                self.assertEqual(result.format, "JPEG")

    def test_rejects_nonpositive_size_budget(self):
        with self.assertRaisesRegex(module.OptimizeError, "must be positive"):
            module.optimize_image(Path("unused.png"), max_bytes=0)

    def test_same_stem_inputs_cannot_overwrite_each_other(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "one" / "photo.png"
            second = root / "two" / "photo.png"
            output = root / "output"
            first.parent.mkdir()
            second.parent.mkdir()
            Image.new("RGB", (32, 32), "red").save(first)
            Image.new("RGB", (32, 32), "blue").save(second)

            with patch.object(
                sys,
                "argv",
                ["image_optimizer.py", str(first), str(second), "--out-dir", str(output)],
            ):
                with self.assertRaisesRegex(module.OptimizeError, "same output"):
                    module.run()

    def test_resize_step_preserves_aspect_ratio(self):
        resized = module.next_size((400, 800))

        self.assertEqual(resized, (340, 680))
        self.assertEqual(resized[0] / resized[1], 400 / 800)

    def test_resize_step_refuses_to_cross_dimension_floor(self):
        with self.assertRaisesRegex(module.OptimizeError, "safety floor"):
            module.next_size((340, 680))

    def test_request_file_treats_shell_metacharacters_as_literal_path_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "photo $(touch SHOULD_NOT_EXIST).png"
            destination = root / "output.jpg"
            request = root / "request.json"
            Image.new("RGB", (32, 32), "green").save(source)
            request.write_text(
                json.dumps({"sources": [str(source)], "out": str(destination)}),
                encoding="utf-8",
            )

            with patch.object(sys, "argv", ["image_optimizer.py", "--request", str(request)]):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    code = module.run()

            self.assertEqual(code, 0)
            self.assertTrue(destination.exists())
            self.assertFalse((root / "SHOULD_NOT_EXIST").exists())


if __name__ == "__main__":
    unittest.main()
