---
name: indian-railways-running-status-monitor
description: "Monitor train running status with change-only alerts."
version: 0.1.0
author: Repository maintainers, Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Indian-Railways, Running-Status, Travel, Alerts, Cron]
    related_skills: [indian-railways-pnr-monitor]
---

# Indian Railways Running Status Monitor

Monitor one Indian Railways train instance and emit updates only when operational status changes. The bundled `scripts/train_running_watch.py` helper tracks location, delay, ETA, next stop, platform, and arrival without requiring a PNR. It uses an unofficial RailYatri endpoint, so establish a live baseline before scheduling and treat results as best-effort rather than safety-critical information.

## When to Use

- The user wants automated running-status alerts for a specific train journey.
- The user wants location, delay, ETA, next-stop, platform, or arrival changes.
- A silent-unless-changed cron job is preferable to repeated manual checks.

Don't use for ticket booking, PNR confirmation, high-frequency polling, operational safety decisions, CAPTCHA bypass, or cases requiring a contracted railway API.

## Prerequisites

- Python 3.9 or newer with timezone data for `Asia/Kolkata`.
- Hermes cron scheduling available.
- Network access to `livestatus.railyatri.in` and `www.railyatri.in`.
- User consent to submit the train number and journey date to RailYatri.
- A selected Hermes delivery destination.

A train number is public, but a train number combined with a travel date and route can reveal an itinerary. Keep live configuration and state outside source control.

## How to Run

Install the helper into the active Hermes profile's script directory:

```python
terminal(
    command='install -d -m 700 "${HERMES_HOME:-$HOME/.hermes}/scripts" && install -m 700 "${HERMES_SKILL_DIR}/scripts/train_running_watch.py" "${HERMES_HOME:-$HOME/.hermes}/scripts/indian_railways_running_status_watch.py"',
    timeout=60,
)
```

Before calling `write_file`, resolve the active profile root to an absolute path:

```python
terminal(
    command="python3 -c 'import os; from pathlib import Path; print(Path(os.environ.get(\"HERMES_HOME\") or Path.home() / \".hermes\").expanduser().resolve())'",
    timeout=30,
)
```

Start from `templates/watch-config.example.json`. Copy the returned absolute profile path into `write_file(path="<absolute-profile-path>/train-running-watches/watch.json", ...)`, write the completed configuration, then restrict it. File-tool paths do not expand `$HERMES_HOME`, `${HERMES_HOME}`, or `~`; never pass those forms to `write_file`.

```python
terminal(
    command='chmod 600 "${HERMES_HOME:-$HOME/.hermes}/train-running-watches/watch.json"',
    timeout=30,
)
```

Run a live, non-mutating baseline:

```python
terminal(
    command='python3 "${HERMES_HOME:-$HOME/.hermes}/scripts/indian_railways_running_status_watch.py" --config "${HERMES_HOME:-$HOME/.hermes}/train-running-watches/watch.json" --dry-run',
    timeout=180,
)
```

## Configuration

- `train_number`: four- or five-digit train number.
- `journey_date`: date the train leaves its originating station, formatted `YYYY-MM-DD`. This can differ from the passenger's boarding date for an overnight train.
- `source`: originating station code expected from the live feed.
- `destination`: terminating station code expected from the live feed.
- `monitor_from`: timezone-aware ISO timestamp for the first allowed check.
- `monitor_until`: timezone-aware ISO timestamp after which checks stop.
- `label`: non-sensitive name shown in alerts.
- `mention`: optional platform mention prepended to alerts.
- `state_path`: optional absolute state path; when omitted, state is stored beside the configuration with a `.state.json` suffix.

## Procedure

1. Resolve the train number, origin departure date, originating station code, destination station code, and scheduled times from a current source. Do not infer the origin date from an intermediate boarding date without checking the timetable. Done when the exact train instance is unambiguous.
2. Read `templates/watch-config.example.json`, replace every placeholder, resolve `HERMES_HOME` to an absolute profile path, and pass that absolute path to `write_file`; file tools do not expand shell variables or `~`. Write the result outside the repository and set a monitoring window that starts before departure and extends past scheduled arrival to tolerate delays. Done when the config contains no placeholder and has mode `0600`.
3. Install `scripts/train_running_watch.py` and run `--dry-run`. Verify train number, train name, start date, source, destination, and scheduled departure against the intended journey. Do not schedule on a mismatch. Done when one live baseline succeeds without creating state.
4. Create a script-only cron job with a respectful cadence and finite repeat count. Ten minutes is appropriate during a journey; avoid aggressive polling. Done when `cronjob(action="list")` shows the expected script, cadence, finite repeat count, and destination.
5. Let cron deliver stdout. The helper stays silent outside the window and when nothing operational changed; it prints a baseline, meaningful changes, arrival, the first failure, and every sixth consecutive failure. Done when an unchanged replay produces no delivery.
6. After arrival, confirm state records `finished: true`. The helper will stop fetching even if finite cron ticks remain. Done when a post-arrival invocation is silent and returns `finished`.

Create the recurring job with the installed script name:

```text
cronjob(
  action="create",
  name="Train running status watch",
  schedule="every 10m",
  repeat=<finite count ending after monitor_until>,
  prompt="Run the deterministic train running-status watcher and deliver change-only output.",
  script="indian_railways_running_status_watch.py",
  no_agent=true,
  deliver=<selected destination>
)
```

## Alert Behavior

The helper fingerprints operational fields while excluding volatile refresh timestamps. It emits output for:

- the first in-window baseline;
- current-location, delay, ETA, next-stop, or platform changes;
- arrival at the configured destination;
- a forced setup test using `--force-alert` for an unfinished watch;
- the first fetch failure and every sixth consecutive failure.

Failed fetches preserve the last good status. State writes are atomic and use mode `0600`.

## Pitfalls

- RailYatri is an undocumented third-party source and may change or become unavailable.
- A future train instance may report only a pre-departure message until live data begins.
- The API's relative `start_day` is derived from the configured origin date; using the passenger's boarding date can select the wrong train instance.
- Platform numbers and ETAs may be revised and should be independently confirmed at the station.
- A monitoring window that ends at scheduled arrival can stop too early when the train is delayed.
- Reusing one state file for multiple journeys mixes fingerprints and suppresses valid alerts.
- The helper uses POSIX permission modes, so this skill is limited to Linux and macOS.

## Verification

- [ ] Live dry-run matches the intended train number, origin date, source, and destination.
- [ ] No real itinerary, state file, credentials, channel identifier, or personal mention is stored in the repository.
- [ ] Configuration and state files have mode `0600`.
- [ ] First in-window run emits a baseline and an unchanged second run is silent.
- [ ] A simulated or observed arrival emits once and marks the watch finished.
- [ ] Fetch failures preserve the last good status and do not disclose the configured train number in error text.
- [ ] Cron uses `no_agent=true`, a respectful cadence, and a finite repeat count.
