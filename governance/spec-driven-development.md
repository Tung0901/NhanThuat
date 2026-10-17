# Nhân Thuật Spec-Driven Development (NT-SDD) Protocol

**ID:** NT-GOV-SDD-001  
**Version:** 0.1.0  
**Status:** approved  
**Approved By:** Product Owner (2026-10-15)  
**Owner:** Product Owner  
**Created:** 2026-10-15  
**Updated:** 2026-10-15  
**Governing Authority:** [PROJECT_CONSTITUTION.md](../PROJECT_CONSTITUTION.md)

---

## 1. Mục đích & Tầm nhìn

Quy chuẩn **Nhân Thuật Spec-Driven Development (NT-SDD)** được thiết kế dựa trên phương pháp luận chuẩn của GitHub Spec-Kit, được tinh chỉnh và bản địa hóa để tương thích tuyệt đối với Hiến chương Nhân Thuật ([PROJECT_CONSTITUTION.md](../PROJECT_CONSTITUTION.md)), các quyết định kiến trúc ([docs/adr/](../docs/adr/)) và nguyên tắc quản trị Frozen State.

Mục tiêu cốt lõi:
- **Xóa bỏ triệt để "Vibe Coding"**: Mọi thay đổi kỹ thuật hoặc tri thức đều phải được đặc tả (Specify), lập phương án kiến trúc (Plan), phân rã công việc (Tasks) trước khi Agent bắt đầu viết code (Implement).
- **Tuân thủ phân tầng (ADR-0002)**: Phân tách rạch ròi giữa Tầng Tri thức (Knowledge Content) và Tầng Động cơ (Engine & Web App).
- **Bảo toàn quyền lực Product Owner (PO Authority)**: Agent chỉ thực thi, kiểm thử và chuẩn bị hồ sơ bằng chứng; quyền phê duyệt (Approved) và đóng băng (Frozen) thuộc độc quyền của PO.

---

## 2. Vòng đời SDD chuẩn trong Nhân Thuật

```
[ Ý tưởng / Yêu cầu ]
        │
        ▼
   1. SPECIFY (Đặc tả)          ──> specs/<feature_id>/spec.md
        │                           - User scenarios, scope, acceptance criteria
        │                           - Đánh giá tác động Schema & Frozen content
        ▼
   2. PLAN (Thiết kế kỹ thuật)  ──> specs/<feature_id>/plan.md
        │                           - Architecture blueprint, ADR alignment
        │                           - Tách bạch Content vs Engine
        ▼
   3. TASKS (Phân rã việc)      ──> specs/<feature_id>/tasks.md
        │                           - Task tuần tự, checklist nghiệm thu
        │                           - Các lệnh test tự động định sẵn
        ▼
   4. IMPLEMENT (Thực thi)      ──> Agent thực thi từng task theo checklist
        │                           - Không nhảy cóc, không sửa ngoài phạm vi
        ▼
   5. VERIFY (Kiểm chứng)       ──> Chạy test suites, linters, validators
        │                           - scripts/validate_all.py
        │                           - pytest, ruff check
        ▼
   6. DOSSIER (Trình duyệt)     ──> Hồ sơ nghiệm thu gửi Product Owner
        │                           - Trạng thái: ready_for_review
        ▼
[ Product Owner Quyết định ]    ──> Approved / Frozen (hoặc Yêu cầu chỉnh sửa)
```

---

## 3. Quy tắc bắt buộc cho AI Agents

1. **Hiến pháp tối thượng**: Mọi nội dung trong `spec.md`, `plan.md` phải tuân thủ điều khoản của [PROJECT_CONSTITUTION.md](../PROJECT_CONSTITUTION.md). Không được đề xuất phá vỡ Frozen items nếu không có quy trình Change Request chính thức.
2. **Không tự phong Approved/Frozen**: Agent chỉ được cập nhật trạng thái tối đa đến `ready_for_review`.
3. **Evidence-First**: Không có deliverable nào được coi là hoàn tất nếu thiếu bằng chứng thực tế từ `validate_all.py` và `pytest`.
4. **Phạm vi cô lập (Scoping)**: Agent chỉ được sửa các file đã được liệt kê trong `plan.md` và `tasks.md`. Mọi phát sinh ngoài phạm vi phải báo cáo để bổ sung vào spec.
