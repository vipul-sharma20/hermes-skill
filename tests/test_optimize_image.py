import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
