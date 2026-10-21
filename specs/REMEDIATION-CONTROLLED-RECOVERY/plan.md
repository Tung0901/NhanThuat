# REMEDIATION-CONTROLLED-RECOVERY: Khắc Phục Bảo Mật Sparring, Giao Diện Điều Hành & Kiểm Soát Thay Đổi 352 Đơn Vị Tri Thức — Technical Plan

**ID:** PLAN-REMEDIATION-CONTROLLED-RECOVERY  
**Spec Tham Chiếu:** SPEC-REMEDIATION-CONTROLLED-RECOVERY  
**Người lập:** Main Agent (Controlled Recovery Mode)  
**Trạng thái:** ready_for_review  

---

## 1. Bản vẽ Thiết kế Kiến trúc (Architectural Blueprint)
- **Tổng quan giải pháp kỹ thuật:**
  1. **Giai đoạn 1 — Khóa lỗi bảo mật Sparring (P0):**
     - Bổ sung trường `owner_id: str = "system"` vào `SparringSession` (`src/nhan_thuat/storage/models.py`) và cột `owner_id TEXT NOT NULL DEFAULT 'system'` vào bảng `sparring_sessions` (`src/nhan_thuat/storage/db.py`), kèm cơ chế tự động `ALTER TABLE sparring_sessions ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'system'` trong `init_db()` để tương thích ngược an toàn với mọi cơ sở dữ liệu SQLite cũ.
     - Cập nhật `DatabaseManager.create_session()`, `DatabaseManager.list_sessions(owner_id=...)` và `SparringEngine.start_session()`, `SparringEngine.process_turn()` để truyền và kiểm tra `owner_id`.
     - Tại `backend/app/main.py`: Tất cả 5 endpoint Sparring (`POST /api/v1/sparring/sessions`, `POST /api/v1/sparring/messages`, `GET /api/v1/sparring/sessions`, `GET /api/v1/sparring/sessions/{id}`, `GET /api/v1/sparring/sessions/{id}/export`) đều gọi `self._require_case_file_session()` (trả về HTTP `401` nếu chưa đăng nhập) và kiểm tra quyền sở hữu `self._can_access_sparring_session(auth_session, sparring_session)` (chỉ chủ sở hữu `session.owner_id == auth_session["user_id"]` hoặc tài khoản `user_id == "admin"` mới được phép truy cập; trả về HTTP `403` nếu truy cập trái phép).
     - Tại `frontend/app.html`: Gửi kèm header `Authorization: Bearer <token>` khi gọi các API `/api/v1/sparring/*` và dùng `fetch` kèm Bearer token khi xuất biên bản Đấu Trí.
     - Tại `src/nhan_thuat/export/executive_brief.py`: Dùng `html.escape(..., quote=True)` trên toàn bộ trường động trong `_render_sparring_html` (`session.title`, `session.id`, `session.philosophy_lens`, `session.created_at`, `msg.created_at`, `msg.content`, `msg.matched_unit_ids`, và các trường `opponent_name`, `opponent_role`, `opponent_personality`, `opponent_leverage` trong `session.metadata`), giữ nguyên `white-space: pre-wrap` để bảo toàn xuống dòng của transcript.
  2. **Giai đoạn 2 — Sửa tính năng và Giao diện (P1/P2):**
     - Thêm class `.iching-palace-pill` vào tất cả các nút lọc cung trong `#iching-palace-tabs`, đồng bộ logic `selectIChingPalace(palace, btn)` và `filterIChingHexagrams()`, bổ sung hiển thị rõ 3 trạng thái `loading`, `empty`, `error` trong `loadIChingHexagrams()`.
     - Sửa lỗi chính tả `"ĐỘI NGŨ TIẾẬN NHẬN"` $\rightarrow$ `"ĐỘI NGŨ TIẾP NHẬN"`.
     - Sửa `transferAdvisoryToSparring()`, `transferCouncilToSparring()`, và `transferCouncilToWarRoom()`: chỉ chuyển workspace, mở panel cấu hình, điền dữ liệu vào các ô input và focus + hiển thị trạng thái chờ xác nhận, **tuyệt đối không** tự động gọi `launchConfiguredSparring()` hay `initWarRoomSimulation()`.
     - Thay thế inline styles lặp lại của phần mới (Ma trận 64 quẻ, thanh thêm tag tùy chỉnh, thanh hành động chuyển phòng) bằng các class CSS sạch và dùng SVG/ký hiệu tối giản đồng bộ với hệ thống thiết kế hiện tại.
     - Viết bộ kiểm thử thực thi DOM/JS (`tests/test_frontend_dom_behavior.py`) chạy code thực trên Node.js VM + DOM harness để kiểm chứng hành vi chọn cung, tìm kiếm, mở chi tiết quẻ, chuyển phòng không gọi API tự động, và xử lý lỗi API.
  3. **Giai đoạn 3 — Kiểm soát Thay đổi 352 Knowledge Units, Xử lý Evidence & Pilot Batch (P1/P3):**
     - Xuất báo cáo kiểm kê chính xác 352 đơn vị đã sửa và lập hồ sơ Change Request (`governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md`) ở trạng thái `ready_for_review` cho 346 Frozen units và 15 đơn vị đại diện thuộc Pilot Batch.
     - Khôi phục các Frozen units chưa được duyệt sửa và khôi phục `tests/test_motivation_domain.py`, `tests/test_personality_domain.py` về trạng thái chuẩn (không sửa test để hợp thức hóa dữ liệu sai).
     - Xây dựng công cụ chính thức trong repo `scripts/knowledge_content_pilot_tool.py` có `--dry-run`, xuất manifest, kiểm tra cấm câu lặp boilerplate, cấm từ ngữ tuyệt đối hóa, kiểm tra tính hợp lệ của `evidence` (cấm nâng `supported`/`strong` khi chỉ có placeholder `EV-REQ-0001-01`).
     - Chuẩn hóa **Pilot Batch 12 đơn vị đại diện** (bao gồm 6 đơn vị `draft` trong `knowledge/units/` và 6 bản đề xuất nâng cấp mẫu trong gói Pilot `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/` phủ đủ 5 loại `law`, `principle`, `model`, `phenomenon`, `anti-pattern`) với nội dung chuyên sâu riêng biệt, có đầy đủ điều kiện áp dụng, ngoại lệ, mức bất định, rủi ro diễn giải sai và phân loại nguồn tham chiếu rõ ràng.
- **Các ADR liên quan:** ADR-0001 (Repository as source of truth), ADR-0002 (Separation of knowledge content and engine), ADR-0003 (Product Owner approval and Frozen control).

---

## 2. Danh sách Tệp tin Ảnh hưởng (Impacted Files & Scoping)

| Tệp tin | Loại hành động | Trách nhiệm |
| :--- | :--- | :--- |
| `src/nhan_thuat/storage/models.py` | Sửa | Thêm `owner_id` vào `SparringSession` |
| `src/nhan_thuat/storage/db.py` | Sửa | Thêm cột `owner_id` + migration an toàn + lọc theo `owner_id` |
| `src/nhan_thuat/engine/sparring_engine.py` | Sửa | Truyền `owner_id` khi khởi tạo phiên và xử lý lượt đấu |
| `src/nhan_thuat/export/executive_brief.py` | Sửa | Escape toàn bộ dữ liệu động trong `_render_sparring_html` chống Stored XSS |
| `backend/app/main.py` | Sửa | Bắt buộc xác thực Bearer session và kiểm tra quyền sở hữu trên cả 5 API Sparring |
| `frontend/app.html` | Sửa | Gửi Bearer token cho Sparring, sửa `.iching-palace-pill`, sửa typo, bỏ tự chạy khi chuyển phòng, gom CSS class |
| `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md` | Thêm mới | Hồ sơ Change Request (`ready_for_review`) kèm Inventory 352 units & kế hoạch rollback |
| `scripts/knowledge_content_pilot_tool.py` | Thêm mới | Công cụ kiểm định & sinh manifest có `--dry-run`, chống boilerplate & kiểm định evidence |
| `knowledge/units/...` (6 Draft units + rollback 346 Frozen units) | Sửa / Khôi phục | Khôi phục 346 Frozen units về trạng thái được duyệt; chuẩn hóa 6 Draft units + 6 đề xuất Pilot đại diện |
| `tests/test_sparring_security.py` | Thêm mới | Kiểm thử 401/403/200 ownership & Stored XSS cho HTML/Markdown export |
| `tests/test_frontend_dom_behavior.py` | Thêm mới | Kiểm thử hành vi DOM/JS thực tế cho bộ lọc 64 quẻ, chuyển phòng và xử lý lỗi API |
| `tests/test_knowledge_pilot_and_evidence.py` | Thêm mới | Kiểm thử chống boilerplate, kiểm định chất lượng evidence và công cụ `--dry-run` |

---

## 3. Thiết kế Dữ liệu & Giao diện Hợp đồng (Data & Interface Contracts)
- **Data Model (`SparringSession`):**
  - `id: str`, `title: str`, `philosophy_lens: str = "auto"`, `owner_id: str = "system"`, `created_at: str`, `status: str = "active"`, `summary: str = ""`, `metadata: dict[str, Any]`
- **API Endpoints (`/api/v1/sparring/*`):**
  - `POST /api/v1/sparring/sessions`: Yêu cầu `Authorization: Bearer <token>`. Gán `owner_id = auth_session["user_id"]`. Trả `401` nếu thiếu token.
  - `POST /api/v1/sparring/messages`: Yêu cầu `Authorization: Bearer <token>`. Nếu `session_id` tồn tại nhưng `session.owner_id != auth_session["user_id"]` (và không phải `admin`), trả `403`.
  - `GET /api/v1/sparring/sessions`: Yêu cầu `Authorization: Bearer <token>`. Chỉ trả về các phiên thuộc `auth_session["user_id"]` (hoặc tất cả nếu `admin`).
  - `GET /api/v1/sparring/sessions/{id}` & `GET /api/v1/sparring/sessions/{id}/export`: Yêu cầu `Authorization: Bearer <token>`. Trả `404` nếu không tồn tại, `403` nếu không phải chủ sở hữu.

---

## 4. Chiến lược Thử nghiệm & Kiểm chứng (Testing & Verification Strategy)
- `python -m ruff check src backend tests scripts`
- `pytest -q`
- `python scripts/validate_all.py`
- `python scripts/audit_content_inventory.py --check`
- `git diff --check`

