---
name: nhanthuat-sdd
description: Spec-Driven Development (SDD) protocol customized for the Nhan Thuat repository. Enforces rigorous requirement specification, architecture planning, and task execution under Nhan Thuat Constitution and governance rules.
---

# Nhân Thuật Spec-Driven Development (NT-SDD) Skill

## 1. Mục đích
Skill này hướng dẫn AI Agent thực thi mọi yêu cầu phát triển tính năng, sửa lỗi (bug-fixing), hoặc đánh giá đề xuất mới theo quy chuẩn **Spec-Driven Development** của dự án Nhân Thuật, đảm bảo:
- Tuyệt đối tuân thủ [PROJECT_CONSTITUTION.md](../../PROJECT_CONSTITUTION.md) và quyền phê duyệt tối thượng của Product Owner.
- Tách bạch giữa **Tầng Tri thức (Knowledge Content)** và **Tầng Động cơ (Knowledge Engine)** theo ADR-0002.
- Không phát sinh code tùy hứng ("vibe coding"), mọi dòng code sinh ra đều phải được kiểm chứng bằng test suites tự động.

---

## 2. Các Lệnh / Quy trình Hành động (Workflows)

Khi nhận một nhiệm vụ mới từ người dùng, Agent xác định loại công việc và thực hiện theo đúng luồng:

### Workflow A: Phát triển Tính năng / Module mới (Feature Development)
1. **Khởi tạo Specification (`spec.md`)**:
   - Sử dụng mẫu `governance/sdd-templates/01_SPEC_TEMPLATE.md`.
   - Lưu tại `specs/<feature-name>/spec.md`.
   - Xác định rõ: Bối cảnh, User scenarios, Tách bạch Content vs Engine, Acceptance Criteria.
2. **Thiết kế Kỹ thuật (`plan.md`)**:
   - Sử dụng mẫu `governance/sdd-templates/02_PLAN_TEMPLATE.md`.
   - Lưu tại `specs/<feature-name>/plan.md`.
   - Liệt kê chính xác các file sẽ thêm/sửa, hợp đồng API, và các lệnh test tự động.
3. **Phân rã Công việc (`tasks.md`)**:
   - Sử dụng mẫu `governance/sdd-templates/03_TASKS_TEMPLATE.md`.
   - Lưu tại `specs/<feature-name>/tasks.md`.
   - Chia nhỏ thành từng task độc lập, có lệnh xác minh cụ thể.
4. **Thực thi tuần tự (Implementation)**:
   - Làm từng task một, cập nhật trạng thái checklist `[x]` trong `tasks.md`.
   - Sau mỗi task, chạy lệnh kiểm tra cú pháp và unit test tương ứng.
5. **Kiểm chứng Toàn diện & Trình duyệt (PO Review)**:
   - Chạy toàn bộ bộ test hồi quy:
     ```bash
     python -m ruff check src backend tests scripts
     pytest
     python scripts/validate_all.py
     ```
   - Chuyển trạng thái sang `ready_for_review` và trình Product Owner duyệt.

---

### Workflow B: Sửa lỗi có Bằng chứng (Evidence-Based Bug Fixing)
1. Sử dụng mẫu `governance/sdd-templates/04_BUG_FIX_TEMPLATE.md`.
2. Tạo test case tái hiện lỗi trước (`reproduction test`), chạy phải FAIL.
3. Khoanh vùng sửa code tối thiểu (Minimal Scoped Fix).
4. Chạy lại test tái hiện $\rightarrow$ PASS, chạy toàn bộ regression tests $\rightarrow$ PASS.
5. Đóng bug kèm biên bản bằng chứng.

---

### Workflow C: Thẩm định Ý tưởng / Thấu kính mới (Idea Assessment)
1. Sử dụng mẫu `governance/sdd-templates/05_IDEA_ASSESSMENT_TEMPLATE.md`.
2. Đánh giá tác động đến Hiến chương, rủi ro vỡ schema YAML/JSON, và chi phí duy trì.
3. Đưa ra 1 trong 3 khuyến nghị: **GO**, **CLARIFY**, hoặc **STOP** cho Product Owner quyết định.

---

## 3. Điều cấm Kỷ luật (Strict Prohibitions)
- **CẤM**: Tự ý sửa đổi nội dung đã `frozen` mà không có Change Request được PO duyệt.
- **CẤM**: Tự ý ghi trạng thái `approved` hoặc `frozen`. Agent chỉ được ghi tối đa là `ready_for_review`.
- **CẤM**: Bỏ qua bước kiểm tra `scripts/validate_all.py` hoặc `pytest`.
