# Monitoring

English version of [../../operations/monitoring.md](../../operations/monitoring.md).

| Signal | Where | Purpose |
| --- | --- | --- |
| `GET /` | application | Render health-check (`healthCheckPath: /`) |
| stdout logs | process | route errors, keep-alive messages |
| `quiz_submissions` table | SQLite | request flow and statuses |
| keep-alive log | stdout, when enabled | diagnosing sleep on the free tier |

## Minimal alerts

1. `/` does not answer for 2 minutes (Render restarts the service by itself).
2. The 5xx share is above 1% over 5 minutes.
3. SMTP errors while credentials are configured.
4. A growing number of 409 responses on sign-up — brute force or a client bug.

## What is missing

- No `/metrics`, no tracing, no SLO.
- No structured logs: free-form printing to stdout.
- No notification about new requests apart from e-mail (if configured).
