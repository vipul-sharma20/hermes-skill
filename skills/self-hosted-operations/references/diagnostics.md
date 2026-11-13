# Linux and external-browser diagnostics

## Bounded host probes

Run through the already authorized transport with `terminal`; these examples describe a target Linux host, not necessarily the agent container:

```python
terminal(command="hostname; date -Is; uptime; nproc", timeout=20)
terminal(command="vmstat 1 5", timeout=20)
terminal(command="ps -eo pid,ppid,comm,stat,etimes,%cpu,rss --sort=-%cpu", timeout=20)
terminal(command="iostat -xz 1 3", timeout=20)
terminal(command="pidstat -dur 1 5", timeout=20)
```

Check installed tools first; do not install diagnostics or auto-elevate beyond scope. Reduce large outputs in code before returning them. Broad inventories use executable names, not argv/environment; full arguments can expose credentials. Even `top` may include command arguments: sanitize before capture/report. Inspect selected PIDs only when necessary.

- Ignore first since-boot vmstat/iostat summaries for recent rate claims.
- `ps %CPU` is lifetime-influenced; use interval CPU-time deltas or pidstat for current attribution.
- Docker/Linux 100% generally means one logical CPU. Consumed cores = percentage/100; host percent = percentage/logical CPU count. Calculate in code and disclose convention.
- Load includes runnable and uninterruptible work; high load plus idle CPU/I/O wait suggests blocking, not a CPU hog.
- Docker BlockIO is cumulative; sample deltas for throughput. Never add a parent container/cgroup total to its children.
- Map busy devices to live mounts/UUIDs; disk letters can change after reboot.
- Swap usage alone is not pressure; active swap rates, latency and available memory matter.

## Thermal, GPU and service gaps

Capture evidence before reboot. Correlate timestamped CPU modes, disk/PSI, temperatures, fan RPM and GPU state over repeated samples/history. A boot cold-start I/O storm can explain load without directly proving why fans spin. Cooling lag, firmware policy and physical faults remain hypotheses unless supported.

No fan/GPU series is unknown, not zero. Check exporter health and sensor labels. A loaded-versus-installed NVIDIA module mismatch explains failed NVML telemetry, not proof of GPU heat. Device clients show access, not utilization. A restart is a separately approved remediation, followed by fresh driver/exporter checks.

Investigate exact failed systemd units and their current impact. Historical failure state can remain while its underlying probe now succeeds. An inactive display manager on a text server or timesyncd with working Chrony is not automatically unhealthy. Missing SMART/NVMe tooling leaves storage wear untested; kernel logs are not a substitute. Use hardware/workload baselines rather than universal thermal/battery thresholds.

## Existing authorized CDP browser

Do not open new tabs or start another browser merely to diagnose its load. Discover the actual attachment route and supervisor. Through its authorized local/private CDP endpoint, read `/json/version` and `/json/list`; keep URLs/titles/query strings private.

On the browser WebSocket sample `SystemInfo.getProcessInfo` twice over a measured monotonic interval. Match stable PID/type and compute `100 * delta(cpuTime) / elapsed_seconds`; disclose process-churn undercount. Use `SystemInfo.getInfo` graphics metadata to identify software renderers such as SwiftShader. A GPU process can consume CPU.

Per-page Performance metrics are advisory; shared renderers and TaskDuration are not independent OS CPU measurements. Page visibility, animations/canvases and duplicate origins suggest mechanisms, not exact per-tab attribution. Navigation age is not tab age/inactivity; do not infer idle ownership from it.

## Only if tab cleanup is authorized

Inventory exact target IDs and approved scope. Preserve recent/active projects, uploads, filled controls/editors, unknown frame state and inspection failures. Recheck ID, URL and state immediately before closing each confirmed-unused target; never auto-dismiss unsaved-work warnings. Record each result incrementally, then requery and reconcile closures/new/preserved targets. Preserve cookies/profile and unrelated browser/agent processes. Repeat the same CPU/memory interval measurement after each batch; a remaining animated survivor can still dominate load. One cleanup does not install automatic lifecycle management.

Source to refresh for Hermes attachment ownership: https://hermes-agent.nousresearch.com/docs/user-guide/features/browser
