# Deployment

English version of [../../operations/deployment.md](../../operations/deployment.md).

## Options

| Option | File | Note |
| --- | --- | --- |
| Render.com | `render.yaml` | Python 3.11, `python server.py`, health-check `/` |
| Local | `make run` | uvicorn on port 8000 |
| Windows | `start.bat` | for local development |

## Procedure

```bash
cp .env.example .env      # set ADMIN_CODE
make doctor
make install
make test                 # 15 tests, no network access
make run
make smoke-test           # in another terminal
```

## Before going public

1. `ADMIN_CODE` — a long random code (not `ADMIN123`).
2. If e-mail is needed, set `SMTP_USERNAME`/`SMTP_PASSWORD` (a new app password; revoke
   the old one).
3. `CORS_ORIGINS` — the exact domain if the frontend is served from elsewhere.
4. `KEEP_ALIVE_ENABLED=true` only on a free tier that sleeps the service.
5. `data.db` must live on a persistent disk: on Render without a disk the database is
   lost on restart. That is a hosting limitation, not an application one.
6. A single process: SQLite and sessions are not designed for several replicas.

## After deployment

```bash
make smoke-test BASE_URL=https://<domain>
```

The smoke test separately checks that `/api/admin/submissions` is **not** reachable
without the admin role — a guard against the privilege-escalation regression.
