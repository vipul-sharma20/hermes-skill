#!/usr/bin/env python3
"""Monitor a RailYatri PNR page and emit change-only alerts."""

from __future__ import annotations

import argparse
import html as html_lib
import http.cookiejar
import json
import os
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo


def _text(fragment: str) -> str:
    fragment = re.sub(
        r"(?is)<!--.*?-->|<script\b.*?</script>|<style\b.*?</style>",
        " ",
        fragment,
    )
    fragment = re.sub(r"(?is)<br\s*/?>", " ", fragment)
    fragment = re.sub(r"(?s)<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(fragment)).strip()


def _field_after_label(page: str, label: str, value_class: str = "pnr-bold-txt") -> str:
    pattern = (
        r"<p[^>]*>\s*" + re.escape(label) + r"\s*</p>\s*"
        r"<p[^>]*class=[\"'][^\"']*" + re.escape(value_class)
        + r"[^\"']*[\"'][^>]*>(.*?)</p>"
    )
    match = re.search(pattern, page, re.I | re.S)
    return _text(match.group(1)) if match else ""


def canonical_status(value: str) -> str:
    value = _text(value).strip()
    waitlist = re.fullmatch(r"(\d+)\s*(?:WAITLIST|WAITING\s+LIST|WL)", value, re.I)
    if waitlist:
        return f"WL/{waitlist.group(1)}"
    rac = re.fullmatch(r"RAC\s*[/ -]?\s*(\d+)", value, re.I)
    if rac:
        return f"RAC/{rac.group(1)}"
    if re.fullmatch(r"CONFIRMED|CONFIRM|CNF", value, re.I):
        return "CNF"
    return re.sub(r"\s+", " ", value).strip()


def parse_pnr_html(page: str) -> dict[str, Any]:
    chart_match = re.search(
        r"class=[\"'][^\"']*chart-status-txt[^\"']*[\"'][^>]*>(.*?)</p>",
        page,
        re.I | re.S,
    )
    chart_status = _text(chart_match.group(1)) if chart_match else ""

    train_match = re.search(r"TRAIN NAME\s*:.*?<a\b[^>]*>(.*?)</a>", page, re.I | re.S)
    train_text = _text(train_match.group(1)) if train_match else ""
    train_parts = re.match(r"^(\d{4,5})\s*\W*\s*(.*?)$", train_text)
    train_number = train_parts.group(1) if train_parts else ""
    train_name = train_parts.group(2) if train_parts else train_text

    passenger_list = re.search(
        r"<ul[^>]*class=[\"'][^\"']*pasListUL[^\"']*[\"'][^>]*>(.*?)</ul>",
        page,
        re.I | re.S,
    )
    passenger_source = passenger_list.group(1) if passenger_list else ""
    passengers: list[dict[str, Any]] = []
    blocks = re.findall(
        r"<li[^>]*class=[\"'][^\"']*PNRPasList[^\"']*[\"'][^>]*>(.*?)</li>",
        passenger_source,
        re.I | re.S,
    )
    for index, block in enumerate(blocks, start=1):
        values = re.findall(
            r"<p[^>]*class=[\"'][^\"']*statusType[^\"']*[\"'][^>]*>(.*?)</p>",
            block,
            re.I | re.S,
        )
        if len(values) >= 2:
            passengers.append(
                {
                    "number": index,
                    "booking": canonical_status(values[0]),
                    "current": canonical_status(values[1]),
                }
            )

    result: dict[str, Any] = {
        "train_number": train_number,
        "train_name": train_name,
        "from": _field_after_label(page, "FROM"),
        "to": _field_after_label(page, "TO"),
        "boarding_date": _field_after_label(page, "DAY OF BOARDING"),
        "journey_class": _field_after_label(page, "CLASS"),
        "chart_status": chart_status,
        "passengers": passengers,
    }
    required = ("train_number", "from", "to", "boarding_date", "chart_status")
    missing = [key for key in required if not result[key]]
    if missing or not passengers:
        detail = ", ".join(missing + ([] if passengers else ["passengers"]))
        raise ValueError(f"RailYatri response did not contain a complete PNR result: {detail}")
    return result


def status_fingerprint(status: dict[str, Any]) -> str:
    stable = {
        key: status.get(key)
        for key in (
            "train_number",
            "train_name",
            "from",
            "to",
            "boarding_date",
            "journey_class",
            "chart_status",
            "passengers",
        )
    }
    return json.dumps(stable, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def decode_update_html(response: str) -> str:
    fragments: list[str] = []
    pattern = r'\$\("#[^\"]+"\)\.html\("(.*?)"\);'
    for payload in re.findall(pattern, response, re.S):
        payload = payload.replace("\\'", "'")
        fragments.append(json.loads('"' + payload + '"'))
    if not fragments:
        raise ValueError("RailYatri refresh response contained no HTML fragments")
    return "\n".join(fragments)


def determine_event(
    previous_state: dict[str, Any] | None,
    current_status: dict[str, Any],
    *,
    force: bool,
) -> str:
    if force:
        return "test"
    if not previous_state or not previous_state.get("status"):
        return "baseline"
    if status_fingerprint(previous_state["status"]) != status_fingerprint(current_status):
        return "change"
    return "no_change"


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
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


def build_alert_message(
    status: dict[str, Any],
    *,
    pnr: str,
    label: str,
    mention: str,
    event: str,
    previous: dict[str, Any] | None = None,
) -> str:
    heading = {
        "baseline": "PNR monitor started",
        "change": "PNR status changed",
        "test": "PNR monitor test",
    }.get(event, "PNR monitor")
    prefix = f"{mention.strip()} " if mention.strip() else ""
    lines = [
        f"{prefix}🚆 **{heading}**",
        "",
        f"Watch: **{label or 'Rail journey'}**",
        f"PNR ending **{pnr[-4:]}**",
        f"Train: **{status['train_number']} {status['train_name']}**",
        f"Route: {status['from']} → {status['to']}",
        f"Boarding: **{status['boarding_date']}** · Class **{status['journey_class']}**",
    ]
    previous_passengers = {
        item.get("number"): item for item in (previous or {}).get("passengers", [])
    }
    for passenger in status["passengers"]:
        old = previous_passengers.get(passenger["number"], {}).get("current")
        if event == "change" and old and old != passenger["current"]:
            lines.append(
                f"Passenger {passenger['number']}: **{old} → {passenger['current']}** "
                f"(booked {passenger['booking']})"
            )
        else:
            lines.append(
                f"Passenger {passenger['number']} — Booked: **{passenger['booking']}** · "
                f"Current: **{passenger['current']}**"
            )
    old_chart = (previous or {}).get("chart_status")
    if event == "change" and old_chart and old_chart != status["chart_status"]:
        lines.append(f"Chart: **{old_chart} → {status['chart_status']}**")
    else:
        lines.append(f"Chart: **{status['chart_status']}**")
    if status.get("checked_at"):
        lines.append(f"Checked: {status['checked_at']}")
    return "\n".join(lines)


def fetch_status(pnr: str, *, attempts: int = 3) -> dict[str, Any]:
    base_url = "https://www.railyatri.in"
    user_agent = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/124 Safari/537.36"
    )
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        cookies = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
        page_url = f"{base_url}/pnr-status/{pnr}"
        try:
            request = urllib.request.Request(
                page_url,
                headers={"User-Agent": user_agent, "Accept-Language": "en-IN,en;q=0.9"},
            )
            with opener.open(request, timeout=45) as response:
                page = response.read().decode("utf-8", "replace")
            csrf_match = re.search(r'<meta name="csrf-token" content="([^"]+)"', page)
            if not csrf_match:
                raise ValueError("RailYatri page did not provide a CSRF token")
            refresh = urllib.request.Request(
                f"{base_url}/update-status-result",
                data=urllib.parse.urlencode({"pnr_number": pnr}).encode(),
                method="POST",
                headers={
                    "User-Agent": user_agent,
                    "Accept": "*/*",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": base_url,
                    "Referer": page_url,
                    "X-CSRF-Token": csrf_match.group(1),
                    "X-Requested-With": "XMLHttpRequest",
                },
            )
            with opener.open(refresh, timeout=60) as response:
                update_javascript = response.read().decode("utf-8", "replace")
            status = parse_pnr_html(decode_update_html(update_javascript) + "\n" + page)
            status["checked_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).strftime(
                "%d-%m-%Y %I:%M %p IST"
            )
            status["source"] = "RailYatri"
            return status
        except (OSError, ValueError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt < attempts:
                time.sleep(3 * attempt)
    raise RuntimeError(f"RailYatri refresh failed after {attempts} attempts: {last_error}")


def run_watch(
    config_path: Path,
    *,
    fetcher: Callable[[str], dict[str, Any]] = fetch_status,
    force_alert: bool = False,
) -> str:
    config = load_json(config_path)
    if not config:
        raise ValueError(f"Missing watcher configuration: {config_path}")
    pnr = str(config.get("pnr", ""))
    if not re.fullmatch(r"\d{10}", pnr):
        raise ValueError("Watcher configuration must contain a 10-digit PNR")
    state_path = Path(config.get("state_path") or config_path.with_suffix(".state.json"))
    previous_state = load_json(state_path)
    try:
        status = fetcher(pnr)
    except Exception as exc:
        failure_count = int((previous_state or {}).get("failure_count", 0)) + 1
        failure_state = dict(previous_state or {})
        failure_state["failure_count"] = failure_count
        failure_state["last_error"] = str(exc).replace(pnr, "**********")[:500]
        save_state(state_path, failure_state)
        if failure_count == 1 or failure_count % 3 == 0:
            mention = f"{str(config.get('mention', '')).strip()} " if config.get("mention") else ""
            print(
                f"{mention}⚠️ **PNR monitor problem**\n\n"
                f"PNR ending **{pnr[-4:]}** could not be checked "
                f"(failure {failure_count}).\n"
                f"Reason: {failure_state['last_error']}\n"
                "The watcher will retry on its next run."
            )
            return "error_alert"
        return "error_suppressed"

    event = determine_event(previous_state, status, force=force_alert)
    if event != "no_change":
        print(
            build_alert_message(
                status,
                pnr=pnr,
                label=str(config.get("label", "Rail journey")),
                mention=str(config.get("mention", "")),
                event=event,
                previous=(previous_state or {}).get("status"),
            )
        )
    save_state(
        state_path,
        {"failure_count": 0, "last_event": event, "status": status},
    )
    return event


def default_config_path() -> Path:
    return Path(__file__).resolve().parents[1] / "pnr-watches" / "watch.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=default_config_path())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force-alert", action="store_true")
    args = parser.parse_args(argv)

    if args.dry_run:
        config = load_json(args.config)
        if not config:
            raise ValueError(f"Missing watcher configuration: {args.config}")
        status = fetch_status(str(config["pnr"]))
        print(json.dumps(status, indent=2, sort_keys=True, ensure_ascii=False))
        return 0
    run_watch(args.config, force_alert=args.force_alert)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
