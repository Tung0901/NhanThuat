# SPEC-ICHING-MATRIX-V2: Nâng Cấp Toàn Diện Ma Trận 64 Quẻ Biến Dịch & 8 Cung Quản Trị — Specification

**ID:** SPEC-ICHING-MATRIX-V2  
**Epic Liên Quan:** NT-EPIC-06 (Usable Product) / NT-EPIC-05 (Knowledge Engine AI)  
**Tác giả:** Main Agent (AI Coding Assistant)  
**Người duyệt:** Product Owner (Approved proposal PROP-ICHING-MATRIX-V2)  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-11-09  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)
- **Vấn đề cần giải quyết:** Module Ma trận 64 quẻ dịch hiện tại ở `frontend/app.html` còn sơ sài:
  1. Chỉ là một danh sách thẻ phẳng (flat card grid) lọc theo 8 Cung, chưa phải một "Ma trận" đúng nghĩa (bàn cờ tọa độ 8x8 giữa Ngoại Quái thời cuộc và Nội Quái nội lực).
  2. Thiếu tính năng "Biến Dịch": các quẻ tĩnh, không có cơ chế mô phỏng biến hào (State Transition), thiếu hệ tứ quái phản chiếu (Quẻ Hỗ, Quẻ Thác, Quẻ Tung).
  3. Bỏ quên trục chu kỳ 12 Quẻ Tiêu Trưởng (Thập Nhị Tức Quái) biểu diễn nhịp đập sinh mệnh tổ chức.
  4. Trải nghiệm tra cứu thụ động, thiếu công cụ chẩn đoán tình thế theo triệu chứng thực tế của doanh nghiệp.
  5. Drawer hiển thị chi tiết chật hẹp, ký tự unicode quá nhỏ, thiếu đồ giải Lục Hào (6 vạch âm dương) tương tác và chưa kết nối với 379 Đơn vị Tri thức (Knowledge Units) trong hệ thống.
- **Mục tiêu đạt được:**
  1. Xây dựng Bàn cờ Ma trận Tương tác 8x8 (Ngoại Quái x Nội Quái) chuẩn tắc dịch học quản trị.
  2. Bổ sung chế độ xem Vòng Chu Kỳ 12 Tức Quái biểu diễn hình sin năng lượng Âm/Dương tổ chức.
  3. Xây dựng Động cơ Biến Hào & Chuyển Pha (State Transition Simulator) cho phép click đổi Hào (1..6) để tính Quẻ Biến tức thì, cùng hệ Tứ Quái (Gốc - Hỗ - Thác - Tung).
  4. Xây dựng Bộ Chẩn Đoán Tình Thế Doanh Nghiệp (Organizational Diagnostic Assistant) theo triệu chứng thực tế.
  5. Nâng cấp đồ giải Lục Hào SVG tương tác và Modal Inspector 4 tab chuyên sâu, liên kết với 379 Knowledge Units và Case Studies.
  6. Duy trì 100% backward compatibility với các test hiện hữu (`test_commercial_and_iching_api.py`, `test_frontend_dom_behavior.py`).
- **Ngoài phạm vi (Out of Scope):**
  - Tuyệt đối không mở cơ chế bói toán / divination (`cast_oracle` vẫn giữ trạng thái fail-closed an toàn theo Hiến chương).
  - Không tự ý Frozen nội dung hay thay đổi các file đã Frozen trong Epic 0 và Epic 1.

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories)
- **User Story 1 (Đa Chế Độ Xem):** Người dùng có thể chuyển đổi linh hoạt giữa 4 View:
  - View 1: `matrix_8x8` (Bàn cờ ma trận 8x8 giao điểm Ngoại quái x Nội quái).
  - View 2: `sovereign_12` (Vòng chu kỳ 12 Quẻ Tiêu Trưởng theo nhịp sinh suy tổ chức).
  - View 3: `cards_grid` (Lưới thẻ Lục Hào V2 với đồ giải SVG và badges phân loại).
  - View 4: `diagnostics` (Bộ chẩn đoán tình thế theo 4 nhóm triệu chứng).
- **User Story 2 (Mô Phỏng Biến Hào & Chuyển Pha):** Khi xem một quẻ, người dùng có thể click vào bất kỳ Hào nào (1..6) để xem Quẻ Biến và kịch bản can thiệp, đồng thời xem được Quẻ Hỗ, Quẻ Thác, Quẻ Tung.
- **User Story 3 (Chẩn Đoán Tình Thế Doanh Nghiệp):** Lãnh đạo chọn 1 hoặc nhiều vấn đề thực tế (dòng tiền, xung đột nội bộ, áp lực đối thủ...), hệ thống tự động gợi ý nhóm Quẻ tương ứng và tư thế chiến lược (Tiến, Thoái, Thủ, Biến).
- **User Story 4 (Executive Inspector 4 Tab):** Khi mở chi tiết quẻ, hệ thống hiển thị Modal chuyên sâu 4 tab: (1) Thời Thế & Cảnh Báo, (2) Đồ Giải Lục Hào & Vị Trí Quyền Lực, (3) Chuyển Pha & Hệ Quẻ Liên Quan, (4) Tri Thức Liên Đới & Case Study.
- **User Story 5 (Bảo Toàn Kỷ Cương & Kiểm Thử):** Tất cả unit tests và integration tests phải PASS 100%, không vi phạm Hiến chương hay làm vỡ bất kỳ luồng hoạt động nào của web app.

---

## 3. Ranh giới Tách biệt Tầng (ADR-0002)
- **Knowledge Content:** Dữ liệu chuẩn hóa 64 quẻ, ngoại/nội quái, 6 hào, quẻ hỗ/thác/tung, 12 quẻ tức trong `backend/app/engine/philosophies/iching_64_hexagrams.json`.
- **Knowledge Engine:** `backend/app/engine/philosophies/iching_service.py` thực hiện logic tra cứu, tính toán quẻ biến, bàn cờ 8x8, lọc chẩn đoán; API Gateway trong `backend/app/main.py`.
- **Presentation Layer:** Giao diện người dùng trong `frontend/app.html` hiển thị tương tác, modal inspector, đồ giải SVG.

---

## 4. Đánh giá Tác động Quản trị (Governance & Impact Analysis)
- **Ảnh hưởng đến Frozen Items?** Không.
- **Ảnh hưởng đến Schema YAML/JSON?** Không làm vỡ schema hiện tại; mở rộng trường trong JSON engine của thấu kính I Ching.
- **Domain Areas liên quan:** `NT-DA-0005` (Chiến lược & Thời thế), `NT-DA-0023` (Động lực học chu kỳ Chu Dịch).

---

## 5. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)
- [ ] AC-1: `iching_64_hexagrams.json` có đủ 64 quẻ với cấu trúc 6 hào, ngoại quái, nội quái, quẻ hỗ/thác/tung, binary pattern, 12 quẻ tức và liên kết tri thức.
- [ ] AC-2: `IChingService` cung cấp các hàm `get_hexagram`, `get_matrix_8x8`, `get_sovereign_hexagrams`, `simulate_transition`, `diagnose_phase`.
- [ ] AC-3: API endpoints `/api/v1/iching/hexagrams`, `/api/v1/iching/hexagrams/{id}`, `/api/v1/iching/matrix-8x8`, `/api/v1/iching/sovereign` hoạt động chuẩn xác.
- [ ] AC-4: UI `frontend/app.html` hỗ trợ chuyển đổi mượt mà giữa 4 view (`matrix_8x8`, `sovereign_12`, `cards_grid`, `diagnostics`), có đồ giải Lục Hào SVG tương tác và Modal Inspector 4 tab.
- [ ] AC-5: Toàn bộ test suite `pytest` chạy PASS 100% (bao gồm `test_commercial_and_iching_api.py`, `test_frontend_dom_behavior.py` và test mới).
- [ ] AC-6: `python scripts/validate_all.py` chạy exit code 0.
- [ ] AC-7: `ruff check` sạch sẽ, không có lỗi linting.
