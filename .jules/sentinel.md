## 2024-05-23 - Default Network Binding Exposure
**Vulnerability:** The application was binding to `0.0.0.0` by default, exposing the backend and UDP listener to all network interfaces.
**Learning:** Development tools often default to wide open network bindings for convenience, but this poses a security risk if the tool runs on a machine connected to untrusted networks (e.g., public Wi-Fi).
**Prevention:** Default to `127.0.0.1` (localhost) for all network listeners. Provide an explicit configuration option (e.g., environment variable) to allow users to opt-in to wider exposure if needed.
