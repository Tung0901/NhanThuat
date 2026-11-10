# TASKS-EXECUTIVE-CONSIGLIERE-ENGINE: Danh Sách Công Việc Thực Thi

**ID:** TASKS-EXECUTIVE-CONSIGLIERE-ENGINE  
**Plan Liên Quan:** `specs/EXECUTIVE-CONSIGLIERE-ENGINE/plan.md`  
**Trạng thái:** completed  

---

## Danh mục Task Thực Thi

- [x] **Task 1:** Xây dựng dữ liệu 30 Án Điển Giải Phẫu Sống tại `knowledge/cases/living_dossiers.json` (10 ca tranh chấp quyền lực nội bộ, 10 ca khủng hoảng hiện trường công trường, 10 ca đàm phán sinh tử & thu hồi nợ) kèm dịch vụ `backend/app/engine/cases_service.py`.
- [x] **Task 2:** Nâng cấp `backend/app/engine/nhan_thuat_api.py` và `backend/app/main.py` với:
  - Động cơ định lượng `compute_executive_metrics` (Kairos Timing Score, Leverage Ratio, Cost of Inaction VNĐ, Silence Window).
  - Chế độ Quân Sư Thân Tín Hậu Trường (`consigliere_mode` & `consigliere_brief`).
  - API Endpoints `/api/v1/cases/dossiers` và `/api/v1/cases/dossiers/<id>`.
  - Bộ giải phẫu đòn đánh `tactical_audit` cho Sparring Arena.
- [x] **Task 3:** Nâng cấp giao diện `frontend/app.html` đồng bộ thẩm mỹ Obsidian-Gold chống AI:
  - Công tắc & bảng chỉ dẫn **Mật Thất Quân Sư (Consigliere Realpolitik Mode)** trong Advisory Cockpit.
  - **Bảng Đồng Hồ Cảm Thức Thời Thế & Chi Phí Trì Hoãn (Executive Kairos & ROI Cockpit)** trong Advisory & Diagnostics.
  - Khu vực **Kho 30 Án Điển Sống (Living Case Dossiers)** có bộ lọc 3 chiến trường và Modal/Drawer giải phẫu chi tiết.
  - Khung **Giải Phẫu Đòn Đánh Tức Thì (Tactical Strike Analyzer)** trong Sparring Arena.
- [x] **Task 4:** Viết bộ test tự động `tests/test_executive_consigliere_engine.py`, chạy kiểm thử toàn diện (`pytest`, `scripts/validate_all.py`, `ruff check`) và đẩy mã nguồn lên GitHub.
