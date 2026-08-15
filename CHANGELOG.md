# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi tại đây.

## [Unreleased]

### Added

- KnowledgeSynthesizer (capability NHANTHUAT-CAP-002) with fallback-first LLM synthesis via OpenAI-compatible endpoint, configurable through OPENAI_API_KEY / NHAN_THUAT_OPENAI_API_KEY, OPENAI_BASE_URL, and NHAN_THUAT_LLM_MODEL.
- `KnowledgeResolver.resolve_scored` returning (score, unit) pairs for real relevance ranking.
- Knowledge unit export endpoint `GET /knowledge/units/{unit_id}/export?format=json|markdown` and Workbench download buttons (JSON/Markdown) in the detail page.
- Five synthesizer/resolver tests and three knowledge unit export tests.

### Changed

- Ask page now surfaces real resolver scores, synthesis mode (LLM or deterministic), citations, and audit (correlation_id, provider, model, latency) instead of planned/mock placeholders.
- System page shows live synthesis provider status; mock "134/134" placeholder removed.
- `requests` added to package dependencies.
- Full repository ruff scope (src, scripts, tests, app, backend) passes clean.
- Version bumped to 1.0.0.

### Fixed

- Synthesizer provider call monkeypatching in tests via module-level `requests` import.

### Added

- Khung repository cho EPIC 0.
- JSON Schema cho domain và knowledge unit.
- Loader và validator YAML/JSON.
- Năm miền tri thức ở trạng thái draft.
- Test và CI nền tảng.
- Project Constitution cho EPIC 1.
- ADR directory và bốn ADR nền tảng ban đầu.
- EPIC 1 status ở trạng thái Ready for Review.
- EPIC 2 Knowledge Architecture analysis.
- Knowledge Unit, Taxonomy, Ontology, Registry, Catalog, identifier, naming, and validation architecture.
- ADR-0005 through ADR-0008 for EPIC 2 durable architecture decisions.
- EPIC 3 laws and principles architecture analysis.
- Initial core laws and principles library.
- ADR-0009 for the core laws and principles library.
- Knowledge Foundation Batch 1 with 20 laws and 40 principles.
- Evidence Layer foundation with standalone evidence records, citations, confidence, and traceability indexes.
- Knowledge Factory foundation with batch manifests, quality gates, review findings, and freeze eligibility.
- ADR-0010 through ADR-0013 for Evidence Layer and Knowledge Factory decisions.
- Milestone 1 Knowledge Core status artifact and pilot review report.
- Milestone 2 Domain Blueprint architecture and ADR-0014 through ADR-0015.
- Milestone 2 status artifact and ID/slug-only Domain Registry.
- Domain Freeze governance infrastructure and ADR-0016.
- Human Nature domain foundation with laws, principles, patterns, anti-patterns, glossary, concept map, dependencies, evidence placeholders, and review report.
- Motivation domain foundation with laws, principles, models, anti-patterns, glossary, concept map, dependencies, evidence placeholders, and review report.
- Ten new domain areas (NT-DA-0021 through NT-DA-0030) with 96 knowledge units (laws, principles, models, anti-patterns, phenomena).
- Phenomena knowledge type and `domain_area` metadata added to the unit schema, identifiers, and validator.
- Domain registry categories (CAT-CORE, CAT-BEHAVIORAL, CAT-APPLIED) and category mapping for all domains.
- Knowledge runtime components: graph traversal, keyword resolver, prompt builder, and heuristic evaluator.
- Streamlit Knowledge Workbench with six pages and Vietnamese localization layer.
- Domain blueprint documentation (ARCHITECTURE, CONCEPT-MAP, DEPENDENCIES, GLOSSARY, evidence-placeholders) for the ten new domain areas.

### Changed

- EPIC 0 approved by Product Owner and marked Frozen.
- EPIC 1 approved by Product Owner and marked Frozen.
- EPIC 2 approved by Product Owner and marked Frozen.
- EPIC 3 moved to Ready for Review.
- EPIC 3 approved by Product Owner and marked Frozen.
- Knowledge Foundation Batch 1 approved by Product Owner and marked Frozen.
- Milestone 1 Knowledge Core approved by Product Owner and marked Frozen.
- Roadmap aligned around Milestone 2 Knowledge Expansion & Domain System, Milestone 3 Intelligence Engine, and Milestone 4 BusinessOS Integration.
- ADR-0014 and ADR-0015 accepted by Product Owner.
- Repository validation now supports domain-area Frozen Register entries while preserving existing Epic, Milestone, and Batch records.
- Human Nature domain approved by Product Owner and marked Frozen.
- Motivation domain approved by Product Owner and marked Frozen.
- Engine indexes `primary_domain` instead of the unused `domain` field, fixing domain query and filtering.
- Twenty frozen domain status files reformatted to block YAML style without semantic changes (documented in the M16 review package).
- Knowledge engine now loads 370 units; tests and runtime assertions updated from 274 to 370.
- New units set to `review` status pending Product Owner approval; auto-frozen states reverted per governance.
- M16 knowledge expansion approved by Product Owner (2026-08-14): NT-BATCH-002, NT-DA-0021 through NT-DA-0030, and all 96 units frozen and registered in the Frozen Register.
