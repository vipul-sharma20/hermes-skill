# Metrics and exact sample times

## Select the correct source

| Claim | Evidence |
|---|---|
| Registered management targets | Successful inventory collection with pagination, not exporter count |
| Currently reachable target | Timestamped management probe plus a separate live path where possible |
| Running Docker containers | Host runtime state; cAdvisor is an explicitly qualified estimate |
| Available host memory | Linux MemAvailable, not MemFree |
| Stopped service | Exact child/container terminal state, not lingering Prometheus series |

A Coolify application encryption APP_KEY is not an API bearer token. Use a scoped token from the exact trusted installation. A failed credential proves neither host outage nor an empty inventory.

## Grafana proxy discovery

Legacy `/api` routes are deprecated in current Grafana documentation but remain operative. Check the installed version and its supported datasource/proxy route before use; there may be no exact replacement in the newer `/apis` API. Do not rewrite a working route merely by substituting its prefix.

Use the existing approved authenticated client through `terminal`, suppressing credentials and raw privileged payloads. Verify TLS and target origin; never forward auth on an unreviewed redirect.

1. Discover `GET /api/datasources`; select the intended Prometheus datasource, not the first match.
2. Retain its UID and use the installed Grafana version's supported route, commonly `GET /api/datasources/proxy/uid/<uid>/api/v1/query`.
3. URL-encode PromQL, validate JSON status/result type and inspect actual labels before filtering.
4. Match exporter/job/instance as well as host. `up == 1` for one exporter does not prove every exporter or application works.

Query shapes, with actual labels substituted by the operator:

```promql
node_memory_MemTotal_bytes{server="TARGET"}
node_memory_MemAvailable_bytes{server="TARGET"}
100 * (1 - node_memory_MemAvailable_bytes{server="TARGET"} / node_memory_MemTotal_bytes{server="TARGET"})
node_memory_SwapTotal_bytes{server="TARGET"}
node_memory_SwapFree_bytes{server="TARGET"}
rate(container_cpu_usage_seconds_total{server="TARGET",name!=""}[5m])
container_memory_working_set_bytes{server="TARGET",name!=""}
```

Compute bytes/GiB and utilization with code; host usage includes kernel/cache/noncontainer overhead. Container working set, RSS and total usage differ. Evaluate min/average/max, restart and OOM evidence across appropriate windows before hypothesizing a leak. Flat high memory alone is not a leak. JVM heap ergonomics require actual cgroup/runtime flags, not guesswork from host RAM.

## Identity and freshness

A name can be reused; deduplicate exporter replicas by validated host/runtime/container ID. Never blindly sum relabeled duplicates or collapse distinct same-named containers. Empty names often represent system cgroups, but nonempty names alone do not guarantee unique running containers. `last_over_time(container_last_seen[window])` returns recent observed series, not a definitive running count; choose a window from scrape intervals and compare actual last-seen values.

For an exact historical last sample, submit a bounded raw range vector to the instant `/api/v1/query` endpoint, for example `node_load1{server="TARGET"}[2h]`. Read each matrix series' actual `values` timestamp/value pairs. `last_over_time` result timestamps describe evaluation time; regular range-query evaluation steps can also repeat samples through lookback. Do not call either the exact source failure time.

Keep per-series times when status lives in labels: an older Charging/Full or network-state series may coexist with a newer one. Convert epochs/timezones in code. A final normal OOM/thermal reading cannot exclude a sudden event after telemetry stopped.

## Checks and sources

Require successful response, exact target, expected cardinality, freshness and appropriate exporter health. Missing data is unavailable, never healthy zero.

- https://prometheus.io/docs/prometheus/latest/querying/api/
- Official source fallback: https://raw.githubusercontent.com/prometheus/prometheus/main/docs/querying/api.md
- https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/api-legacy/data_source/
- https://coolify.io/docs/api/overview
