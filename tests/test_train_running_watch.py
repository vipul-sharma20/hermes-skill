from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MODULE = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "indian-railways-running-status-monitor"
    / "scripts"
    / "train_running_watch.py"
)
spec = importlib.util.spec_from_file_location("published_train_running_watch", MODULE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

IST = ZoneInfo("Asia/Kolkata")
# All-zero digits deliberately generate a fixture that cannot name a live train.
TRAIN_NUMBER = "0" * 5
JOURNEY_DATE = "2099-01-02"


def sample_payload(**overrides):
    payload = {
        "success": True,
        "train_number": TRAIN_NUMBER,
        "train_name": "Example Express",
        "train_start_date": JOURNEY_DATE,
        "source": "SRC",
        "source_stn_name": "ORIGIN",
        "destination": "DST",
        "dest_stn_name": "DESTINATION",
        "std": f"{JOURNEY_DATE} 06:00",
        "journey_time": 360,
        "current_station_code": "MID",
        "current_station_name": "MIDPOINT",
        "status": "T",
        "delay": 5,
        "eta": "09:05",
        "etd": "09:10",
        "status_as_of": "As of 2 mins ago",
        "update_time": f"{JOURNEY_DATE} 09:05:00 +0530",
        "distance_from_source": 150,
        "total_distance": 400,
        "platform_number": 2,
        "at_dstn": False,
        "title": None,
        "new_message": None,
        "data_from": "mntes",
        "current_location_info": [
            {
                "type": 1,
                "message": "Crossed MIDPOINT at 09:05",
                "hint": "DELAY 5 MIN",
            }
        ],
        "upcoming_stations": [
            {"station_code": "", "station_name": ""},
            {
                "station_code": "NXT",
                "station_name": "NEXT STOP",
                "eta": "10:15",
                "arrival_delay": 5,
                "platform_number": 3,
                "distance_from_source": 250,
            },
        ],
    }
    payload.update(overrides)
    return payload


def write_config(root: Path) -> Path:
    config_path = root / "watch.json"
    config_path.write_text(
        json.dumps(
            {
                "train_number": TRAIN_NUMBER,
                "journey_date": JOURNEY_DATE,
                "source": "SRC",
                "destination": "DST",
                "monitor_from": f"{JOURNEY_DATE}T04:00:00+05:30",
                "monitor_until": f"{JOURNEY_DATE}T18:00:00+05:30",
                "label": "Example journey",
                "mention": "",
            }
        ),
        encoding="utf-8",
    )
    return config_path


class NormalizeStatusTest(unittest.TestCase):
    def test_normalizes_live_payload_and_skips_placeholder_station(self):
        status = module.normalize_status(sample_payload())

        self.assertEqual(status["train_number"], TRAIN_NUMBER)
        self.assertEqual(status["location_message"], "Crossed MIDPOINT at 09:05")
        self.assertEqual(status["next_station"]["code"], "NXT")
        self.assertEqual(status["next_station"]["eta"], "10:15")
        self.assertFalse(status["at_destination"])


class FetchStatusTest(unittest.TestCase):
    def test_targets_configured_instance_with_relative_start_day(self):
        requested_urls = []
        body = json.dumps(sample_payload()).encode("utf-8")

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self):
                return body

        def fake_urlopen(request, timeout):
            requested_urls.append(request.full_url)
            self.assertEqual(timeout, 45)
            return Response()

        status = module.fetch_status(
            {"train_number": TRAIN_NUMBER, "journey_date": JOURNEY_DATE},
            datetime(2099, 1, 1, 12, 0, tzinfo=IST),
            urlopen=fake_urlopen,
            attempts=1,
        )

        self.assertIn(f"/{TRAIN_NUMBER}/-1.json", requested_urls[0])
        self.assertIn("start_day=-1", requested_urls[0])
        self.assertNotIn("authentication_token", requested_urls[0])
        self.assertEqual(status["train_start_date"], JOURNEY_DATE)


class AlertMessageTest(unittest.TestCase):
    def test_provider_fields_cannot_inject_markdown_links_mentions_or_lines(self):
        attack = "@everyone **bold** [click](https://evil.example)\n> injected\x00"
        status = module.normalize_status(sample_payload())
        status.update(
            {
                "train_number": attack,
                "train_name": attack,
                "train_start_date": attack,
                "source_name": attack,
                "destination_name": attack,
                "location_message": attack,
                "updated_at": attack,
                "next_station": {
                    "name": attack,
                    "eta": attack,
                    "platform": 3,
                },
            }
        )

        message = module.build_alert_message(
            status,
            config={"label": "Example journey", "mention": ""},
            event="change",
        )

        self.assertNotIn("@everyone", message)
        self.assertNotIn("**bold**", message)
        self.assertNotIn("[click](", message)
        self.assertNotIn("https://evil.example", message)
        self.assertNotIn("\n> injected", message)
        self.assertNotIn("\x00", message)
        self.assertEqual(message.count("https://"), 1)
        self.assertIn("https://www.railyatri.in/live-train-status/", message)


class RunWatchTest(unittest.TestCase):
    def test_outside_window_is_silent_and_does_not_fetch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            output = io.StringIO()

            with redirect_stdout(output):
                event = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 1, 12, 0, tzinfo=IST),
                    fetcher=lambda *_: self.fail("outside-window fetch"),
                )

            self.assertEqual(event, "inactive")
            self.assertEqual(output.getvalue(), "")
            self.assertFalse(config_path.with_suffix(".state.json").exists())

    def test_baseline_prints_once_and_unchanged_refresh_is_silent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            status = module.normalize_status(sample_payload())
            first_output = io.StringIO()
            second_output = io.StringIO()

            with redirect_stdout(first_output):
                first = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 5, 0, tzinfo=IST),
                    fetcher=lambda *_: status,
                )
            refreshed = dict(
                status,
                status_as_of="As of 1 min ago",
                updated_at=f"{JOURNEY_DATE} 09:06:00 +0530",
            )
            with redirect_stdout(second_output):
                second = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 5, 10, tzinfo=IST),
                    fetcher=lambda *_: refreshed,
                )

            self.assertEqual(first, "baseline")
            self.assertEqual(second, "no_change")
            self.assertIn("Running-status monitor started", first_output.getvalue())
            self.assertEqual(second_output.getvalue(), "")
            state_path = config_path.with_suffix(".state.json")
            self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)

    def test_arrival_marks_watch_finished_and_stops_future_fetches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            moving = module.normalize_status(sample_payload())
            arrived = module.normalize_status(
                sample_payload(
                    current_station_code="DST",
                    current_station_name="DESTINATION",
                    status="A",
                    at_dstn=True,
                    title="Train Run Complete",
                    new_message="Train has reached destination.",
                    upcoming_stations=[],
                )
            )
            with redirect_stdout(io.StringIO()):
                module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 8, 0, tzinfo=IST),
                    fetcher=lambda *_: moving,
                )
            arrival_output = io.StringIO()
            with redirect_stdout(arrival_output):
                arrival = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 12, 0, tzinfo=IST),
                    fetcher=lambda *_: arrived,
                )
                finished = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 12, 10, tzinfo=IST),
                    fetcher=lambda *_: self.fail("fetch after arrival"),
                )

            self.assertEqual(arrival, "arrived")
            self.assertEqual(finished, "finished")
            self.assertIn("Train arrived", arrival_output.getvalue())

    def test_force_alert_does_not_fetch_or_reopen_a_finished_watch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            state_path = config_path.with_suffix(".state.json")
            state_path.write_text(
                json.dumps(
                    {
                        "failure_count": 0,
                        "finished": True,
                        "last_event": "arrived",
                        "status": module.normalize_status(sample_payload(at_dstn=True)),
                    }
                ),
                encoding="utf-8",
            )
            original_state = state_path.read_text(encoding="utf-8")
            output = io.StringIO()

            with redirect_stdout(output):
                event = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 12, 10, tzinfo=IST),
                    fetcher=lambda *_: self.fail("forced fetch after arrival"),
                    force_alert=True,
                )

            self.assertEqual(event, "finished")
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(state_path.read_text(encoding="utf-8"), original_state)

    def test_identity_mismatch_is_rejected_and_safely_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            malicious_source = "OTHER\n@everyone [click](https://evil.example)"
            mismatched = module.normalize_status(
                sample_payload(source=malicious_source)
            )
            output = io.StringIO()

            with redirect_stdout(output):
                event = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 8, 0, tzinfo=IST),
                    fetcher=lambda *_: mismatched,
                )

            state = json.loads(
                config_path.with_suffix(".state.json").read_text(encoding="utf-8")
            )
            self.assertEqual(event, "error_alert")
            self.assertEqual(state["failure_count"], 1)
            self.assertNotIn("status", state)
            self.assertIn("Live-status identity mismatch", output.getvalue())
            self.assertNotIn("@everyone", output.getvalue())
            self.assertNotIn("https://evil.example", output.getvalue())
            self.assertNotIn("\n@everyone", output.getvalue())

    def test_failure_preserves_last_good_state_and_throttles_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            good = module.normalize_status(sample_payload())
            with redirect_stdout(io.StringIO()):
                module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 8, 0, tzinfo=IST),
                    fetcher=lambda *_: good,
                )

            def fail(*_):
                raise RuntimeError(f"request failed for {TRAIN_NUMBER}")

            first_output = io.StringIO()
            second_output = io.StringIO()
            with redirect_stdout(first_output):
                first = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 8, 10, tzinfo=IST),
                    fetcher=fail,
                )
            with redirect_stdout(second_output):
                second = module.run_watch(
                    config_path,
                    now=datetime(2099, 1, 2, 8, 20, tzinfo=IST),
                    fetcher=fail,
                )

            state = json.loads(config_path.with_suffix(".state.json").read_text())
            self.assertEqual(first, "error_alert")
            self.assertEqual(second, "error_suppressed")
            self.assertEqual(state["status"], good)
            self.assertNotIn(TRAIN_NUMBER, first_output.getvalue())
            self.assertEqual(second_output.getvalue(), "")


class CliTest(unittest.TestCase):
    def test_dry_run_does_not_write_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = write_config(Path(temp_dir))
            output = io.StringIO()

            with redirect_stdout(output):
                result = module.main(
                    ["--config", str(config_path), "--dry-run"],
                    now=datetime(2099, 1, 1, 12, 0, tzinfo=IST),
                    fetcher=lambda *_: module.normalize_status(sample_payload()),
                )

            self.assertEqual(result, 0)
            self.assertIn(f'"train_number": "{TRAIN_NUMBER}"', output.getvalue())
            self.assertFalse(config_path.with_suffix(".state.json").exists())


if __name__ == "__main__":
    unittest.main()
