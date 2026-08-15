# Knowledge Engine & Runtime Architecture

**Document ID:** `DOC-ARCH-011`
**Applies to:** `src/nhan_thuat/` + `app/` + `backend/app/engine/`
**Status:** CURRENT (NhanThuat 1.0)

## 1. Overview

Knowledge content lives in `knowledge/`, schemas in `schemas/`, and the
deterministic Python engine in `src/nhan_thuat/`. API adapters and the Streamlit
Workbench consume the engine; they are not a source of content.

## 2. Knowledge Engine (`src/nhan_thuat/knowledge_engine.py`)

- Loads all YAML units under `knowledge/units/` (370 units as of 1.0).
- **Domain index keys on `primary_domain`** (`data.get("primary_domain") or
  data.get("domain", "unassigned")`), so domain queries and filtering return
  real results. The legacy `domain` field is not used for indexing.
- The `relations` block is **semantic and bidirectional** (e.g. anti-pattern ↔
  law mutual references) and is **excluded from dependency-graph traversal**;
  including it would create false cycles.

## 3. Runtime Components (`src/nhan_thuat/runtime/`)

| Module | Responsibility |
| --- | --- |
| `graph.py` | `KnowledgeGraph`: transitive traversal + cycle detection |
| `resolver.py` | `KnowledgeResolver`: keyword-overlap scoring (used for real confidence scores) |
| `prompt_builder.py` | `PromptBuilder`: markdown context assembly for synthesis |
| `evaluator.py` | `KnowledgeEvaluator`: heuristic risk assessment |

## 4. Public Contract V1 (`src/nhan_thuat/public/v1/`)

- Stable, immutable typed boundary (`dataclass(frozen=True)`): `KnowledgeQuery`,
  `KnowledgeResult`, `KnowledgeUnitSummary`, provider adapter, capability
  descriptors, and `PublicError` family.
- Consumers MUST import from `nhan_thuat.public.v1` and never from the engine.

## 5. LLM Synthesis (EPIC 5, capability `NHANTHUAT-CAP-002`)

- **Fallback-first design:** synthesis reads an OpenAI-compatible key from
  `.streamlit/secrets.toml` / env. If no key is present the ask page returns the
  deterministic retrieval flow (resolver scores, citations, audit); with a key
  it additionally calls the configured provider via `requests`.
- Every result carries citations (unit id/title), confidence (resolver score),
  and an audit record (correlation_id, provider, prompt, latency).

## 6. Workbench & API

- **Streamlit Workbench** (`app/`, `scripts/run_web_dashboard.py`): 6 Vietnamese
  pages over `EngineAdapter` (`app/services/engine_adapter.py`).
- **REST Gateway** (`backend/app/main.py`): `/health`, `/version`,
  `/knowledge/*`, `/runtime/*`, `/salesos/*`, plus export endpoints.

## 7. Validation

`scripts/validate_all.py` validates all managed documents; `pytest` covers
engine, runtime, contract, workbench, and API behaviour. See CI workflow.