# Verification matrix

English version of [../../verification/matrix.md](../../verification/matrix.md).

| Check | What it proves | Command | CI |
| --- | --- | --- | --- |
| Tests (15) | authentication, the quiz and the protective properties work | `make test` | `ci.yml` → `tests` |
| ruff | static rules are respected across `app/`, `server.py`, `tools/` | `make lint` | `ci.yml` → `tests` |
| Security regressions | no password in code, no wildcard CORS, admin code from the environment | `make test` | `ci.yml` → `tests` |
| Start without optional configuration | works without SMTP and without `ADMIN_CODE` (admin sign-in answers 503) | start + `/` | `ci.yml` → `runtime` |
| Smoke test of a live instance | routes answer, admin data is closed | `make smoke-test` | manually after deploy |
| Documentation is consistent | links are alive, module specifications are complete, every document has a translation and a PDF | `make docs-check` | `ci.yml` → `docs` |
| Host check | environment and secrets are in order before start-up | `make doctor` | locally |

## What is not checked automatically

- Deployment to Render: `render.yaml` exists, but the deploy is not automated in CI.
- `data.db` survival across host restarts — depends on an attached disk.
- Behaviour under load and password brute force (no rate limiting implemented).
