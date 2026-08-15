# M16 REVIEW PACKAGE — KNOWLEDGE EXPANSION & KNOWLEDGE WORKBENCH

**Document ID:** `DOC-REP-M16-001`
**Execution Date:** August 14, 2026
**Status:** **APPROVED BY PRODUCT OWNER (2026-08-14)**

## 0. Approval Record

- **Decision:** Approved in full by Product Owner on August 14, 2026.
- **Effect:** NT-BATCH-002 frozen; NT-DA-0021 through NT-DA-0030 frozen with all 96 units; `docs/domains/*/status.yaml` for the ten new domains stamped `frozen` (frozen_at 2026-08-14); frozen register updated.
- **Post-approval change control:** G3 (reformatted frozen status.yaml) accepted as change control record; G5 (anti-patterns 3xxx) confirmed deferred to backlog; G7 (EPIC 5 scope) acknowledged — LLM integration tracked under capability NHANTHUAT-CAP-002.

## 1. Purpose

This package documents the M16 batch: knowledge expansion from 20 to 30 domain areas (96 new units), the knowledge runtime components, and the Streamlit Knowledge Workbench. It consolidates all changes, governance decisions, and the evidence needed for Product Owner review.

## 2. Scope of Changes

| Area | Detail |
| --- | --- |
| **Knowledge units** | 96 new units: NT-DA-0021..0030 (laws 82, principles 134, models 45, anti-patterns 60, phenomena 49 total across 370 units) |
| **Domain registry** | Added 10 domains (NT-DA-0021..0030) and 3 categories (CAT-CORE, CAT-BEHAVIORAL, CAT-APPLIED) |
| **Schema** | `phenomenon` type, `domain_area` metadata field (optional, `^NT-DA-[0-9]{4}$`) |
| **Runtime** | `src/nhan_thuat/runtime/`: graph, resolver, prompt_builder, evaluator |
| **Workbench** | Streamlit app (`app/`) with 6 pages, Vietnamese localization |
| **Engine fix** | Domain index now reads `primary_domain` (was unassigned for all units) |
| **Tests** | 145 tests passing; runtime/UI/localization tests added |

## 3. Governance Decisions (Pending PO Approval)

| # | Decision | Rationale |
| --- | --- | --- |
| G1 | 76 units (NT-DA-0026..0030) reverted from `frozen` to `review` | They were auto-frozen by script without PO approval, violating Constitution §4. PO re-freezes after review. |
| G2 | 20 units (NT-DA-0021..0025) added `domain_area` field | Aligns units with the domain registry; previously unregistered. |
| G3 | 20 frozen domain `status.yaml` files reformatted (block YAML style) | Pure formatting: list indentation, unquoted scalars, removed comments. No semantic change (verified by diff review). Kept as-is; recorded here for transparency. |
| G4 | NT-LAW-3001 gap left unfilled | ID numbering is block-based (e.g. 0075 → 2101); no dangling references exist. |
| G5 | No anti-patterns in 3xxx series (created) | Original WP-01 plan listed 4; the delivered design replaced laws/anti-patterns with phenomena. Deferred to backlog — not invented ad hoc. |
| G6 | `relations` block excluded from dependency graph traversal | Relations are semantic and bidirectional (anti-pattern ↔ law); including them creates false cycles. Documented in engine. |
| G7 | Ask page synthesis and system metrics remain mock | Marked PLANNED; LLM integration belongs to EPIC 5 (capability NHANTHUAT-CAP-002). |

## 4. Traceability Table

| Acceptance Criterion | Status | Evidence |
| --- | --- | --- |
| All new units schema-valid | PASS | `scripts/validate_all.py`: "Validation passed: all managed documents are valid" |
| All tests pass | PASS | `pytest`: 145 passed, 0 failed |
| 20 frozen status.yaml unchanged semantically | PASS | `git diff docs/domains/` reviewed: formatting only |
| Engine domain queries work | PASS | `query(domain='tri-nhan')` → 174 units (previously 0) |
| 10 new domain blueprint docs exist | PASS | ARCHITECTURE/CONCEPT-MAP/DEPENDENCIES/GLOSSARY/evidence-placeholders per domain |
| 5 domain status.yaml created for 0026..0030 | PASS | `docs/domains/{cognitive-science-sensemaking,behavioral-economics-choice-architecture,behavioral-design,social-psychology,persuasion-influence}/status.yaml` |
| Stale brief fixed | PASS | `knowledge/domain-areas/cognitive-science-sensemaking.md` now describes NT-DA-0023 as sibling, not empty |
| Workbench mocks labeled | PASS | PLANNED captions in `app/pages/ask.py`, `app/pages/system.py` |
| Placeholders removed | PASS | `app/backend/`, `app/frontend/` deleted |

## 5. Test Evidence

- **Full suite:** `python -m pytest -p no:cacheprovider` → 145 passed, 0 failed, 0 skipped.
- **Validation:** `python scripts/validate_all.py` → pass.
- **Engine smoke:** engine loads 370 units, domain index has 5 lens keys with correct counts (174/47/54/53/42).

## 6. Files Changed (Summary)

- `knowledge/units/**` — 96 new unit files (untracked) + modified status/domain_area.
- `knowledge/domain-registry.yaml` — categories + 10 domains.
- `schemas/knowledge-unit.schema.json`, `src/nhan_thuat/{identifiers,validator,factory}.py` — phenomenon + domain_area support.
- `src/nhan_thuat/knowledge_engine.py` — primary_domain index fix.
- `src/nhan_thuat/runtime/` — 4 new modules.
- `app/**` — Streamlit workbench (7 files).
- `docs/domains/**` — 10 new domain directories with 5 blueprint files each; 20 reformatted status.yaml.
- `knowledge/domain-areas/cognitive-science-sensemaking.md` — fixed stale brief.
- `tests/` — 4 new test files + 2 updated.
- `scripts/run_web_dashboard.py`, `scripts/test_nhan_thuat_cli.py`, `pyproject.toml`, `CHANGELOG.md`, `CURRENT_STATE.md`.

## 7. Requests to Product Owner

1. **Approve G1–G2**: confirm the 96 new units remain `review` until you review; re-freeze at your discretion.
2. **Acknowledge G3**: 20 frozen status.yaml files were reformatted (cosmetic). Accept as change control record.
3. **Confirm G5**: anti-patterns for 3xxx series deferred to backlog.
4. **Scope EPIC 5**: approve LLM integration work plan for the ask page (capability NHANTHUAT-CAP-002).
