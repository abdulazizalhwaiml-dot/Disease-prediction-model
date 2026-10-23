# Security and deployment boundaries

The app processes measurements in memory for the current Streamlit session. It does
not persist patient records, invoke an external AI service, or log input measurements.
Streamlit usage telemetry is disabled. Hosts and reverse proxies must also avoid
collecting request bodies, websocket payloads or session memory dumps.

For an exposed deployment, use a TLS-terminating reverse proxy with authentication,
appropriate access restrictions and session timeouts. Streamlit itself supplies no
clinical user authorization or electronic health-record controls. Keep CORS and XSRF
protection enabled. Set resource limits for worker memory and concurrent SHAP requests.

The container runs as a non-root user. Treat the source and model directories as
read-only. Load only trusted model artifacts. Hash checks detect accidental corruption,
not malicious replacement of both an artifact and its manifest. Dependencies are pinned
with verified hashes; review security updates, regenerate locks and retrain/revalidate
before changing model-runtime dependencies.

Use GitHub private vulnerability reporting if enabled by the repository owner; never
include patient measurements, credentials or private records in a public issue.
