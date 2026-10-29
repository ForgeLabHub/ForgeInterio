# Code style and lint

English version of [../../development/code-style.md](../../development/code-style.md).

## What is checked

| Tool | Version | Configuration | Where it runs |
| --- | --- | --- | --- |
| ruff | `ruff==0.8.4` (`requirements-dev.txt`) | `ruff.toml` | `make lint`, CI job "Tests and lint" |
| pytest | `python -m pytest -q` | `tests/conftest.py` | `make test`, CI |

The configuration lives in the repository, not in an editor: `ruff.toml` sets
`line-length`, `target-version = "py311"` and the rule set `E4,E7,E9,F` (errors and
potential bugs). The ruff version is pinned, so `make lint` gives the same result locally
and in CI.

## Why the rule set is narrow

The code is split into `app/` modules now, but historical heritage remains: broad
`except Exception` in background tasks and files opened without context managers.
Enabling `BLE`, `SIM`, `PLW` produces findings that cannot be fixed in one move without
risking behaviour. Therefore:

1. Blocking are the rules that catch real errors.
2. `docs/audit/portability-audit-2026-10-29.md` records the style debt.

## How to tighten

1. Take one rule (for example `BLE001`).
2. Add it to `select`, put `# noqa: BLE001` with a comment where the broad catch is
   intentional (keep-alive, sending e-mail).
3. Remove `noqa` where the exception type can be narrowed.
4. Only then extend `select` further.

## Local commands

```bash
make lint    # ruff over app/, server.py, tests/ and tools/
make test    # pytest, no network, no secrets
make check   # lint + test + docs-check
```
