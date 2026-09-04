import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

MODULE = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "indian-railways-pnr-monitor"
    / "scripts"
    / "pnr_watch.py"
)
spec = importlib.util.spec_from_file_location("published_pnr_watch", MODULE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

SAMPLE_HTML = """
<div id="status-chart">
  <p>CURRENT STATUS</p><p class="pnr-bold-txt">W/L</p>
  <p>CHART STATUS</p><p class="chart-status-txt">NOT PREPARED</p>
</div>
<div class="train-info"><span>TRAIN NAME :</span>
  <a href="/time-table/example"><span>12345 <span>&#8210; Example Express</span></span></a>
</div>
<div class="train-route">
  <div><p>FROM</p><p class="pnr-bold-txt">ORIGIN | ORG</p></div>
  <div><p>TO</p><p class="pnr-bold-txt">DESTINATION | DST</p></div>
</div>
<div class="boarding-detls">
  <div><p>DAY OF BOARDING</p><p class="pnr-bold-txt">31-12-2099</p></div>
  <div><p>CLASS</p><p class="pnr-bold-txt">CC</p></div>
</div>
<ul class="pasListUL">
  <li class="PNRPasList">
    <p class="pnr-bold-txt statusType">WL/10</p>
    <p class="pnr-bold-txt statusType">4 Waitlist</p>
  </li>
</ul>
"""


class PnrParserTest(unittest.TestCase):
    def test_parses_one_passenger_from_combined_refresh_and_page(self):
        result = module.parse_pnr_html(SAMPLE_HTML + SAMPLE_HTML)

        self.assertEqual(result["train_number"], "12345")
        self.assertEqual(result["passengers"], [
            {"number": 1, "booking": "WL/10", "current": "WL/4"}
        ])


class WatchRunTest(unittest.TestCase):
    def test_baseline_prints_masked_alert_and_persists_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "watch.json"
            config_path.write_text(
                json.dumps({"pnr": "1234567890", "label": "Example trip"}),
                encoding="utf-8",
            )
            status = module.parse_pnr_html(SAMPLE_HTML)
            output = io.StringIO()

            with redirect_stdout(output):
                event = module.run_watch(config_path, fetcher=lambda _pnr: status)

            self.assertEqual(event, "baseline")
            self.assertIn("PNR ending **7890**", output.getvalue())
            self.assertIn("Passenger 1", output.getvalue())
            self.assertNotIn("1234567890", output.getvalue())
            self.assertTrue(config_path.with_suffix(".state.json").exists())

    def test_unchanged_run_is_silent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "watch.json"
            config_path.write_text(
                json.dumps({"pnr": "1234567890", "label": "Example trip"}),
                encoding="utf-8",
            )
            status = module.parse_pnr_html(SAMPLE_HTML)
            with redirect_stdout(io.StringIO()):
                module.run_watch(config_path, fetcher=lambda _pnr: status)
            output = io.StringIO()

            with redirect_stdout(output):
                event = module.run_watch(
                    config_path,
                    fetcher=lambda _pnr: module.parse_pnr_html(SAMPLE_HTML),
                )

            self.assertEqual(event, "no_change")
            self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
