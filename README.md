# NaVro

Embeddable search infrastructure — a developer-first, plug-and-play search
system for apps, websites, and SaaS products.

> A developer should be able to add high-quality search to their product
> without building their own search infrastructure.

## Status: M0 — Foundation

The repo currently contains only the pieces needed for the M0/M1 loop
(Create Index → Add Documents → Search → Rank → Return Results). Folders
for the widget, dashboard, and SDKs are added as their milestones start —
see [`docs/spec.md`](docs/spec.md) for the full milestone sequence.

## Docs

- [`docs/spec.md`](docs/spec.md) — core objects, API contract, search
  pipeline, non-goals, and milestone roadmap. Start here.

## Backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

Then check `GET /health`.

## Milestones

```text
M0  Foundation        repo + architecture + spec        <- we are here
M1  Search Engine      storage, indexing, query, rank
M2  API                REST interface around the engine
M3  Quality             benchmark dataset, keyword -> hybrid
M4  Widget              embeddable JS search component
M5  Dashboard           index/doc management, API keys, playground
```
