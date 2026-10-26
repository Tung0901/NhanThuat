# REMEDIATION-CONTROLLED-RECOVERY: Khắc Phục Bảo Mật Sparring, Giao Diện Điều Hành & Kiểm Soát Thay Đổi 352 Đơn Vị Tri Thức — Specification

**ID:** SPEC-REMEDIATION-CONTROLLED-RECOVERY
**Epic Liên Quan:** NT-EPIC-03, NT-EPIC-04, NT-EPIC-05
**Tác giả:** Main Agent (Controlled Recovery Mode)
**Người duyệt:** Product Owner
**Trạng thái:** ready_for_review
**Ngày tạo:** 2026-10-19

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)
- **Vấn đề cần giải quyết:**
  1. **Lỗ hổng bảo mật Sparring (P0):**
     - Các endpoint `/api/v1/sparring/sessions`, `/api/v1/sparring/messages`, `/api/v1/sparring/sessions/{id}`, `/api/v1/sparring/sessions/{id}/export` chưa bắt buộc xác thực bằng Bearer session (`_require_case_file_session`) và chưa kiểm tra quyền sở hữu (`owner_id`) trên `SparringSession`, dẫn đến nguy cơ truy cập trái phép hoặc IDOR giữa các người dùng.
     - Hàm `_render_sparring_html` trong `src/nhan_thuat/export/executive_brief.py` nối chuỗi trực tiếp `session.title`, `session.philosophy_lens`, `msg.content`, `msg.matched_unit_ids` và `session.metadata` vào tài liệu HTML mà không qua `html.escape`, gây lỗ hổng Stored XSS khi xuất biên bản HTML.
  2. **Lỗi tính năng & Giao diện Frontend (P1/P2):**
     - Bộ lọc 8 Cung trong `#iching-palace-tabs` (`frontend/app.html`) gắn class `mode-pill` nhưng thiếu class `.iching-palace-pill` mà hàm `selectIChingPalace()` truy vấn, khiến nhiều nút cung cùng sáng `.active` hoặc không cập nhật trạng thái active đúng.
     - Lỗi chính tả hiển thị: `"ĐỘI NGŨ TIẾẬN NHẬN"` thay vì `"ĐỘI NGŨ TIẾP NHẬN"`.
     - Luồng chuyển phòng (`transferAdvisoryToSparring`, `transferCouncilToSparring`, `transferCouncilToWarRoom`) tự động gọi `launchConfiguredSparring()` hoặc `initWarRoomSimulation()` ngay khi chuyển tab thay vì để người dùng xem xét, chỉnh sửa và chủ động bấm xác nhận khởi chạy.
     - Cần giảm inline style lặp lại và emoji dư thừa trong các thành phần mới thêm, chuyển sang class CSS dùng chung đồng bộ với thiết kế hiện hữu.
  3. **Vi phạm quy trình quản trị Frozen & Boilerplate trên 352 Knowledge Units (P1/P3):**
     - 352 đơn vị tri thức (`346` Frozen, `6` Draft) đã bị sửa hàng loạt bằng script ngoài repo mà chưa có hồ sơ Change Request được Product Owner phê duyệt.
     - Mức bằng chứng (`evidence.level`) bị nâng từ `provisional` lên `supported` hàng loạt, kể cả trên các đơn vị giữ mã placeholder `EV-REQ-0001-01`.
     - Trường `content:` sinh tự động chứa các câu văn lặp hàng loạt (boilerplate) và các tuyên bố tuyệt đối hóa hành vi con người, vi phạm Điều 4 & Điều 5 của `PROJECT_CONSTITUTION.md`.
     - Hai file kiểm thử `tests/test_motivation_domain.py` và `tests/test_personality_domain.py` đã bị sửa để hợp thức hóa dữ liệu thay đổi.
- **Mục tiêu đạt được:**
  - Khóa toàn bộ lỗ hổng xác thực, phân quyền sở hữu (`owner_id`) và Stored XSS trên toàn bộ luồng Sparring API & Export.
  - Sửa dứt điểm bộ lọc 64 quẻ, typo, workflow chuyển phòng chờ xác nhận, chuẩn hóa CSS/icon cho phần UI mới và bổ sung kiểm thử thực thi DOM/JS tự động.
  - Lập inventory đầy đủ 352 đơn vị bị tác động, lập hồ sơ Change Request (`ready_for_review`) cho 346 Frozen units, khôi phục trạng thái nguyên vẹn cho các đơn vị ngoài phạm vi pilot, xử lý trung thực `evidence` (loại bỏ nâng khống `EV-REQ-0001-01`), và biên soạn chuẩn mực một **Pilot Batch 12 đơn vị đại diện** (`law`, `principle`, `model`, `phenomenon`, `anti-pattern`) không chứa câu lặp hay mệnh đề tuyệt đối hóa để trình Product Owner duyệt.
  - Đưa công cụ hỗ trợ kiểm định/biên tập vào repo (`scripts/knowledge_content_pilot_tool.py`) có chế độ `--dry-run`, xuất manifest, không tự ý đổi `status`/`evidence`/`version`, và có bộ test chống lặp boilerplate.
- **Ngoài phạm vi (Out of Scope):**
  - Không tự ý phê duyệt (`approved`) hoặc đóng băng (`frozen`) bất kỳ Change Request hay Epic nào.
  - Không viết lại đồng loạt cả 352 đơn vị tri thức khi chưa có quyết định phê duyệt Pilot của Product Owner.
  - Không redesign toàn bộ giao diện ứng dụng ngoài các vùng tính năng được chỉ định.
  - Không thực hiện `git commit` hoặc `git push`.

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories & Requirements)
- **User Story 1 (Bảo mật & Quyền sở hữu Sparring — P0):** Với vai trò là người dùng đã xác thực, tôi muốn phiên Đấu Trí của mình được gắn `owner_id` riêng và bảo vệ bởi Bearer token để không ai khác đọc, gửi tin nhắn hoặc xuất biên bản phiên của tôi, đồng thời biên bản HTML xuất ra an toàn tuyệt đối trước mã độc HTML/JS.
  - *Kịch bản kiểm thử:*
    - Given: Request gọi bất kỳ endpoint `/api/v1/sparring/*` không kèm Bearer token hợp lệ.
    - When: Gửi request `GET` hoặc `POST`.
    - Then: Nhận HTTP `401 Unauthorized`.
    - Given: Người dùng A tạo phiên `SPAR-SESS-XXXX`, người dùng B (khác `user_id` và không phải `ADMIN`) gọi `GET /api/v1/sparring/sessions/{id}`, `POST /api/v1/sparring/messages`, hoặc `GET /api/v1/sparring/sessions/{id}/export`.
    - When: Server kiểm tra quyền sở hữu.
    - Then: Nhận HTTP `403 Forbidden`, dữ liệu của người dùng A không bị lộ.
    - Given: Phiên đấu trí chứa payload `<script>alert(1)</script><img src=x onerror=alert(1)>` trong `title`, `philosophy_lens`, `content`, `metadata`, `matched_unit_ids`.
    - When: Xuất biên bản qua `export_sparring_session(..., format="html")`.
    - Then: Toàn bộ ký tự `<`, `>`, `"`, `'`, `&` đều được escape thành HTML entities an toàn và vẫn giữ nguyên hiển thị xuống dòng (`white-space: pre-wrap`).
- **User Story 2 (Bộ lọc 64 Quẻ, Typo & Workflow Chuyển Phòng — P1/P2):** Với vai trò là lãnh đạo sử dụng Web Studio, tôi muốn lọc 64 quẻ theo từng Cung kết hợp tìm kiếm từ khóa chính xác, và khi chuyển kịch bản từ Cố Vấn hoặc Hội Đồng sang Phòng Đấu Trí / Sa Bàn thì hệ thống chỉ điền sẵn dữ liệu vào khung cấu hình để tôi rà soát trước khi bấm nút khởi chạy.
  - *Kịch bản kiểm thử:*
    - Given: Mở Ma trận 64 Quẻ trong `#view-codex`.
    - When: Bấm chọn một cung (ví dụ `"Khảm"`) và nhập từ khóa tìm kiếm.
    - Then: Chỉ duy nhất nút cung `"Khảm"` có class `.active`, danh sách quẻ lọc đúng theo cung và từ khóa; hiển thị rõ trạng thái `loading`, `empty`, hoặc `error` khi cần.
    - Given: Người dùng bấm nút chuyển kịch bản từ `#view-advisory` hoặc `#view-council` sang `#view-sparring` hoặc `#view-war-room`.
    - When: Hàm `transferAdvisoryToSparring()`, `transferCouncilToSparring()`, hoặc `transferCouncilToWarRoom()` chạy.
    - Then: Chuyển sang đúng workspace, điền sẵn dữ liệu vào ô nhập liệu, mở khung cấu hình và hiển thị thông báo hướng dẫn xác nhận mà **không** tự động gọi API tạo phiên hay chạy mô phỏng.
- **User Story 3 (Quản trị Frozen, Trung thực Evidence & Pilot 12 Units — P1/P3):** Với vai trò là Product Owner, tôi muốn có bảng kiểm kê chính xác 352 đơn vị bị tác động, hồ sơ Change Request chuẩn governance cho 346 Frozen units ở trạng thái `ready_for_review`, khôi phục nguyên trạng các Frozen units chưa được duyệt sửa, và thẩm định một Pilot Batch 12 đơn vị chất lượng cao không chứa câu mẫu lặp hay tuyên bố tuyệt đối hóa.

---

## 3. Ranh giới Tách biệt Tầng (Architecture Boundary Check - ADR-0002)
- [x] Tính năng thuộc về **Knowledge Content** (Khôi phục nguyên trạng Frozen units chưa duyệt, chuẩn hóa Pilot Batch 12 units, xử lý trung thực `evidence`, lập Change Request & Inventory).
- [x] Tính năng thuộc về **Knowledge Engine** (`src/nhan_thuat/storage/models.py`, `src/nhan_thuat/storage/db.py`, `src/nhan_thuat/engine/sparring_engine.py`, `src/nhan_thuat/export/executive_brief.py`, `backend/app/main.py`).
- [x] Tính năng thuộc về **Presentation Layer** (`frontend/app.html` — bộ lọc 64 quẻ, sửa typo, workflow chuyển phòng chờ xác nhận, CSS classes & SVG icons).

---

## 4. Đánh giá Tác động Quản trị (Governance & Impact Analysis)
- **Ảnh hưởng đến Frozen Items?** [x] Có  [ ] Không
  - 346 Frozen units đã bị chỉnh sửa trong working tree đợt trước được kiểm kê đầy đủ trong hồ sơ Change Request `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md` (trạng thái `ready_for_review`).
  - Tuân thủ nghiêm ngặt nguyên tắc *"Không sửa thêm nội dung Frozen nếu chưa có Change Request được Product Owner duyệt"*: Khôi phục toàn bộ 346 Frozen units chưa có phê duyệt Change Request về đúng trạng thái `HEAD` đã đóng băng; Pilot Batch được thực hiện trên 6 đơn vị `draft` trong `knowledge/units/` cùng gói 6 bản mẫu đề xuất (`ready_for_review`) cho các đơn vị đại diện (`law`, `principle`, `model`, `phenomenon`, `anti-pattern`) để tổng cộng đủ **12 đơn vị Pilot đại diện 5 loại hình** trình Product Owner duyệt mà không tự ý ghi đè trái phép lên các tệp `frozen`.
- **Ảnh hưởng đến Schema YAML/JSON?** [ ] Có  [x] Không
- **Domain Areas liên quan:** Toàn bộ 31 Domain Areas (`NT-DA-0001` .. `NT-DA-0031`).

---

## 5. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)
- [x] AC-1: Toàn bộ 5 endpoint Sparring yêu cầu Bearer session hợp lệ (`401` khi thiếu/sai token) và kiểm tra quyền sở hữu `owner_id` (`403` khi truy cập phiên của người dùng khác).
- [x] AC-2: `ExecutiveBriefExporter._render_sparring_html` escape toàn bộ dữ liệu động (`title`, `philosophy_lens`, `content`, `metadata`, `matched_unit_ids`), chống hoàn toàn Stored XSS mà vẫn giữ xuống dòng.
- [x] AC-3: Bộ lọc 64 quẻ dùng đúng class `.iching-palace-pill`, chỉ 1 cung active tại một thời điểm, kết hợp đúng với ô tìm kiếm, có đủ trạng thái `loading`, `empty`, `error`.
- [x] AC-4: Sửa lỗi chính tả `"ĐỘI NGŨ TIẾẬN NHẬN"` thành `"ĐỘI NGŨ TIẾP NHẬN"`; workflow chuyển phòng chỉ nạp dữ liệu vào form cấu hình, không tự gọi API khởi chạy.
- [x] AC-5: Hoàn tất Inventory 352 units, hồ sơ Change Request (`ready_for_review`), khôi phục test gốc (`test_motivation_domain.py`, `test_personality_domain.py`), loại bỏ hoàn toàn các cụm câu lặp boilerplate và cụm từ tuyệt đối hóa, hoàn thiện Pilot Batch 12 units và script công cụ có `--dry-run` + manifest trong repo.
- [x] AC-6: Mọi thao tác transaction dùng chung khóa độc quyền trước recovery; journal từ chối auxiliary path tương đối và buộc full-match transaction PID; live apply chỉ chạy trong detached linked worktree tại đúng review commit; rollback fail-closed khi canonical thiếu hoặc path không được confinement.
- [x] AC-7: `python -m ruff check src backend tests scripts`, `pytest -q`, `python scripts/validate_all.py`, `python scripts/audit_content_inventory.py --check`, `git diff --check` đều đạt `exit code 0`.
