# Content Upgrade Report — Vietnamese Knowledge Base Completion

**ID:** NT-BATCH-003
**Date:** 2026-09-14
**Status:** completed (PO-approved change-control)
**Approved by:** Product Owner
**Scope:** knowledge/units (379 units), knowledge/cases, docs/knowledge, docs/domains/human-nature

---

## 1. Context

The repository-wide language sweep (`ff154d7`, 2026-08-15) translated 369 unit
files to Vietnamese, but an independent audit found substantive quality gaps:

- **45 units** carried boilerplate summaries ("Đơn vị tri thức cấu trúc về …"),
  generic definitions, template risks and template applications — all marked
  `status: frozen`.
- **127 units (33.5%)** had an empty `mechanism` array (121 units) or were
  missing the `mechanism` key (6 units).
- **93 units** referenced the orphan evidence placeholder `EV-REQ-0001-01` with
  no defining record anywhere in the repository.
- **2 duplicate title pairs** existed across unit types.
- `knowledge/cases/` and `knowledge/strategies/` were empty shells; 3 curated
  cases lived only in the SQLite database alongside 7 auto-generated duplicates;
  3 of the 18 book files were 106–123 byte stubs.
- `applications` section keys mixed `snake_case` and `kebab-case` conventions.

The Product Owner approved a full content upgrade (A1–A9) on 2026-09-14.

## 2. Changes Applied

### 2.1 Placeholder content replaced (45 units)

| Batch | Units | IDs | New content |
| --- | --- | --- | --- |
| Laws | 23 | `NT-LAW-0037`–`NT-LAW-0059` | Real summary, definition, 4–5 step mechanism, specific conditions/exceptions/applications/risks |
| Principles | 27 | `NT-PRINCIPLE-0063`–`NT-PRINCIPLE-0089` | Same full-field standard |
| Models | 15 | `NT-MODEL-0009`–`NT-MODEL-0023` | Model structure, mechanism, boundaries |
| Anti-patterns | 7 | `NT-ANTI-PATTERN-0012`, `0013`, `0029`–`0031`, `0038`, `0039` | Harmful-pattern mechanism, conditions, countermeasures |

### 2.2 Mechanism added (127 units total)

- 30 units above (placeholders) received mechanisms in the same pass.
- 70 additional units received new 4–5 step mechanisms:
  - anti-patterns `0014`–`0028`, `0032`–`0037`, `6001` (22 units)
  - laws `0060`–`0075`, `3201`, `4102`, `6001` (19 units)
  - phenomena `4101`–`4103` (3 units)
  - principles `0090`–`0113`, `4101` (25 units)
  - strategy `6001` (1 unit)
- Result: **0 units missing a mechanism**.

### 2.3 Evidence placeholder resolved

- `EV-REQ-0001-01` (93 references) defined in
  `docs/domains/human-nature/evidence-placeholders.yaml` together with
  `EV-REQ-0001-02` and `EV-REQ-0001-03`.
- No dead evidence references remain.

### 2.4 Duplicate titles disambiguated

- `NT-ANTI-PATTERN-2301`: "Ngụy biện chi phí chìm" → "Leo thang cam kết vào dự án thất bại".
- `NT-MODEL-0003`: "Chu kỳ thích ứng" → "Vòng lặp Thích ứng Hành vi".
- `NT-MODEL-2401`: "Chu kỳ Thích ứng" → "Chu kỳ Thích ứng Hệ thống (Panarchy)".
- `NT-PHENOMENON-3108` keeps "Ngụy biện chi phí chìm" as the canonical
  cognitive-phenomenon name.

### 2.5 Cases and books

- 3 curated cases were initially written to `knowledge/cases/` as YAML
  (`CASE-OPS-001`, `CASE-SALES-001`, `CASE-HR-001`). Per Product Owner decision on
  2026-09-14, the pre-made cases were **removed** (YAML files and database seeds):
  the Case Library must be user-driven only. Any difficult/special case is saved
  when the user exports an executive brief, which now persists the case
  automatically.
- 7 auto-generated duplicate rows removed from `knowledge/nhan_thuat.db`.
- 3 stub books expanded with full Vietnamese editorial content:
  `06_THUC_CHIEN_DU_AN.md`, `07_THUC_CHIEN_DU_AN.md`, `10_THUC_CHIEN_NHAN_SINH.md`.

### 2.6 Application key normalization

- 115 files normalized: all `applications` section keys are now lowercase
  `kebab-case`; variants merged (`process_design` + `process-design` →
  `process-design`, etc.).

## 3. Metadata

- Content-upgraded units: `version` bumped `0.1.0 → 0.2.0` where applicable.
- All touched units: `updated_at: 2026-09-14`.
- Frozen statuses preserved; no unit was unfrozen or refrozen in this batch.
- 6 draft units (`NT-LAW-3201`, `NT-LAW-4102`, `NT-PRINCIPLE-4101`,
  `NT-PHENOMENON-4101`–`4103`) remain `draft` pending Product Owner freeze.

## 4. Verification

- `python scripts/validate_all.py` → PASS (0 issues).
- `pytest` → all tests green.
- Content scan: 0 boilerplate summaries, 0 missing mechanisms.

## 5. Notes for Product Owner

- The 6 draft units now have complete content (mechanism included) and are
  ready for a freeze decision.
- `docs/domains/consumer-psychology/` (NT-DA-0031) has no `status.yaml`; the
  domain is registered in `knowledge/domain-registry.yaml` but not yet
  materialized as a governance artifact.
