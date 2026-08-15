# Nhân Thuật 1.0.0 — Release Notes

**Version:** 1.0.0
**Release date:** August 15, 2026
**Scope:** EPIC 5 (Knowledge Engine and AI), EPIC 6 (Usable Product), EPIC 7 (Validation and Release)

---

## Highlights

Nhân Thuật 1.0.0 delivers a production-ready knowledge system: 30 frozen domain areas, 370 indexed knowledge units, a deterministic knowledge engine with real relevance scoring and citation-backed synthesis, a Vietnamese Streamlit Workbench, and a REST gateway with unit export.

## What's new in 1.0.0

### EPIC 5 — Knowledge Engine and AI
- `KnowledgeSynthesizer` (capability NHANTHUAT-CAP-002): fallback-first architecture — LLM synthesis over an OpenAI-compatible endpoint when a key is configured, deterministic retrieval-based synthesis otherwise.
- `KnowledgeResolver.resolve_scored`: real relevance scoring returning `(score, unit)` pairs.
- Ask page surfaces actual scores, synthesis mode (LLM/deterministic), citations, and audit trail (correlation_id, provider, model, latency).
- Configuration via environment: `OPENAI_API_KEY` / `NHAN_THUAT_OPENAI_API_KEY`, `OPENAI_BASE_URL` (default `https://api.openai.com/v1`), `NHAN_THUAT_LLM_MODEL` (default `gpt-4o-mini`).

### EPIC 6 — Usable Product
- REST export endpoint `GET /knowledge/units/{unit_id}/export?format=json|markdown`.
- Workbench detail page: one-click JSON/Markdown download buttons.
- Full-repository ruff lint scope passes clean (src, scripts, tests, app, backend).

### EPIC 7 — Validation and Release
- Version bumped to 1.0.0 (`pyproject.toml`, `nhan_thuat.__version__`).
- Full verification: repository validation, 100% test pass rate, lint clean, engine and API smoke tests.

## Verification evidence

| Check | Result |
| --- | --- |
| `python scripts/validate_all.py` | PASS — all managed documents valid |
| `python -m pytest` | All tests pass, 0 failures |
| `ruff check src scripts tests app backend` | All checks passed |
| Engine smoke | 370 units indexed; Vietnamese query resolution works |
| API smoke | `/knowledge/units/{id}/export` JSON 200, Markdown 200, unknown 404 |

## Operational notes

- Without an LLM key configured, synthesis runs in deterministic mode with citations — no external dependency.
- When `OPENAI_API_KEY` (or `NHAN_THUAT_OPENAI_API_KEY`) is set, provider calls are attempted first and fall back to deterministic on any failure.

## Governance

- EPIC 5, EPIC 6, EPIC 7 marked COMPLETED in `ROADMAP.md`.
- Frozen content (EPIC 0-4, Milestones, NT-BATCH-002, NT-DA-0021..0030) untouched.
- Release closed under EPIC 7. Product Owner ratification required to freeze EPIC 5/6/7.