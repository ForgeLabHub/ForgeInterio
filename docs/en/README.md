# Interio — English overview

English overview of the project. The full Russian README is
[../../README.md](../../README.md); this page covers what the project is, how to run it,
and where the details live.

## What it is

A small web application for an interior design studio: visitors take a quiz about their
flat, the studio receives a request, and an administrator moderates the flow in a panel.
FastAPI, server-side templates, static JavaScript, SQLite — one process, no external
services required.

## Run it

```bash
cp .env.example .env      # set ADMIN_CODE to a long random value
make install
make test                 # 15 tests, no network access
make run                  # http://localhost:8000/
# or, on any platform:
./forge.sh start          # linux/macos
forge.bat start           # windows
```

## What is inside

| Part | Where | What you can borrow |
| --- | --- | --- |
| Configuration from the environment | `app/config.py` | one `settings()` call, no import-time state |
| SQLite layer without an ORM | `app/db.py` | idempotent schema, cursor with commit |
| Passwords, sessions, roles | `app/security.py` | cookie sessions, fail-closed admin code |
| E-mail with attachments | `app/mailer.py` | optional feature that degrades quietly |
| HTTP layer | `app/routers/` | one router per responsibility |
| Control scripts | `forge.sh`, `forge.bat` | start/stop/doctor/logs/env in one command |

Module borrowing map: [modules/module-map.md](modules/module-map.md).

## Documentation

- [index.md](index.md) — map of all documents
- [BUILD.md](BUILD.md), [verification/matrix.md](verification/matrix.md),
  [security/secrets.md](security/secrets.md)
- PDF of every document: [../pdf/](../pdf/)

## Licence

MIT — see [../../LICENSE](../../LICENSE).
