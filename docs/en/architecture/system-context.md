# System context

English version of [../../architecture/system-context.md](../../architecture/system-context.md).

## What this is

Interio is a small web application for interior design selection: sign-up and sign-in,
an interactive quiz, and an admin panel for requests. One FastAPI process, server-side
templates, static files, SQLite.

## Context diagram

```
   +------------+        +--------------+
   |  Visitor   |        | Administrator|
   +-----+------+        +------+-------+
         | HTTPS                | HTTPS (access code)
         v                      v
   +------------------------------------------+
   | app/ - FastAPI                           |
   |  /            application page           |
   |  /quiz        quiz                       |
   |  /admin       admin panel                |
   |  /api/auth/*  sign-up, sign-in, sessions |
   |  /api/quiz/*  requests                   |
   |  /api/admin/* request moderation         |
   +-----+--------------------------+---------+
         |                          | optional
         v                          v
   +------------+            +--------------+
   | SQLite     |            | SMTP (Gmail) |
   | data.db    |            | e-mail       |
   +------------+            +--------------+
```

## Modules of the `app/` package

The code is organised by responsibility; every module can be taken to another project
on its own (borrowing map: [../modules/module-map.md](../modules/module-map.md)).

| Module | Responsibility | Depends on |
| --- | --- | --- |
| `app/config.py` | environment reading, `settings()`, server address | nothing |
| `app/db.py` | SQLite schema, connection, cursor with commit | `config` |
| `app/security.py` | passwords, sessions, cookies, role checks, admin code | `db`, `config` |
| `app/mailer.py` | SMTP, attachments, "mail disabled" without configuration | `config` |
| `app/models.py` | Pydantic request and response models | nothing |
| `app/routers/auth.py` | sign-up, sign-in, sign-out, current user | `db`, `security`, `models` |
| `app/routers/quiz.py` | request validation and storage, background e-mail | `db`, `mailer`, `models` |
| `app/routers/admin.py` | request list and status change (admin role only) | `db`, `security`, `models` |
| `app/routers/pages.py` | HTML pages and quiz state stubs | `models` |
| `app/keepalive.py` | self-ping (optional) | `config` |
| `server.py` | `create_app()` + `uvicorn.run`, import compatibility | everything |

Rule: the HTTP layer never talks to the database on its own — only through `app.db`,
and password/session rules live in exactly one place (`app.security`).

## Supported scope

Declared: Python 3.11+, Linux/Render, a browser. Not declared: several replicas (SQLite
is a single file, sessions live in the same database), other DBMS, running without a
filesystem.
