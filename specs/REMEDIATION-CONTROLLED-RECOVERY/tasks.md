# REMEDIATION-CONTROLLED-RECOVERY: Khắc Phục Bảo Mật Sparring, Giao Diện Điều Hành & Kiểm Soát Thay Đổi 352 Đơn Vị Tri Thức — Task Breakdown

**ID:** TASKS-REMEDIATION-CONTROLLED-RECOVERY  
**Spec & Plan Tham Chiếu:** SPEC-REMEDIATION-CONTROLLED-RECOVERY / PLAN-REMEDIATION-CONTROLLED-RECOVERY  
**Trạng thái:** ready_for_review  

---

## Danh sách Công việc Tuần tự (Ordered Implementation Tasks)

### Giai đoạn 1: Khóa Lỗi Bảo Mật Sparring (P0)
- [x] **TASK-01**: Bổ sung `owner_id` vào `SparringSession`, migration SQLite an toàn trong `DatabaseManager.init_db()`, và lọc/kiểm tra quyền sở hữu trong `SparringEngine` & `backend/app/main.py`.
  - *Tệp tác động:* `src/nhan_thuat/storage/models.py`, `src/nhan_thuat/storage/db.py`, `src/nhan_thuat/engine/sparring_engine.py`, `backend/app/main.py`
  - *Lệnh kiểm tra:* `.venv\Scripts\python.exe -m py_compile src/nhan_thuat/storage/models.py src/nhan_thuat/storage/db.py src/nhan_thuat/engine/sparring_engine.py backend/app/main.py`
- [x] **TASK-02**: Khắc phục lỗ hổng Stored XSS trong `src/nhan_thuat/export/executive_brief.py` bằng `html.escape` trên toàn bộ trường động của phiên và tin nhắn Đấu Trí.
  - *Tệp tác động:* `src/nhan_thuat/export/executive_brief.py`
- [x] **TASK-03**: Cập nhật `frontend/app.html` và các bài test sẵn có để truyền Bearer session khi gọi API Sparring; viết bộ test bảo mật `tests/test_sparring_security.py` kiểm chứng 401, 403, 200 (owner) và XSS escaping trên cả HTML & Markdown export.
  - *Tệp tác động:* `frontend/app.html`, `tests/test_sparring_security.py`, `tests/test_commercial_and_iching_api.py`
  - *Lệnh kiểm tra:* `.venv\Scripts\python.exe -X utf8 -m pytest tests/test_sparring_security.py tests/test_commercial_and_iching_api.py -q`

### Giai đoạn 2: Sửa Tính Năng và Giao Diện (P1/P2)
- [x] **TASK-04**: Sửa bộ lọc 64 quẻ (`.iching-palace-pill`, trạng thái `loading`/`empty`/`error`), sửa lỗi chính tả `"ĐỘI NGŨ TIẾP NHẬN"`, bỏ tự động gọi `launchConfiguredSparring()` và `initWarRoomSimulation()` khi chuyển phòng, chuyển inline styles lặp lại sang CSS classes và giảm emoji dư thừa.
  - *Tệp tác động:* `frontend/app.html`
- [x] **TASK-05**: Viết bộ kiểm thử thực thi DOM/JS `tests/test_frontend_dom_behavior.py` kiểm chứng thao tác chọn cung, tìm kiếm, mở chi tiết quẻ, chuyển phòng không tự khởi chạy API, trạng thái lỗi API và bố cục responsive.
  - *Tệp tác động:* `tests/test_frontend_dom_behavior.py`
  - *Lệnh kiểm tra:* `.venv\Scripts\python.exe -X utf8 -m pytest tests/test_frontend_dom_behavior.py -q`

### Giai đoạn 3: Xử Lý 352 Knowledge Units, Change Request & Pilot Batch (P1/P3)
- [x] **TASK-06**: Trích xuất Inventory chính xác của 352 đơn vị bị sửa và lập hồ sơ Change Request `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md` ở trạng thái `ready_for_review` cho 346 Frozen units.
  - *Tệp tác động:* `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md`
- [x] **TASK-07**: Khôi phục nguyên trạng 340 Frozen units (thu hồi boilerplate rập khuôn), hạ 171 units có bằng chứng placeholder sang `provisional` trung thực theo Change Request, giữ nguyên 2 file test `tests/test_motivation_domain.py`, `tests/test_personality_domain.py`; biên soạn Pilot Batch 12 đơn vị (`NT-LAW-3201`, `NT-LAW-4102`, `NT-LAW-2101`, `NT-PRINCIPLE-4101`, `NT-PRINCIPLE-0063`, `NT-MODEL-2101`, `NT-MODEL-2201`, `NT-PHENOMENON-4101`, `NT-PHENOMENON-4102`, `NT-PHENOMENON-4103`, `NT-ANTI-PATTERN-0012`, `NT-ANTI-PATTERN-0013`) đảm bảo không có câu lặp boilerplate, không tuyệt đối hóa hành vi và phân loại nguồn tham chiếu trung thực.
  - *Tệp tác động:* `knowledge/units/...`, `tests/test_motivation_domain.py`, `tests/test_personality_domain.py`
- [x] **TASK-08**: Đưa công cụ `scripts/knowledge_content_pilot_tool.py` vào repo (hỗ trợ `--dry-run`, xuất manifest, không tự ý đổi `status`/`evidence`/`version`, kiểm định chống lặp boilerplate & kiểm định chất lượng `evidence`) kèm bộ test `tests/test_knowledge_pilot_and_evidence.py`.
  - *Tệp tác động:* `scripts/knowledge_content_pilot_tool.py`, `tests/test_knowledge_pilot_and_evidence.py`
  - *Lệnh kiểm tra:* `.venv\Scripts\python.exe -X utf8 -m pytest tests/test_knowledge_pilot_and_evidence.py -q`

### Giai đoạn 4: Làm Sạch và Kiểm Chứng Toàn Diện (Verification & Dossier)
- [x] **TASK-09**: Chạy và báo cáo đầu ra thực của toàn bộ 7 bước kiểm chứng:
  1. `python -m ruff check src backend tests scripts` (Exit code 0, 0 lints)
  2. `pytest -q` (Exit code 0, 284/284 tests passed across 56 test files)
  3. `python scripts/validate_all.py` (Exit code 0, all managed documents valid)
  4. `python scripts/audit_content_inventory.py --check` (Exit code 0, 379 units verified)
  5. `git diff --check` (Exit code 0, no whitespace or merge marker issues)
  6. Kiểm thử bảo mật Sparring (`pytest tests/test_sparring_security.py -v`: Exit code 0, 4/4 passed)
  7. Kiểm thử browser/DOM cho phần frontend mới (`pytest tests/test_frontend_dom_behavior.py -v`: Exit code 0, 2/2 passed)

