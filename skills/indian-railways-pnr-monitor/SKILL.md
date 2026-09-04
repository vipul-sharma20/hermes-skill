---
name: indian-railways-pnr-monitor
description: "Monitor Indian Railways PNR changes with scheduled alerts."
version: 0.1.1
author: Vipul Sharma (vipul-sharma20), Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Indian-Railways, PNR, Travel, Alerts, Cron]
    related_skills: []
---

# Indian Railways PNR Monitor

Monitor a PNR through RailYatri's public status page and emit an alert only when passenger or chart status changes. This is an unofficial third-party integration: establish a live baseline before scheduling and expect the parser to require maintenance if the page changes.

## When to Use

- The user asks to monitor an Indian Railways PNR.
- The user wants recurring WL, RAC, CNF, berth, or chart-status alerts.
- A free, low-frequency monitor is acceptable and the user consents to sharing the PNR with RailYatri.

Don't use for ticket booking, cancellation, high-frequency polling, CAPTCHA bypass, or cases where an official or contracted API is required.

## Prerequisites

- Hermes gateway and cron scheduler running.
- `python3` available.
- Network access to `https://www.railyatri.in`.
- Explicit user consent to submit the PNR to RailYatri.
- A selected Hermes delivery destination.

The full PNR is private travel information. Never place it in a job name, cron prompt, log message, repository, or alert body.

## Setup

### 1. Install the cron script

The bundled helper is `scripts/pnr_watch.py`. Copy it into the profile's cron-script directory:

```python
terminal(
    command='install -d -m 700 "${HERMES_HOME:-$HOME/.hermes}/scripts" && install -m 700 "${HERMES_SKILL_DIR}/scripts/pnr_watch.py" "${HERMES_HOME:-$HOME/.hermes}/scripts/indian_railways_pnr_watch.py"',
    timeout=60,
)
```

Done when the destination script exists with owner-executable permissions.

### 2. Create a protected watch configuration

Start from `templates/watch-config.example.json`, replace the placeholder PNR, choose a non-sensitive label, and optionally add a platform mention such as `@username`. Write it to:

```text
${HERMES_HOME}/pnr-watches/watch.json
```

Set mode `0600`. Do not include a full PNR in the filename. Done when only the owner can read the configuration.

### 3. Establish a live baseline

Run a dry check before creating the cron job:

```python
terminal(
    command='python3 "${HERMES_HOME:-$HOME/.hermes}/scripts/indian_railways_pnr_watch.py" --config "${HERMES_HOME:-$HOME/.hermes}/pnr-watches/watch.json" --dry-run',
    timeout=180,
)
```

Verify train, date, route, class, passenger count, booking status, current status, and chart state with the user. Do not schedule if any field is wrong.

### 4. Create the recurring job

Use a script-only job so unchanged runs consume no LLM calls and produce no delivery:

```text
cronjob(
  action="create",
  name="Hourly PNR status watch",
  schedule="every 1h",
  script="indian_railways_pnr_watch.py",
  no_agent=true,
  deliver=<selected destination>
)
```

Set a finite repeat count ending after the journey when the travel date is known. Done when `cronjob(action="list")` shows the expected cadence, script, and destination.

### 5. Test delivery

Run once with `--force-alert` in the foreground or trigger the cron job manually. Verify the delivered alert shows only the last four PNR digits and the correct passenger count. A second unchanged normal run must stay silent.

## Alert Behavior

The helper emits stdout only for:

- initial baseline;
- passenger booking/current status changes;
- chart-status changes;
- a forced test;
- the first fetch failure and every third consecutive failure.

State is stored next to the configuration as `watch.state.json` with mode `0600`. Failed fetches preserve the last-good observation.

## Pitfalls

- RailYatri is an undocumented source and can change without notice.
- The refresh response and original page can contain duplicate passenger lists; parse only the first refreshed list.
- A PNR can reveal itinerary and reservation status. Keep configuration and state out of source control.
- Platform mention behavior differs. A textual `@username` does not guarantee a push when an adapter or channel suppresses mentions.
- Do not overwrite the last-good state with an error page.
- Polling aggressively can trigger blocking; hourly is the recommended default.

## Verification

- [ ] Live dry-run matches the ticket and passenger count.
- [ ] Full PNR appears only in the protected local configuration.
- [ ] Alert shows only the final four digits.
- [ ] Baseline or forced alert reaches the selected destination.
- [ ] A second unchanged run emits no stdout.
- [ ] State survives a Hermes restart.
- [ ] Cron job has a finite end after the journey when possible.
