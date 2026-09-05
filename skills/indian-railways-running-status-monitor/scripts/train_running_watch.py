#!/usr/bin/env python3
"""Monitor one Indian Railways train instance with change-only output."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

API_BASE = "https://livestatus.railyatri.in/api/v3/train_eta_data"
IST = ZoneInfo("Asia/Kolkata")
_MARKDOWN_UNSAFE = "@\\`*_{}[]<>()#+=|~!/:.&$^"
_MARKDOWN_SAFE_TRANSLATION = str.maketrans(
    {character: chr(ord(character) + 0xFEE0) for character in _MARKDOWN_UNSAFE}
)


def _sanitize_markdown_text(value: Any) -> str:
    """Render untrusted text inert in Markdown-based delivery channels."""
    normalized = unicodedata.normalize("NFKC", str(value))
    without_controls = "".join(
        " "
        if character.isspace() or unicodedata.category(character).startswith("C")
        else character
        for character in normalized
    )
    collapsed = " ".join(without_controls.split())
    return collapsed.translate(_MARKDOWN_SAFE_TRANSLATION)


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"Expected a JSON object in {path}")
    return value


def save_state(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_name, 0o600)
        os.replace(temp_name, path)
        os.chmod(path, 0o600)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def normalize_status(payload: dict[str, Any]) -> dict[str, Any]:
    if not payload.get("success"):
        raise ValueError("Live-status response was not successful")
    required = ("train_number", "train_start_date", "source", "destination")
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise ValueError(f"Live-status response is missing: {', '.join(missing)}")

    location = ""
    location_hint = ""
    for item in payload.get("current_location_info") or []:
        if item.get("type") == 1 and item.get("message"):
            location = str(item["message"]).strip()
            location_hint = str(item.get("hint") or "").strip()
            break
    if not location:
        location = str(
            payload.get("new_message") or payload.get("title") or "Status unavailable"
        ).strip()

    next_station = None
    for station in payload.get("upcoming_stations") or []:
        if station.get("station_code"):
            next_station = {
                "code": str(station["station_code"]),
                "name": str(station.get("station_name") or station["station_code"]),
                "eta": str(station.get("eta") or ""),
                "delay_minutes": int(station.get("arrival_delay") or 0),
                "platform": int(station.get("platform_number") or 0),
                "distance_from_source": int(station.get("distance_from_source") or 0),
            }
            break

    status_code = str(payload.get("status") or "")
    current_station_code = str(payload.get("current_station_code") or "")
    destination = str(payload["destination"])
    at_destination = bool(payload.get("at_dstn")) or (
        status_code == "A" and current_station_code == destination
    )
    return {
        "train_number": str(payload["train_number"]),
        "train_name": str(payload.get("train_name") or ""),
        "train_start_date": str(payload["train_start_date"]),
        "source": str(payload["source"]),
        "source_name": str(payload.get("source_stn_name") or payload["source"]),
        "destination": destination,
        "destination_name": str(payload.get("dest_stn_name") or destination),
        "scheduled_departure": str(payload.get("std") or ""),
        "journey_time_minutes": int(payload.get("journey_time") or 0),
        "current_station_code": current_station_code,
        "current_station_name": str(payload.get("current_station_name") or ""),
        "status_code": status_code,
        "location_message": location,
        "location_hint": location_hint,
        "delay_minutes": int(payload.get("delay") or 0),
        "eta": str(payload.get("eta") or ""),
        "etd": str(payload.get("etd") or ""),
        "status_as_of": str(payload.get("status_as_of") or ""),
        "updated_at": str(payload.get("update_time") or ""),
        "distance_from_source": int(payload.get("distance_from_source") or 0),
        "total_distance": int(payload.get("total_distance") or 0),
        "platform": int(payload.get("platform_number") or 0),
        "next_station": next_station,
        "at_destination": at_destination,
        "title": str(payload.get("title") or ""),
        "message": str(payload.get("new_message") or ""),
        "data_from": str(payload.get("data_from") or ""),
    }


def status_fingerprint(status: dict[str, Any]) -> str:
    stable = {
        key: status.get(key)
        for key in (
            "train_start_date",
            "status_code",
            "current_station_code",
            "current_station_name",
            "location_message",
            "location_hint",
            "delay_minutes",
            "eta",
            "etd",
            "platform",
            "next_station",
            "at_destination",
            "title",
            "message",
        )
    }
    return json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def determine_event(
    previous_state: dict[str, Any] | None,
    current_status: dict[str, Any],
    *,
    force: bool = False,
) -> str:
    if force:
        return "test"
    if current_status.get("at_destination"):
        if not previous_state or not previous_state.get("status", {}).get(
            "at_destination"
        ):
            return "arrived"
        return "no_change"
    if not previous_state or not previous_state.get("status"):
        return "baseline"
    if status_fingerprint(previous_state["status"]) != status_fingerprint(
        current_status
    ):
        return "change"
    return "no_change"


def build_alert_message(
    status: dict[str, Any],
    *,
    config: dict[str, Any],
    event: str,
) -> str:
    heading = {
        "baseline": "Running-status monitor started",
        "change": "Train running update",
        "arrived": "Train arrived",
        "test": "Running-status monitor test",
    }.get(event, "Train running update")
    delay = int(status.get("delay_minutes") or 0)
    if delay > 0:
        delay_text = f"{delay} min late"
    elif delay < 0:
        delay_text = f"{abs(delay)} min early"
    else:
        delay_text = "On time"

    safe_text = _sanitize_markdown_text
    mention = str(config.get("mention") or "").strip()
    prefix = f"{mention} " if mention else ""
    lines = [
        f"{prefix}🚆 **{heading}**",
        "",
        f"Watch: **{safe_text(config.get('label') or 'Rail journey')}**",
        (
            f"Train: **{safe_text(status['train_number'])} "
            f"{safe_text(status['train_name'])}**"
        ),
        (
            f"Journey: {safe_text(status['source_name'])} → "
            f"{safe_text(status['destination_name'])} · "
            f"**{safe_text(status['train_start_date'])}**"
        ),
        f"Status: **{safe_text(status['location_message'])}**",
        f"Delay: **{delay_text}**",
    ]
    next_station = status.get("next_station")
    if next_station:
        next_bits = [safe_text(next_station["name"])]
        if next_station.get("eta"):
            next_bits.append(f"ETA {safe_text(next_station['eta'])}")
        if next_station.get("platform"):
            next_bits.append(f"PF {next_station['platform']}")
        lines.append("Next: " + " · ".join(next_bits))
    elif status.get("platform"):
        lines.append(f"Platform: PF {status['platform']}")
    distance = int(status.get("distance_from_source") or 0)
    total = int(status.get("total_distance") or 0)
    if total:
        lines.append(f"Progress: {distance}/{total} km")
    if status.get("updated_at"):
        lines.append(f"Source updated: {safe_text(status['updated_at'])}")
    train_path = urllib.parse.quote(str(status["train_number"]), safe="")
    source_page = f"https://www.railyatri.in/live-train-status/{train_path}"
    source_note = " (reports NTES data)" if status.get("data_from") == "mntes" else ""
    lines.append(f"Source: [RailYatri live status]({source_page}){source_note}")
    return "\n".join(lines)


def fetch_status(
    config: dict[str, Any],
    now: datetime,
    *,
    urlopen: Any = urllib.request.urlopen,
    attempts: int = 3,
) -> dict[str, Any]:
    train_number = str(config.get("train_number") or "")
    if not re.fullmatch(r"\d{4,5}", train_number):
        raise ValueError(
            "Watcher configuration must contain a 4- or 5-digit train number"
        )
    journey_date = datetime.fromisoformat(str(config["journey_date"])).date()
    start_day = (now.date() - journey_date).days
    query = urllib.parse.urlencode(
        {
            "start_day": start_day,
            "user_id": -1,
            "device_type_id": 4,
            "change_name": "seo_train_name",
            "lat": "",
            "lng": "",
            "claim_on_train": "false",
        }
    )
    url = f"{API_BASE}/{train_number}/{start_day}.json?{query}"
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36"
                    ),
                    "Accept": "application/json",
                    "Accept-Language": "en-IN,en;q=0.9",
                },
            )
            with urlopen(request, timeout=45) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise TypeError("Live-status response was not a JSON object")
            return normalize_status(payload)
        except (
            OSError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
            urllib.error.URLError,
        ) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(3 * attempt)
    raise RuntimeError(
        f"RailYatri live-status fetch failed after {attempts} attempts: {last_error}"
    )


def _identity_mismatches(
    config: dict[str, Any],
    status: dict[str, Any],
) -> list[str]:
    expected = {
        "train_number": config["train_number"],
        "train_start_date": config["journey_date"],
        "source": config["source"],
        "destination": config["destination"],
    }
    return [
        f"{key}={status.get(key)!r} (expected {value!r})"
        for key, value in expected.items()
        if str(status.get(key)) != str(value)
    ]


def run_watch(
    config_path: Path,
    *,
    now: datetime | None = None,
    fetcher: Callable[..., dict[str, Any]] = fetch_status,
    force_alert: bool = False,
) -> str:
    config = load_json(Path(config_path))
    if not config:
        raise ValueError(f"Missing watcher configuration: {config_path}")
    current_time = now or datetime.now(IST)
    monitor_from = datetime.fromisoformat(str(config["monitor_from"]))
    monitor_until = datetime.fromisoformat(str(config["monitor_until"]))
    if monitor_from.utcoffset() is None or monitor_until.utcoffset() is None:
        raise ValueError("Monitoring timestamps must include a UTC offset")
    if monitor_from > monitor_until:
        raise ValueError("monitor_from must not be later than monitor_until")
    if not force_alert and (
        current_time < monitor_from or current_time > monitor_until
    ):
        return "inactive"

    state_path = Path(
        config.get("state_path") or Path(config_path).with_suffix(".state.json")
    )
    previous_state = load_json(state_path)
    if previous_state and previous_state.get("finished"):
        return "finished"

    try:
        status = fetcher(config, current_time)
        mismatches = _identity_mismatches(config, status)
        if mismatches:
            raise ValueError("Live-status identity mismatch: " + "; ".join(mismatches))
    except Exception as exc:  # noqa: BLE001 - cron must preserve state on any fetch failure
        failure_count = int((previous_state or {}).get("failure_count", 0)) + 1
        failure_state = dict(previous_state or {})
        failure_state["failure_count"] = failure_count
        train_number = str(config.get("train_number") or "")
        failure_state["last_error"] = _sanitize_markdown_text(
            str(exc).replace(train_number, "*****")
        )[:500]
        save_state(state_path, failure_state)
        if failure_count == 1 or failure_count % 6 == 0:
            mention = str(config.get("mention") or "").strip()
            prefix = f"{mention} " if mention else ""
            print(
                f"{prefix}⚠️ **Running-status monitor problem**\n\n"
                f"Could not check the configured train (failure {failure_count}).\n"
                f"Reason: {failure_state['last_error']}\n"
                "The watcher will retry on its next run."
            )
            return "error_alert"
        return "error_suppressed"

    event = determine_event(previous_state, status, force=force_alert)
    if event != "no_change":
        print(build_alert_message(status, config=config, event=event))
    save_state(
        state_path,
        {
            "failure_count": 0,
            "finished": event == "arrived",
            "last_event": event,
            "status": status,
        },
    )
    return event


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "train-running-watches" / "watch.json"


def main(
    argv: list[str] | None = None,
    *,
    now: datetime | None = None,
    fetcher: Callable[..., dict[str, Any]] = fetch_status,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-alert", action="store_true")
    args = parser.parse_args(argv)

    current_time = now or datetime.now(IST)
    if args.dry_run:
        config = load_json(args.config)
        if not config:
            raise ValueError(f"Missing watcher configuration: {args.config}")
        status = fetcher(config, current_time)
        mismatches = _identity_mismatches(config, status)
        if mismatches:
            raise ValueError("Live-status identity mismatch: " + "; ".join(mismatches))
        print(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=False))
        return 0

    run_watch(
        args.config,
        now=current_time,
        fetcher=fetcher,
        force_alert=args.force_alert,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
