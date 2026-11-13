# Upload size, duration and client deadlines

Map the actual client surface through DNS/TLS/network family, negotiated HTTP protocol, ingress body read, upstream transport, application HTTP/multipart/decoder, storage and later bot/provider processing. A dashboard cap cannot fix a different messaging client's upload path.

Record decoded size, wire size, per-request/resource/idle/response deadlines and which component owns each. Base64 JSON expands payload; calculate actual encoded/wire length with code rather than conflating bytes, MB and MiB. Verify downstream provider resize behavior separately from upload acceptance.

## Paired red-capable probes

After approval for disposable storage and data transfer:
1. Use one deterministic valid fixture; random bytes with an image extension confound decoding.
2. Upload at full speed over the actual public hostname/protocol.
3. Download complete bytes and validate size/hash.
4. Repeat with realistic rate limiting to cross the suspected deadline.
5. Correlate elapsed time, bytes, HTTP version/status, request IDs, app/proxy errors and simultaneous WebSocket closures.
6. Clean up through the documented path; do not repeatedly generate orphan large files without a cleanup policy.

| Evidence | Supports, but does not alone prove |
|---|---|
| Fast/slow fail at same byte count | Size/content boundary |
| Fast works, slow fails near stable time | Client/proxy/application timer |
| No application request record | Failure before that boundary |
| Multipart unexpected EOF | Body ended early; correlate who closed it |
| Upload OK, no attached message | File association or downstream processing |
| Download truncates | Storage/response path |

## Fix the demonstrated timer, not a nearby one

Traefik entrypoint `transport.respondingTimeouts.readTimeout` covers incoming body reads. ServersTransport responseHeaderTimeout concerns upstream response headers. Recheck current defaults/live config; do not install a historical fixed timeout. A global entrypoint change affects neighbors and increases slow-client occupancy.

A native upload's request-specific deadline can override session/global defaults. Inspect current client source and version: server-side increases cannot extend a client that has already aborted. Later unexpected EOF after a proxy fix may be a second boundary. Do not infer a constant from a version-unmatched anecdote.

Back up exact configuration, change one proven boundary through its owning control plane, poll actual restart/readiness, compare neighbors and rerun the same throttled failure. A quick local upload and health check are not sufficient proof. Preserve trusted TLS and authentication throughout.

Sources to refresh:
- https://doc.traefik.io/traefik/reference/install-configuration/entrypoints/
- https://docs.mattermost.com/administration-guide/configure/environment-configuration-settings
- https://github.com/mattermost/mattermost-mobile
