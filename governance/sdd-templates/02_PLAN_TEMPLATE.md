# [FEATURE_ID]: [Tên Tính Năng / Đề Xuất] — Technical Plan

**ID:** PLAN-[MÃ_TÍNH_NĂNG]  
**Spec Tham Chiếu:** SPEC-[MÃ_TÍNH_NĂNG]  
**Người lập:** [Tên người lập / Agent]  
**Trạng thái:** draft | ready_for_review  

---

## 1. Bản vẽ Thiết kế Kiến trúc (Architectural Blueprint)
- **Tổng quan giải pháp kỹ thuật:** Mô tả cách tiếp cận mã nguồn hoặc luồng xử lý dữ liệu.
- **Sơ đồ luồng (Flowchart / Sequence):** (Dùng định dạng Markdown / Mermaid nếu cần).
- **Các ADR liên quan:** Tham chiếu đến ADR-0001, ADR-0002, ADR-0019,...

---

## 2. Danh sách Tệp tin Ảnh hưởng (Impacted Files & Scoping)

| Tệp tin | Loại hành động (Thêm mới / Sửa / Xóa) | Trách nhiệm |
| :--- | :--- | :--- |
| `path/to/file1.py` | Sửa | Thêm hàm xử lý X |
| `path/to/file2.json` | Thêm mới | Khai báo engine Y |
| `tests/test_x.py` | Thêm mới | Test cases bao phủ |

---

## 3. Thiết kế Dữ liệu & Giao diện Hợp đồng (Data & Interface Contracts)
- **Data Models / Schemas:** Khai báo cấu trúc JSON/Pydantic/Dataclass (input, output, validation rules).
- **API Endpoints (nếu có):**
  - Method & Path: `POST /api/v1/...`
  - Request format & Response format
  - Mã lỗi và kịch bản fallback

---

## 4. Chiến lược Thử nghiệm & Kiểm chứng (Testing & Verification Strategy)
- **Unit Tests:** Kiểm tra các hàm logic độc lập.
- **Integration Tests:** Kiểm tra tương thích với router / pipeline.
- **Regression Tests:** Đảm bảo không phá vỡ 184 tests hiện tại.
- **Lệnh xác thực tự động:**
  - `python -m py_compile <changed_files>`
  - `ruff check <changed_files>`
  - `pytest tests/<target_test>.py -v`
  - `python scripts/validate_all.py`

---

## 5. Rủi ro Kỹ thuật & Phương án Dự phòng (Technical Risks & Fallbacks)
- Rủi ro 1: ... $\rightarrow$ Phương án xử lý: ...
- Chế độ Fallback khi không có API key / lỗi runtime: ...
