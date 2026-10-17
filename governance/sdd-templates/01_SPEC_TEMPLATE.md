# [FEATURE_ID]: [Tên Tính Năng / Đề Xuất] — Specification

**ID:** SPEC-[MÃ_TÍNH_NĂNG]  
**Epic Liên Quan:** NT-EPIC-[XX]  
**Tác giả:** [Tên người đề xuất / Agent]  
**Người duyệt:** Product Owner  
**Trạng thái:** draft | ready_for_review  
**Ngày tạo:** YYYY-MM-DD  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)
- **Vấn đề cần giải quyết:** Mô tả rõ vấn đề thực tế của người dùng hoặc điểm nghẽn trong hệ thống hiện tại.
- **Mục tiêu đạt được:** Kết quả cụ thể sau khi hoàn thành tính năng này.
- **Ngoài phạm vi (Out of Scope):** Những gì cố tình KHÔNG làm trong đợt này để tránh phình phạm vi (scope creep).

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories & Requirements)
- **User Story 1:** Với vai trò là [Người dùng / Quản trị viên / Council Engine], tôi muốn [hành động] để [lợi ích].
  - *Kịch bản kiểm thử:*
    - Given: [Điều kiện ban đầu]
    - When: [Hành động kích hoạt]
    - Then: [Kết quả mong đợi]
- **User Story 2:** ...

---

## 3. Ranh giới Tách biệt Tầng (Architecture Boundary Check - ADR-0002)
- [ ] Tính năng thuộc về **Knowledge Content** (Dữ liệu tri thức, Schema YAML, Thấu kính triết học)?
- [ ] Tính năng thuộc về **Knowledge Engine** (Python Backend, API Gateway, Council Router)?
- [ ] Tính năng thuộc về **Presentation Layer** (Web Studio, UI frontend/app.html)?
*(Lưu ý: Nếu chạm vào cả Content và Engine, phải mô tả rõ giao diện kết nối giữa hai bên, không được trộn lẫn logic)*.

---

## 4. Đánh giá Tác động Quản trị (Governance & Impact Analysis)
- **Ảnh hưởng đến Frozen Items?** [ ] Có  [ ] Không  
  *(Nếu có, bắt buộc phải có Change Request kèm lý do và kế hoạch backward compatibility)*.
- **Ảnh hưởng đến Schema YAML/JSON?** [ ] Có  [ ] Không
- **Domain Areas liên quan:** NT-DA-XXXX

---

## 5. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)
- [ ] AC-1: [Tiêu chí kiểm chứng 1]
- [ ] AC-2: [Tiêu chí kiểm chứng 2]
- [ ] AC-3: Toàn bộ test suite `pytest` chạy pass 100%.
- [ ] AC-4: `python scripts/validate_all.py` chạy exit code 0.
- [ ] AC-5: `ruff check` không có lỗi linting.
