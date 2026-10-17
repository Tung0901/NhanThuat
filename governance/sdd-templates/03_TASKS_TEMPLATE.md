# [FEATURE_ID]: [Tên Tính Năng / Đề Xuất] — Task Breakdown

**ID:** TASKS-[MÃ_TÍNH_NĂNG]  
**Spec & Plan Tham Chiếu:** SPEC-[MÃ_TÍNH_NĂNG] / PLAN-[MÃ_TÍNH_NĂNG]  
**Trạng thái:** draft | in_progress | completed  

---

## Danh sách Công việc Tuần tự (Ordered Implementation Tasks)

### Giai đoạn 1: Chuẩn bị & Hợp đồng Giao diện (Contracts & Scaffolding)
- [ ] **TASK-01**: Khai báo cấu trúc dữ liệu / schema / types.
  - *Tệp tác động:* `...`
  - *Lệnh kiểm tra:* `python -m py_compile ...`
- [ ] **TASK-02**: Viết test cases kiểm thử ban đầu (Test-first / TDD).
  - *Tệp tác động:* `tests/...`
  - *Lệnh kiểm tra:* `pytest tests/...` (Dự kiến FAIL hợp lệ trước khi implement).

### Giai đoạn 2: Hiện thực hóa Logic (Core Implementation)
- [ ] **TASK-03**: Triển khai logic xử lý chính trong engine / backend.
  - *Tệp tác động:* `...`
  - *Lệnh kiểm tra:* `pytest tests/...` (Dự kiến PASS).
- [ ] **TASK-04**: Tích hợp với Router / Service / UI.
  - *Tệp tác động:* `...`
  - *Lệnh kiểm tra:* `pytest tests/...`

### Giai đoạn 3: Kiểm chứng Toàn diện & Hồ sơ Nghiệm thu (Verification & Dossier)
- [ ] **TASK-05**: Chạy toàn bộ bộ kiểm tra hồi quy:
  - `python -m ruff check src backend tests scripts`
  - `pytest -v`
  - `python scripts/validate_all.py`
- [ ] **TASK-06**: Lập biên bản nghiệm thu (Dossier) và cập nhật [TASK_QUEUE.md](../../TASK_QUEUE.md) trình Product Owner.
