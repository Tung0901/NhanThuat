# SPEC-EXECUTIVE-CONSIGLIERE-ENGINE: Kích Hoạt Linh Hồn Thực Chiến Nhân Thuật (Consigliere Mode, 30 Án Điển Sống, Định Lượng Thời Thế & Đấu Trí Sát Thủ)

**ID:** SPEC-EXECUTIVE-CONSIGLIERE-ENGINE  
**Epic Liên Quan:** NT-EPIC-05 (Knowledge Engine AI) / NT-EPIC-06 (Usable Product)  
**Tác giả:** Main Agent (AI Coding Assistant)  
**Người duyệt:** Product Owner (Approved artifact `ke-hoach-kich-hoat-linh-hon-thuc-chien-nhan-thuat.md`)  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-11-10  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)
- **Vấn đề cần giải quyết:**
  1. Nhân Thuật hiện có khung lý thuyết và quy luật đồ sộ nhưng còn mang dáng dấp của một "Giáo sư học thuật trên bục giảng", thiếu độ lạnh của thực tế (Realpolitik), sự thấu cảm nỗi cô đơn quyền lực và bản năng ra đòn chính xác của một "Tham mưu trưởng thân tín hậu trường" (Executive Consigliere).
  2. Thư mục `knowledge/cases/` hiện chỉ có file giữ chỗ `.gitkeep`, thiếu các hồ sơ án điển máu thịt có số liệu thiệt hại thật và đòn giải phẫu cụ thể.
  3. Khả năng định lượng tài chính & thời thế còn mỏng: thiếu chỉ số Thời thế (Kairos Timing Index), Tương quan đòn bẩy (Leverage Ratio), và Chi phí trì hoãn quy đổi ra tiền mặt (Cost of Inaction - VNĐ).
  4. Thao trường đối kháng (Sparring Arena) chưa có bộ phân tích sơ hở đòn đánh tức thì (Tactical Strike Analyzer) sau mỗi hiệp đối thoại.
- **Mục tiêu đạt được:**
  1. **Giai đoạn 1 (Executive Consigliere & Mật Thất Chiến Lược):** Tích hợp chế độ Quân Sư Thân Tín (`consigliere_mode`) và giao thức Zero-BS Directive bóc tách thẳng thắn quyền lực ngầm, thế chân vạc, phương án rút củi đáy nồi.
  2. **Giai đoạn 2 (Kho 30 Án Điển Sống - Living Case Dossiers):** Xây dựng `knowledge/cases/living_dossiers.json` gồm 30 ca bệnh thực chiến (Tranh chấp cổ đông/nội bộ, Khủng hoảng hiện trường/công trường, Đàm phán sinh tử/thu nợ) cùng API và giao diện tra cứu giải phẫu chuyên sâu.
  3. **Giai đoạn 3 (Bảng Đồng Hồ Cảm Thức Thời Thế & Định Lượng Rủi Ro):** Bổ sung `executive_metrics` (Chỉ số Thời Thế Kairos, Nhịp điệu im lặng chiến thuật, Đòn bẩy quyền lực, Chi phí trì hoãn VNĐ) vào động cơ phân tích và chẩn đoán.
  4. **Giai đoạn 4 (Thao Trường Đấu Trí Sát Thủ):** Nâng cấp Sparring Arena với các kịch bản đối thủ thực địa và khung Giải Phẫu Sơ Hở & Phản Đòn (Tactical Strike Analyzer).
- **Ngoài phạm vi (Out of Scope):**
  - Không thay đổi các đơn vị tri thức đã `frozen` trong `knowledge/units/` hay `governance/frozen-register.yaml`.
  - Không vi phạm ranh giới đạo đức pháp luật hay mở cơ chế bói toán mê tín (`cast_oracle` giữ nguyên trạng thái fail-closed).

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories)
- **User Story 1 (Mật Thất Tham Mưu - Consigliere Mode):** Nhà lãnh đạo có thể bật chế độ "Mật Thất Quân Sư (Realpolitik)" trong Advisory Cockpit để nhận phân tích thẳng thắn, không giáo điều, kèm kịch bản 3 bước chuyển giao quyền lực và khóa đòn bẩy.
- **User Story 2 (Kho 30 Án Điển Sống):** Người dùng có thể truy cập 30 Án Điển Giải Phẫu Sống chia theo 3 chiến trường, xem bản đồ thế lực, sai lầm chí mạng, thiệt hại định lượng bằng tiền mặt, và đòn đánh chuẩn lẽ ra phải xuất.
- **User Story 3 (Bảng Đồng Hồ Thời Thế & Chi Phí Trì Hoãn):** Khi chạy Tham vấn hoặc Chẩn đoán (Person-Role Fit / Team Fit), người dùng nhìn thấy ngay Bảng Đồng Hồ Cảm Thức Thời Thế (Kairos Score, Đòn bẩy %, Nhịp im lặng chiến thuật, và Chi phí rủi ro VNĐ nếu chần chừ 30–45 ngày).
- **User Story 4 (Thao Trường Đấu Trí Sát Thủ):** Khi đấu trí trong Sparring Arena, mỗi lượt phản hồi được giải phẫu ngay: độ áp chế đòn bẩy, điểm hở sườn vừa mắc phải, và câu thoại phản đòn chuẩn FBI/Hàn Phi Tử.

---

## 3. Ranh giới Tách biệt Tầng (ADR-0002)
- **Knowledge Content:** `knowledge/cases/living_dossiers.json` lưu trữ 30 hồ sơ án điển thực chiến có cấu trúc chuẩn và liên kết tới các mã `NT-LAW-*`, `NT-MODEL-*`, `NT-PRINCIPLE-*`, `NT-ANTI-PATTERN-*`.
- **Knowledge Engine:**
  - `backend/app/engine/cases_service.py`: Dịch vụ tải, tìm kiếm, lọc theo chiến trường và gợi ý án điển liên quan.
  - `backend/app/engine/nhan_thuat_api.py`: Bổ sung tính toán `executive_metrics` (Kairos, Leverage, Cost of Inaction), chế độ `consigliere_mode`, và phân tích đòn đánh Sparring.
  - `backend/app/main.py`: Các endpoints `/api/v1/cases/dossiers`, `/api/v1/cases/dossiers/<id>`.
- **Presentation Layer:** `frontend/app.html` hiển thị chế độ Mật Thất Quân Sư, Bảng Đồng Hồ Thời Thế, Kho 30 Án Điển Sống và Bộ Giải Phẫu Đòn Đánh Sparring.

---

## 4. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)
- [ ] AC-1: `knowledge/cases/living_dossiers.json` chứa đủ 30 án điển thực chiến thuộc 3 nhóm chiến trường với đầy đủ trường định lượng thiệt hại và kịch bản giải phẫu.
- [ ] AC-2: API `/api/v1/cases/dossiers` và `/api/v1/cases/dossiers/<id>` hoạt động chuẩn xác, hỗ trợ lọc theo `category` và từ khóa `q`.
- [ ] AC-3: `process_nhan_thuat_analysis`, `diagnose_person_role_fit`, `diagnose_team_structural_fit` trả về `executive_metrics` định lượng đầy đủ (Kairos score, Leverage ratio, Cost of inaction VNĐ, Silence window).
- [ ] AC-4: Giao diện `frontend/app.html` tích hợp mượt mà chế độ Consigliere, Bảng Đồng Hồ Cảm Thức Thời Thế, Kho 30 Án Điển và Giải Phẫu Đòn Đánh Sparring đồng bộ phong cách Obsidian-Gold chống AI.
- [ ] AC-5: Toàn bộ test hiện hữu và test mới (`tests/test_executive_consigliere_engine.py`) PASS 100%, `scripts/validate_all.py` và `ruff check` sạch lỗi.
