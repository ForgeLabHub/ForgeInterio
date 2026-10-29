# Interio documentation

English version. The canonical (Russian) set is in [../index.md](../index.md);
the two are kept in step and both are shipped as PDF in [../pdf/](../pdf/).

| Question | Document |
| --- | --- |
| Run it from scratch | [BUILD.md](BUILD.md) |
| How the application is built | [architecture/system-context.md](architecture/system-context.md) |
| Where the data lives | [database.md](database.md) |
| API and error codes | [api/conventions.md](api/conventions.md) |
| What a module does / what to borrow | [modules/](modules/) |
| Deployment | [operations/deployment.md](operations/deployment.md) |
| Monitoring | [operations/monitoring.md](operations/monitoring.md) |
| **Secrets: what was fixed** | [security/secrets.md](security/secrets.md) |
| What proves it works | [verification/matrix.md](verification/matrix.md), CI |
| What the audit changed | [audit/portability-audit-2026-10-29.md](audit/portability-audit-2026-10-29.md) |

## Rules

1. A claim without a check is just a promise — see
   [verification/matrix.md](verification/matrix.md).
2. No secrets in code. Configuration comes from the environment only
   (`../.env.example`).
3. Tests never touch the network or the production database: `DB_PATH` is replaced in
   `tests/conftest.py`, `KEEP_ALIVE_ENABLED=false`.
4. The code is split into modules under `app/` (`config`, `db`, `security`, `mailer`,
   `models`, `routers/*`); `server.py` only assembles and runs them. What to borrow and
   from where: [modules/module-map.md](modules/module-map.md).

## Project control

- `forge.sh` / `forge.bat` start, stop, tail logs, run tests, manage the database and
  containers in one command; see the README section.
