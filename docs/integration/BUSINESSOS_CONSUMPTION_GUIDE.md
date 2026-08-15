# BusinessOS Consumption Guide

**Document ID:** `DOC-INT-002`
**Version:** v1.1.0 (updated for NhanThuat 1.0)

## Consuming NhanThuat

BusinessOS acts as the operational orchestrator. When querying NhanThuat for knowledge, you must use the adapter provided in `nhan_thuat.public.v1.adapter`.

### 1. Initialization

```python
from nhan_thuat.public.v1.adapter import KnowledgeEngineAdapterV1

provider = KnowledgeEngineAdapterV1()
```

### 2. Querying Knowledge

```python
from nhan_thuat.public.v1 import KnowledgeQuery

query = KnowledgeQuery(domain_slug="human-nature", limit=10)
result = provider.query_knowledge(query)

print(f"Total Matches: {result.total_matches}")
for unit in result.units:
    print(unit.title)
```

### 3. Handling Capabilities

Check if a capability is implemented before invoking it:

```python
capabilities = provider.list_capabilities()
for cap in capabilities:
    if cap.status == "IMPLEMENTED":
        # Safe to use
        pass
```

## 4. NhanThuat 1.0 Additions

- **Domain scope:** 30 domain areas (`NT-DA-0001`..`NT-DA-0030`, categories
  CAT-CORE / CAT-BEHAVIORAL / CAT-APPLIED) and 370 frozen knowledge units,
  including the new `phenomenon` type (Hiện tượng hành vi).
- **Domain filtering:** unit-level `primary_domain` drives engine indexing; the
  optional `domain_area` field (`^NT-DA-[0-9]{4}$`) links a unit to a domain
  registry id. Both `domain_slug` (lens) and `domain_area` queries are valid.
- **Relations:** the `relations` block is semantic/bidirectional metadata and is
  excluded from dependency-graph traversal.
- **Runtime:** `src/nhan_thuat/runtime/` provides graph traversal, keyword
  resolver (confidence scores), prompt builder, and heuristic evaluator.
- **LLM synthesis (`NHANTHUAT-CAP-002`):** fallback-first; see
  `docs/architecture/KNOWLEDGE-ENGINE-RUNTIME.md` §5.
- **Export:** unit/domain export endpoints are available under
  `/knowledge/units/{unit_id}/export` (JSON or Markdown).

## 5. REST Endpoints

See `backend/app/main.py` docstring: `/health`, `/version`, `/knowledge/*`
(units, domains, query, export), `/runtime/*` (execute, provenance), and
`/salesos/*`. Responses are `application/json; charset=utf-8`.
