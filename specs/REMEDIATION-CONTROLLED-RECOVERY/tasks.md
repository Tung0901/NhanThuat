# REMEDIATION-CONTROLLED-RECOVERY: Khắc Phục Bảo Mật Sparring, Giao Diện Điều Hành & Kiểm Soát Thay Đổi 352 Đơn Vị Tri Thức — Task Breakdown

**ID:** TASKS-REMEDIATION-CONTROLLED-RECOVERY
**Spec & Plan Tham Chiếu:** SPEC-REMEDIATION-CONTROLLED-RECOVERY / PLAN-REMEDIATION-CONTROLLED-RECOVERY
**Trạng thái:** ready_for_review

---

## Danh sách Công việc Tuần tự (Ordered Implementation Tasks)

### Giai đoạn 1: Khóa Lỗi Bảo Mật Sparring (P0)
- [x] **TASK-01**: Bổ sung `owner_id` vào `SparringSession`, migration SQLite an toàn trong `DatabaseManager.init_db()`, và lọc/kiểm tra quyền sở hữu trong `SparringEngine` & `backend/app/main.py`.
  - *Tệp tác động:* `src/nhan_thuat/storage/models.py`, `src/nhan_thuat/storage/db.py`, `src/nhan_thuat/engine/sparring_engine.py`, `backend/app/main.py`
  - *Kết quả:* Toàn bộ 5 endpoint Sparring yêu cầu Bearer token và kiểm tra quyền sở hữu (401/403/200).
- [x] **TASK-02**: Khắc phục lỗ hổng Stored XSS trong `src/nhan_thuat/export/executive_brief.py` bằng `html.escape` trên toàn bộ trường động của phiên và tin nhắn Đấu Trí.
  - *Tệp tác động:* `src/nhan_thuat/export/executive_brief.py`
  - *Kết quả:* Escape title, philosophy_lens, metadata đối thủ, message content, matched_unit_ids an toàn; giữ nguyên `white-space: pre-wrap`.
- [x] **TASK-03**: Cập nhật `frontend/app.html` truyền Bearer session khi gọi API Sparring và khi export; viết bộ test bảo mật `tests/test_sparring_security.py` kiểm chứng 401, 403, 200 (owner) và XSS escaping trên cả HTML & Markdown export.
  - *Tệp tác động:* `frontend/app.html`, `tests/test_sparring_security.py`, `tests/test_commercial_and_iching_api.py`

### Giai đoạn 2: Sửa Tính Năng và Giao Diện (P1/P2)
- [x] **TASK-04**: Sửa bộ lọc 64 quẻ (`.iching-palace-pill`, 1 cung active, trạng thái `loading`/`empty`/`error`), sửa lỗi chính tả `"ĐỘI NGŨ TIẾP NHẬN"`, bỏ tự động gọi `launchConfiguredSparring()` và `initWarRoomSimulation()` khi chuyển phòng, chuyển inline styles lặp lại sang CSS classes và giảm emoji dư thừa.
  - *Tệp tác động:* `frontend/app.html`
- [x] **TASK-05**: Viết bộ kiểm thử thực thi DOM/JS `tests/test_frontend_dom_behavior.py` kiểm chứng thao tác chọn cung, tìm kiếm, mở chi tiết quẻ, chuyển phòng không tự khởi chạy API, trạng thái lỗi API và bố cục responsive.
  - *Tệp tác động:* `tests/test_frontend_dom_behavior.py`

### Giai đoạn 3: Đưa Frozen Content Về Đúng Quy Trình & Pilot Batch 12 Đơn Vị (P1/P3)
- [x] **TASK-06**: Khôi phục có chọn lọc toàn bộ 177 Frozen canonical units về đúng trạng thái base commit `27a34bc` bằng manifest và kiểm tra mã băm SHA-256 (0 thay đổi trực tiếp trên canonical Frozen units).
  - *Tệp tác động:* `knowledge/units/...` (177 Frozen canonical files hoàn nguyên về base commit `27a34bc`)
- [x] **TASK-07**: Nâng cấp chất lượng 6 Draft pilot units trong canonical `knowledge/units/` (`NT-LAW-3201`, `NT-LAW-4102`, `NT-PRINCIPLE-4101`, `NT-PHENOMENON-4101`, `NT-PHENOMENON-4102`, `NT-PHENOMENON-4103`): chuẩn hóa phân loại nguồn 7 tầng, loại bỏ câu rập khuôn boilerplate và mệnh đề tuyệt đối hóa.
  - *Tệp tác động:* `knowledge/units/laws/NT-LAW-3201.yaml`, `knowledge/units/laws/NT-LAW-4102.yaml`, `knowledge/units/principles/NT-PRINCIPLE-4101.yaml`, `knowledge/units/phenomena/NT-PHENOMENON-4101.yaml`, `knowledge/units/phenomena/NT-PHENOMENON-4102.yaml`, `knowledge/units/phenomena/NT-PHENOMENON-4103.yaml`
- [x] **TASK-08**: Xây dựng 6 proposal artifacts cho 6 Frozen pilot units tại `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/*.yaml` (`NT-LAW-2101`, `NT-MODEL-2101` [provisional], `NT-MODEL-2201`, `NT-PRINCIPLE-0063`, `NT-ANTI-PATTERN-0012`, `NT-ANTI-PATTERN-0013`) ở trạng thái `ready_for_review`, kèm đầy đủ metadata quy định, đối chiếu trước/sau và phân loại nguồn.
  - *Tệp tác động:* `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/`
- [x] **TASK-09**: Xây dựng công cụ tái lập `scripts/knowledge_content_pilot_tool.py` dựa trên base commit cố định `27a34bc`, hỗ trợ `--audit-only`, `--dry-run` tuyệt đối read-only, `--manifest`, `--rollback` dạng giao dịch staged, journaled, hash-verified; ràng buộc integrity vào review commit Git tree, suy ra canonical path từ immutable base tree, ghi durable early transaction journal, dùng `ExclusiveTransactionLock` trước mọi recovery/mutation, xác minh detached linked promotion worktree, buộc auxiliary path tuyệt đối full-match transaction PID, nhận diện đúng tiến trình Windows đã thoát, và rollback fail-closed khi canonical thiếu.
  - *Tệp tác động:* `scripts/knowledge_content_pilot_tool.py`
- [x] **TASK-10**: Lập hồ sơ Change Request `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md` ở trạng thái `ready_for_review`, tách biệt Quyết định A (171 provisional evidence) và Quyết định B (6 frozen pilot proposals theo Product Owner Promotion Workflow).
  - *Tệp tác động:* `governance/change-requests/CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md`, `specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json`
- [x] **TASK-11**: Viết bộ kiểm thử `tests/test_knowledge_pilot_and_evidence.py` bao quát 6 Draft canonical, 6 Frozen proposals, kiểm định evidence, fail-closed, Git review/worktree verification, isolated fault injection và hard-kill, recovery dùng chung lock, nhận diện PID sống/đã thoát, dry-run zero-write, malicious/relative path confinement theo working directory khác, cleanup, và rollback thiếu canonical.
  - *Tệp tác động:* `tests/test_knowledge_pilot_and_evidence.py`

### Các Nhiệm Vụ Chờ Quyết Định Của Product Owner (Pending PO Approval)
- [ ] **TASK-12 (Pending Dedicated CR — Quyết định A)**: Lập hồ sơ Change Request chuyên biệt riêng kèm spec, proposal artifact và semver bump độc lập cho từng đơn vị trong 171 Frozen units có bằng chứng placeholder ở chu kỳ tiếp theo (không can thiệp trong vòng khắc phục này).
- [ ] **TASK-13 (Pending PO Approval — Quyết định B)**: Áp dụng 6 Frozen pilot proposals từ `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/` vào canonical `knowledge/units/` sau khi PO ký duyệt Quyết định B của Change Request `CR-2026-10-19-KNOWLEDGE-CONTENT-V1`.
