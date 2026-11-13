# Travel identity and lifecycle checks

Existing public indian-railways-pnr-monitor and indian-railways-running-status-monitor packages already supply purpose-specific workflows. Prefer configuring/reviewing those packages to creating another synonym. This reference adds acceptance questions, not an additional provider fetcher or live status claim.

PNR/reservation state is not train movement. Use separate protected config/state/jobs if both are requested. A full PNR is private; train number with date/route is itinerary data too. Consent to one provider does not permit automatic fallback to every travel site. No CAPTCHA bypass or account guessing.

A train instance needs number, origin departure date, actual monitored segment, origin/destination and timezone. Boarding after midnight may have a different date. Confirm relative words using a tool clock and Asia/Kolkata for Indian journeys. Undocumented relative-day fields must be revalidated against current provider behavior, not assumed from past output.

Require exact identity before interpreting not-started, running or arrived. HTTP success with placeholder date, missing passengers or a different completed service is a failed fetch. Source-update time and check time are different; use last reported at rather than exact present position when data is old.

Current status, booking status, prediction, chart-prepared and seat assignment are separate. A numeric berth field can repeat a waitlist position; require explicit consistent current coach/seat evidence. CNF alone proves neither prepared chart nor available seat detail. Missing parser fields mean details unavailable in this result, not no seat assigned. Provider probabilities are estimates, not railway guarantees.

Lifecycle ordering: outside window/after safety deadline/finished => no fetch; otherwise fetch+validate identity; wait for actual departure evidence if requested; alert first running observation and meaningful changes; confirmed destination arrival => one final alert and persistent finished state. Scheduled departure time alone is not observed departure, and expiry is not arrival. Arrival at the train's terminus may differ from the passenger's destination—define which is monitored.

Use a finite execution count as a backstop plus an in-script wall-clock deadline. Check only versus deliver every interval versus change-only are different user requests. Preserve last-good state on all failures; throttle errors and reset failure streak after recovery.

Fixtures must cover future/undeparted, wrong instance, first departure, refresh-only change, location/delay change, arrival, expiry without arrival, after-finished no-network, source failure/recovery and exact job cancellation. An old recorded fallback endpoint requires terms/consent/current validation before adding it to an existing public runtime.
