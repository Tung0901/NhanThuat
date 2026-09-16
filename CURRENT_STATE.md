# Current Repository State - NhanThuat Knowledge Repository

**Last Updated:** 2026-09-16
**Status:** **ACTIVE — Vietnamese content base complete, Web app (Executive Studio) operational**

---

## 1. System Overview

NhanThuat is a formal knowledge repository and governance framework for human nature, organizational behavior, decision intelligence, leadership, and operational management.

The repository ships:
- A Vietnamese knowledge base (379 units) validated by schema + repository validators.
- A five-lens philosophy system (Rhetoric, Confucianism, Legalism, Taoism, Xunzi) with executable engines and a multi-lens router.
- An "Executive Studio" web app served by a stdlib HTTP gateway (`backend/app/main.py`) with the UI in `frontend/app.html`.
- A fallback-first LLM synthesis layer (Google Gemini via OpenAI-compatible endpoint; deterministic fallback when no key is configured).

---

## 2. Five Philosophy Lens Infrastructure

### Single Source of Truth Documentation (`docs/knowledge/`)
1. `01_THUAT_HUNG_BIEN.md` — Thuật Hùng Biện (Rhetoric Lens).
2. `02_TU_THU_KNOWLEDGE_PACK.md` — Nho Gia (Confucian Lens).
3. `03_HAN_PHI_TU_KNOWLEDGE_PACK.md` — Pháp Gia (Legalism Lens).
4. `04_TRANG_TU_KNOWLEDGE_PACK.md` — Đạo Gia (Taoism Lens).
5. `05_TUAN_TU_KNOWLEDGE_PACK.md` — Tuân Tử (Xunzi Lens).

The directory now holds 18 knowledge books in total (including applied books such as
`06_NHAN_THUAT_UNG_XU.md`, `09_TAM_LY_HOC_HANH_VI.md`, `11_TAM_LY_HOC_THUYET_PHUC.md`,
`20_TU_DUY_HE_THONG.md`, `21_NGUYEN_TAC_QUAN_TRI_THUC_THI.md`, and the three
`THUC_CHIEN` case archives).

### Executable JSON Engines (`backend/app/engine/philosophies/`)
Five lens engines (`rhetoric_engine.json`, `confucian_engine.json`, `legalism_engine.json`,
`taoism_engine.json`, `xunzi_engine.json`) expose standardized Program 8 & 9 metadata blocks
and are composed by `PhilosophyRouter` (multi-lens weights and conflict resolution).

---

## 3. Domain & Knowledge Unit Catalog

- **Domain Areas:** 31 registered domains (`NT-DA-0001` through `NT-DA-0031`) in `knowledge/domain-registry.yaml`.
- **Knowledge Units:** 379 units — 85 Laws, 135 Principles, 45 Models, 61 Anti-Patterns, 52 Phenomena, 1 Strategy.
- **Status:** 373 units `frozen`, 6 units `draft` (`NT-LAW-3201`, `NT-LAW-4102`, `NT-PRINCIPLE-4101`, `NT-PHENOMENON-4101`..`4103`) awaiting Product Owner freeze.
- **Cases:** 3 curated field cases in `knowledge/cases/` (`CASE-OPS-001`, `CASE-SALES-001`, `CASE-HR-001`), mirrored in the runtime database.
- **Validation Status:** `scripts/validate_all.py` passes 100% clean.
- **Test Suite Status:** `pytest` passes 100% (184 tests).
- **Lint Status:** `ruff check src scripts tests` passes clean.

---

## 4. Knowledge Runtime & Web App

- **Runtime components** (`src/nhan_thuat/runtime/`): `KnowledgeGraph`, `KnowledgeResolver`, `PromptBuilder`, `KnowledgeEvaluator`, `KnowledgeSynthesizer` (multi-provider failover with deterministic fallback; multi-paragraph strategic argumentative treatise for situation overview).
- **Web gateway** (`backend/app/main.py`): stdlib `ThreadingHTTPServer` exposing REST endpoints for advisory analysis, council deliberation, sparring, diagnostics, case studies, department packs, knowledge units/domains/stats, book reader, PDF export, and temporary authentication session management (`/api/v1/auth/*`).
- **Web app** (`frontend/app.html`): five workspace modules with Dark Glassmorphism temporary login gate modal, quick 1-touch demo access, user profile header widget, and distinctive treatise-card layout for strategic situation overview.
- **Engine index:** domain queries run on `primary_domain`; the `relations` block is treated as semantic (bidirectional) and excluded from dependency graph traversal.
