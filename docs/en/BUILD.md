# Build and run

English version of [../../BUILD.md](../../BUILD.md).

## Pinned versions

| Tool | Version | Source of truth |
| --- | --- | --- |
| Python | 3.11+ (verified on 3.13) | `render.yaml`, `README.md` |
| Runtime dependencies | exact versions (`==`) | `requirements.txt` |
| Dev dependencies | exact versions (`==`) | `requirements-dev.txt` |
| httpx | 0.27.x | otherwise `TestClient` is incompatible with FastAPI 0.104 |

## Level A — source code

```bash
make doctor    # tools, dependencies, configuration, no secrets in code
make install
make lint
make test      # 15 tests; no network access
make docs-check
```

## Level B — run

```bash
cp .env.example .env     # set ADMIN_CODE
make run                 # uvicorn on port 8000
```

There is no build artefact: the application is interpreted.

## Level C — check a live instance

```bash
make smoke-test BASE_URL=http://localhost:8000
```

## Level D — CI

`ci.yml` runs three jobs: tests and lint (`ruff` + `pytest`), a runtime job that boots
the application without optional configuration, and a docs job (`make docs-check`).

## Level E — documentation as artefacts

```bash
make docs-pdf    # Markdown -> PDF for both languages, output in docs/pdf/
```

The script `tools/docs_pdf.py` refuses to build if a document has no translation
(`--check`), so the bilingual set cannot silently drift apart.
