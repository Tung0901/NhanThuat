# Changelog

Mọi thay đổi đáng chú ý của dự án được ghi tại đây.

## [1.0.1] - 2026-09-14

### Added

- Nội dung thật cho 45 units placeholder trước đây (laws 0037–0059, principles 0063–0089, models 0009–0023, anti-patterns 0012/0013/0029–0031/0038/0039) theo chuẩn đầy đủ trường.
- Bổ sung `mechanism` cho 127 units còn thiếu (0 units thiếu mechanism sau cập nhật).
- 3 hồ sơ thực chiến YAML trong `knowledge/cases/`: `CASE-OPS-001`, `CASE-SALES-001`, `CASE-HR-001`.
- Nội dung đầy đủ cho 3 cẩm nang từng là stub: `06_THUC_CHIEN_DU_AN.md`, `07_THUC_CHIEN_DU_AN.md`, `10_THUC_CHIEN_NHAN_SINH.md`.
- Endpoint `GET /api/v1/knowledge/stats` (số units, books, domains, frozen).
- Book reader trong web app (Markdown render + DOMPurify) thay cho việc mở JSON thô.
- Mobile navigation drawer cho màn hình ≤900px; catalog có tìm kiếm, lọc loại, tải dần; case studies tải động từ API.
- DOMPurify sanitize cho toàn bộ markdown render và escape HTML cho nội suy nội dung.
- Change-control report `docs/reports/NT-BATCH-003_CONTENT_UPGRADE_2026-09-14.md` và entry `NT-BATCH-003` trong Frozen Register.
- Định nghĩa `EV-REQ-0001-01` (93 tham chiếu trước đây mồ côi) trong `docs/domains/human-nature/evidence-placeholders.yaml`.

### Changed

- Phân biệt tiêu đề trùng: `NT-ANTI-PATTERN-2301` → "Leo thang cam kết vào dự án thất bại"; `NT-MODEL-0003` → "Vòng lặp Thích ứng Hành vi"; `NT-MODEL-2401` → "Chu kỳ Thích ứng Hệ thống (Panarchy)".
- Chuẩn hóa 115 file: toàn bộ khóa `applications` về kebab-case, gộp biến thể `_`/`-`.
- Web gateway dùng `ThreadingHTTPServer`, thêm cache headers cho static assets; PDF export render markdown thật với nút in.
- Sửa provider/model metadata trong sparring về giá trị thực từ synthesizer.
- Dọn 7+ case test rác và session test khỏi `knowledge/nhan_thuat.db`; test gateway chuyển sang DB cô lập.
- README/CURRENT_STATE phản ánh đúng sản phẩm hiện tại (Executive Studio, Render là chuẩn deploy).
- Dockerfile/compose đồng bộ entry point `python -m backend.app.main` với render.yaml.

### Fixed

- Ruff sạch toàn bộ (`ruff check src scripts tests`) — CI xanh trở lại sau 81 lần đỏ liên tiếp.
- `datetime.utcnow()` deprecated thay bằng `datetime.now(UTC)`.
- Cache vector đọc/ghi lỗi không còn nuốt exception im lặng.

### Removed

- 18 file rác root (fix_*.py, output*.txt, readme.txt của dự án khác, generic_files.json, update_yaml.py).
- Binary runtime khỏi git tracking (`knowledge/nhan_thuat.db`, `knowledge/.vector_cache.json`) — được tái tạo tự động và đã vào `.gitignore`.

## [1.0.0] - 2026-08-15

### Added

- KnowledgeSynthesizer (capability NHANTHUAT-CAP-002) with fallback-first LLM synthesis via OpenAI-compatible endpoint.
- `KnowledgeResolver.resolve_scored` returning (score, unit) pairs for real relevance ranking.
- Knowledge unit export endpoint `GET /knowledge/units/{unit_id}/export?format=json|markdown`.
- Five synthesizer/resolver tests and three knowledge unit export tests.

### Changed

- Ask page surfaces resolver scores, synthesis mode (LLM or deterministic), citations, and audit.
- `requests` added to package dependencies.
- Version bumped to 1.0.0.

### Fixed

- Synthesizer provider call monkeypatching in tests via module-level `requests` import.

## [0.1.0] - 2026-07-20

### Added

- Khung repository cho EPIC 0.
- JSON Schema cho domain và knowledge unit.
- Loader và validator YAML/JSON.
- Năm miền tri thức ở trạng thái draft.
- Test và CI nền tảng.
- Project Constitution cho EPIC 1.
- ADR directory và bốn ADR nền tảng ban đầu.
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
- Human Nature domain foundation.
- Motivation domain foundation.
- Ten new domain areas (NT-DA-0021 through NT-DA-0030) with 96 knowledge units.
- Phenomena knowledge type and `domain_area` metadata added to the unit schema, identifiers, and validator.
- Domain registry categories (CAT-CORE, CAT-BEHAVIORAL, CAT-APPLIED).
- Knowledge runtime components: graph traversal, keyword resolver, prompt builder, and heuristic evaluator.
- Streamlit Knowledge Workbench with six pages and Vietnamese localization layer (superseded by the Executive Studio web app).
- Domain blueprint documentation for the ten new domain areas.

### Changed

- EPIC 0–3 approved by Product Owner and marked Frozen.
- Knowledge Foundation Batch 1 approved and marked Frozen.
- Milestone 1 Knowledge Core approved and marked Frozen.
- Engine indexes `primary_domain` instead of the unused `domain` field.
- Knowledge engine now loads 370 units; tests updated from 274 to 370.
- M16 knowledge expansion approved by Product Owner (2026-08-14): NT-BATCH-002, NT-DA-0021 through NT-DA-0030, and all 96 units frozen and registered in the Frozen Register.
