# Data storage

English version of [../database.md](../database.md).

SQLite, path from `DB_PATH` (default `data.db`). The schema is created at start-up
idempotently: `CREATE TABLE IF NOT EXISTS` plus `ALTER TABLE ... ADD COLUMN` inside
`try/except`. All of it lives in `app/db.py`.

## Tables

| Table | Contents | Owner |
| --- | --- | --- |
| `users` | phone, nickname, password hash, role | authentication |
| `sessions` | session token, user, expiry | authentication |
| `quiz_submissions` | quiz request (contacts, room parameters, status) | quiz/admin |

## Rules

1. **Passwords are stored hashed only** (`hash_password`), at least 8 characters and at
   least one letter (`validate_password`) — enforced by tests.
2. **A session is an HttpOnly cookie** `session_id`, `SameSite=lax`, 7 days.
3. **The role changes only through admin sign-in with a code from the environment**;
   without `ADMIN_CODE` the route answers 503 (fail closed).
4. **Tests never touch the production database**: `DB_PATH` points to a temporary file.

## Backup

```bash
sqlite3 data.db ".backup 'backups/interio-$(date -u +%Y%m%dT%H%M%SZ).db'"
```

Restore: stop the application, replace the file, start it, run `make smoke-test`. On
Render use a disk or re-create the database from the request export.

## Verification

| Claim | How it is checked |
| --- | --- |
| The schema is created on an empty database | every test boots the app on an empty `DB_PATH` |
| Re-running the initialisation is safe | `init_db()` runs on every start and in tests |
| The password is never stored in clear text | `tests/test_auth.py` and review of `hash_password` |
