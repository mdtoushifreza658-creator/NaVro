# NaVro — V1 Technical Specification

> **Status note:** Sections 1–3 (Core Objects, API Contract, Response Shape) are
> load-bearing — every later component depends on them, so changes here are
> expensive. Sections 4+ (ranking approach, storage internals) are current
> thinking, not commitments — they're expected to change once we have real
> benchmark data. Don't let them block coding.

---

## 1. One-sentence definition

A developer-first, embeddable search infrastructure that lets websites and
applications add fast keyword, semantic, and hybrid search without building
their own search engine.

---

## 2. Core objects

```text
Project
 └── Index
      └── Document
```

**Project**
The top-level tenant boundary. Owns one or more Indexes. Authenticated via
an API key. All requests are scoped to a Project — no cross-project reads.

| field       | type      | notes                          |
|-------------|-----------|---------------------------------|
| id          | uuid      | primary key                     |
| name        | string    | human-readable                  |
| api_key     | string    | hashed at rest, shown once      |
| created_at  | timestamp |                                  |

**Index**
A named, isolated collection of Documents belonging to one Project. Roughly
equivalent to a "table" or "collection" — e.g. `products`, `articles`.

| field       | type      | notes                          |
|-------------|-----------|---------------------------------|
| id          | uuid      | primary key                     |
| project_id  | uuid      | foreign key                     |
| name        | string    | unique within a project          |
| created_at  | timestamp |                                  |

**Document**
A single searchable record. V1 keeps the schema flexible (title, content,
plus arbitrary metadata) rather than enforcing a rigid field set per index —
strict per-index schemas can come later if needed.

| field       | type      | notes                                      |
|-------------|-----------|---------------------------------------------|
| id          | string    | developer-supplied, unique within an index   |
| index_id    | uuid      | foreign key                                  |
| title       | string    | primary searchable field                     |
| content     | text      | secondary searchable field                   |
| url         | string    | optional, returned but not searched          |
| metadata    | jsonb     | optional, developer-defined, filterable later|
| created_at  | timestamp |                                               |

---

## 3. API contract (V1)

```text
POST   /indexes
POST   /indexes/{id}/documents
POST   /indexes/{id}/documents/bulk
DELETE /indexes/{id}/documents/{doc_id}

POST   /search
```

### `POST /indexes`
Request:
```json
{ "name": "articles" }
```
Response:
```json
{ "id": "idx_abc123", "name": "articles", "created_at": "2026-08-21T00:00:00Z" }
```

### `POST /indexes/{id}/documents`
Request:
```json
{
  "id": "article_123",
  "title": "Introduction to Machine Learning",
  "content": "Machine learning is a subset of AI...",
  "url": "/articles/ml-introduction",
  "metadata": { "category": "technology" }
}
```
Response: `201 Created`, echoes the stored document.

### `POST /indexes/{id}/documents/bulk`
Request: `{ "documents": [ {...}, {...} ] }`
Response: count inserted + any per-document errors (partial failure allowed).

### `DELETE /indexes/{id}/documents/{doc_id}`
Response: `204 No Content`.

### `POST /search` — the core contract
Request:
```json
{
  "index": "articles",
  "query": "machine learning",
  "limit": 10,
  "offset": 0
}
```
Response:
```json
{
  "results": [
    {
      "id": "article_123",
      "title": "Introduction to Machine Learning",
      "url": "/articles/ml-introduction",
      "score": 0.94
    }
  ],
  "total": 1,
  "took_ms": 12
}
```

**This response shape is fixed for V1.** `score` is always a float, always
present, always comparable *within a single response* — but the scoring
method behind it (keyword-only now, hybrid later) is free to change without
breaking clients, since clients only ever consume rank order + score, never
the internals that produced it.

### Error envelope — fixed for V1

Every non-2xx response uses the same shape, regardless of which endpoint or
what went wrong:

```json
{
  "error": {
    "code": "not_found",
    "message": "Index 'articles' not found",
    "details": null
  }
}
```

`code` is a stable machine-readable string clients can branch on (e.g. show
a specific UI state for `validation_error` vs `unauthorized`). `details` is
present only for `validation_error` and holds a list of
`{ "field": "...", "issue": "..." }` objects — one per invalid field.

| HTTP status | `code`             | when                                    |
|-------------|--------------------|------------------------------------------|
| 401         | `unauthorized`      | missing/invalid API key                  |
| 404         | `not_found`         | index or document doesn't exist          |
| 409         | `conflict`          | index name already exists                |
| 422         | `validation_error`  | request body fails schema validation     |
| 500         | `internal_error`    | unhandled server error                   |

### Pagination limits — fixed for V1

`limit` is clamped to 1–100 (rejected with `validation_error` outside that
range, not silently clamped). `offset` must be ≥ 0. There's no cursor-based
pagination in V1 — offset/limit is enough for the document counts V1 targets.

---

## 4. Search pipeline (behavioral contract, not implementation)

```text
Document
   ↓
Normalize        (lowercase, strip control chars)
   ↓
Index            (make it queryable)
   ↓
Query            (parse incoming search string)
   ↓
Retrieve         (find candidate documents)
   ↓
Rank             (order candidates by relevance)
   ↓
Results
```

What V1 promises, independent of implementation:
- A query that shares exact words with a document's title/content retrieves
  that document.
- Results are returned ordered by relevance, most relevant first.
- Typo tolerance and semantic matching are **not** promised in M1 — they
  arrive in M3.

What V1 deliberately does **not** promise yet:
- Any specific ranking formula (BM25 vs `ts_rank` vs anything else is an
  implementation detail, swappable behind the contract above).
- Sub-second indexing latency guarantees.
- Multi-field weighting (title vs content) — may arrive as a config option
  after M1, not before.

---

## 5. Non-goals for V1

Explicitly out of scope, revisit only in V2+:

- ❌ LLM answers / chatbot / conversational search
- ❌ AI agents
- ❌ Web crawling
- ❌ Personalized / behavioral ranking
- ❌ Recommendation engine
- ❌ Enterprise SSO / complex billing
- ❌ Massive distributed / multi-region infrastructure
- ❌ SDKs beyond REST + JS widget (no `navro-python`, `navro-flutter`, etc. yet)
- ❌ CMS plugins (WordPress, Shopify, Webflow)

---

## 6. Integration surface (V1)

Two paths only, both sitting on the same REST API:

1. **REST API** — canonical, framework-agnostic, works from any language
   or platform that can make HTTP requests.
2. **JavaScript widget** — a thin client that calls the REST API and
   renders a search box + results dropdown. The widget must never contain
   search logic itself; it is purely a UI shell over `/search`.

SDKs, plugins, and framework-specific packages are V1.5+ distribution
channels, not part of the engine.

---

## 7. Milestones

```text
M0 — Foundation
     Repository + architecture + this spec

M1 — Search Engine
     Storage → indexing → querying → ranking (keyword only)

M2 — API
     REST interface around the engine

M3 — Quality
     Test dataset + relevance benchmarks
     Keyword → hybrid/vector, ranking fusion chosen from benchmark results

M4 — Widget
     Embeddable JavaScript search component

M5 — Dashboard
     Index management, documents, API keys, search playground, basic usage
```

M1's target loop, nothing more:

```text
Create Index → Add Documents → Search → Rank → Return Results
```

No dashboard, no widget, no LLM in M1.

---

## 8. Quality benchmark (M3, defined early so M1 code doesn't drift from it)

A benchmark file — `backend/tests/benchmark_queries.json` — of ~20-30
`{query, expected_doc_ids}` pairs against a fixed test dataset, scored with
precision@5 and recall@5. Any ranking change (keyword tuning, hybrid fusion
method, etc.) must be evaluated against this file before being adopted. This
turns "does search feel better" into a measurable before/after.
