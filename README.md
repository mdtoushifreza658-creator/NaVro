# NaVro

Embeddable search infrastructure — a developer-first, plug-and-play search
system for apps, websites, and SaaS products.

> A developer should be able to add high-quality search to their product
> without building their own search infrastructure.

## Status: M2 — API hardening (working)

On top of M1's working loop: a consistent error envelope on every non-2xx
response, input validation (index name format, field lengths, non-blank
queries), and clamped pagination (`limit` 1–100, `offset` ≥ 0). See
`docs/spec.md` Section 3 for the fixed error/pagination contract.

Folders for the widget, dashboard, and SDKs are added as their milestones
start — see [`docs/spec.md`](docs/spec.md) for the full milestone sequence.

## Docs

- [`docs/spec.md`](docs/spec.md) — core objects, API contract, search
  pipeline, non-goals, and milestone roadmap. Start here.

## Backend

### Prerequisites
A running Postgres instance, reachable via the connection string in
`app/core/config.py` (override with the `NAVRO_DATABASE_URL` env var).
Create the `navro` database once:
```bash
createdb navro
```

### Setup
```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Seed a project (dev-only, no /projects endpoint yet)
```bash
.venv/bin/python scripts/seed_project.py "My Project"
# prints an X-Navro-Api-Key value — save it
```

### Run
```bash
.venv/bin/uvicorn app.main:app --reload
```
Tables are created automatically on startup. Check `GET /health`.

### Try the loop
```bash
KEY="<api key from seed script>"

curl -X POST localhost:8000/indexes \
  -H "X-Navro-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"name": "articles"}'

curl -X POST localhost:8000/indexes/<index_id>/documents \
  -H "X-Navro-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"id": "a1", "title": "Introduction to Machine Learning", "content": "..."}'

curl -X POST localhost:8000/search \
  -H "X-Navro-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"index": "articles", "query": "machine learning"}'
```

## Milestones

```text
M0  Foundation        repo + architecture + spec
M1  Search Engine      storage, indexing, query, rank      (V0 search working)
M2  API                REST interface around the engine    <- we are here (validation + error envelope)
M3  Quality             benchmark dataset, keyword -> hybrid
M4  Widget              embeddable JS search component
M5  Dashboard           index/doc management, API keys, playground
```
