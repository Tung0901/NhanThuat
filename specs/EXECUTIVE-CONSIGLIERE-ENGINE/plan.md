# PLAN-EXECUTIVE-CONSIGLIERE-ENGINE: Thiết Kế Kỹ Thuật & Lộ Trình Thực Thi

**ID:** PLAN-EXECUTIVE-CONSIGLIERE-ENGINE  
**Spec Liên Quan:** `specs/EXECUTIVE-CONSIGLIERE-ENGINE/spec.md`  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-11-10  

---

## 1. Kiến trúc Giải pháp (Solution Architecture)

### 1.1. Tầng Dữ liệu Án Điển (`knowledge/cases/living_dossiers.json`)
- Lưu trữ 30 hồ sơ án điển thực chiến (`NT-CASE-0001` .. `NT-CASE-0030`) chia đều vào 3 chiến trường:
  1. `internal_power` (10 cases): Tranh chấp cổ đông sáng lập, phó tướng tạo phản, bè phái nội bộ, thâu tóm ngược.
  2. `field_crisis` (10 cases): Khủng hoảng công trường, đình công tập thể, nhà thầu phụ găm tiến độ, đứt gãy chuỗi cung ứng.
  3. `high_stakes_negotiation` (10 cases): Thu hồi nợ khó đòi, đối phó cổ đông cá mập ép giá, xử lý khủng hoảng truyền thông, đàm phán M&A sinh tử.
- Mỗi bản ghi gồm:
  - `id`, `title`, `category`, `category_label`, `industry`, `scale`
  - `power_map`: Bản đồ thế lực và quân bài các bên nắm giữ
  - `fatal_mistake`: Sai lầm chí mạng đã phạm phải + mã Anti-pattern
  - `quantified_damage`: `{ "financial_vnd": "...", "time_lost": "...", "personnel_impact": "..." }`
  - `surgical_strike`: Mảng 3 bước xuất đòn chuẩn xác (Khóa đòn bẩy -> Chốt hạn Schelling / Thấu cảm FBI -> Rút củi đáy nồi / Plan B)
  - `kairos_rhythm`: Nhịp điệu ra đòn (Khi nào im lặng, khi nào xuất chiêu)
  - `cited_units`: Danh sách mã đơn vị tri thức liên kết (`NT-LAW-*`, `NT-PRINCIPLE-*`, `NT-MODEL-*`, `NT-ANTI-PATTERN-*`).

### 1.2. Dịch vụ Án Điển (`backend/app/engine/cases_service.py`)
- Class `LivingCasesService`:
  - `list_dossiers(category=None, query=None)`: Trả về danh sách hồ sơ án điển kèm thống kê tổng quan.
  - `get_dossier(case_id)`: Trả về chi tiết 1 hồ sơ án điển.
  - `match_relevant_dossiers(scenario_text, top_k=2)`: Đối chiếu ngữ cảnh người dùng để đính kèm án điển máu thịt tương đồng nhất vào kết quả tham mưu.

### 1.3. Động cơ Định lượng Thời Thế & Quân Sư Hậu Trường (`backend/app/engine/nhan_thuat_api.py`)
- Hàm `compute_executive_metrics(scenario_text, mode="advisory", friction_score=None, homogeneity_score=None)`:
  - Tính toán:
    - `kairos_score` (0–100), `kairos_posture` (`ÁN BINH BẤT ĐỘNG - THỦ THẾ`, `NHƯỢNG BỘ CHIẾN THUẬT - CÂU GIỜ`, `XUẤT KÍCH CHỚP NHOÁNG - CHỐT HẠ`, `RÚT CỦI ĐÁY NỒI - TÁI CẤU TRÚC`), `silence_window` (nhịp điệu im lặng chiến thuật).
    - `leverage_score` (0–100), `leverage_position`, `switching_cost_pct`.
    - `cost_of_inaction_vnd` (Định lượng thiệt hại tài chính 30–45 ngày nếu chần chừ), `cost_breakdown`.
- Nâng cấp `process_nhan_thuat_analysis`:
  - Hỗ trợ `consigliere_mode: bool`. Khi bật, bổ sung khối `consigliere_brief` (Giải phẫu toan tính ngầm, Điểm gãy của đối phương, Kế sách 3 bước rút củi đáy nồi).
  - Đính kèm `executive_metrics` và `matched_cases` (2 án điển thực tế gần nhất).
- Nâng cấp `diagnose_person_role_fit` & `diagnose_team_structural_fit`:
  - Bổ sung `executive_metrics` (quy đổi ma sát nhận thức / bẫy đồng nhất thành `cost_of_inaction_vnd` cụ thể).

### 1.4. Giải Phẫu Đòn Đánh Sparring (`backend/app/main.py` & `frontend/app.html`)
- Nâng cấp phản hồi Sparring (`/api/v1/sparring/reply` & fallback client) để trả về `tactical_audit`:
  - `dominance_score` (0–100%)
  - `detected_vulnerability`: Điểm hở sườn trong câu nói vừa rồi của người dùng (ví dụ: giải thích quá nhiều, nhượng bộ sớm, để lộ nỗi sợ trễ hạn).
  - `counter_strike_upgrade`: Câu thoại nâng cấp sắc lạnh chuẩn FBI Tactical Empathy / Pháp gia.

---

## 2. Danh sách File Thêm Mới / Chỉnh Sửa
1. `knowledge/cases/living_dossiers.json` (Mới - 30 Án điển sống)
2. `backend/app/engine/cases_service.py` (Mới - Service tra cứu & đối chiếu Án điển)
3. `backend/app/engine/nhan_thuat_api.py` (Cập nhật - `compute_executive_metrics`, `consigliere_brief`, `matched_cases`)
4. `backend/app/main.py` (Cập nhật - Endpoints `/api/v1/cases/dossiers`, `/api/v1/cases/dossiers/<id>`, Sparring `tactical_audit`)
5. `frontend/app.html` (Cập nhật - Chế độ Mật Thất Quân Sư, Bảng Đồng Hồ Cảm Thức Thời Thế, Kho 30 Án Điển Sống, Bộ Giải Phẫu Đòn Đánh Sparring)
6. `tests/test_executive_consigliere_engine.py` (Mới - Unit & Integration tests)

---

## 3. Kế hoạch Kiểm thử (Verification Plan)
- `.venv\Scripts\pytest tests/test_executive_consigliere_engine.py tests/test_frontend_dom_behavior.py tests/test_ui_2_0_integration.py tests/test_commercial_and_iching_api.py tests/test_iching_matrix_v2.py`
- `python scripts/validate_all.py`
- `.venv\Scripts\ruff check backend/ tests/ scripts/ src/`
