# PLAN-LENS-ICHING-TIMING: Tích hợp Thấu kính Dịch Học & Thời Thế — Technical Plan

**ID:** PLAN-LENS-ICHING-TIMING  
**Spec Tham Chiếu:** SPEC-LENS-ICHING-TIMING  
**Người lập:** Main Agent  
**Trạng thái:** ready_for_review  

---

## 1. Thiết kế Kiến trúc (Architecture Blueprint)
- **Council contract:** `CouncilEngine.deliberate()` luôn tạo đúng 7 pitch. Output
  được kiểm tra completeness trước khi chấp nhận nhánh LLM.
- **Content boundary:** Hai pitch mới đọc cấu trúc từ `iching_engine.json` và
  `timing_engine.json`; API chỉ điều phối.
- **Depth contract:** Mở rộng `PerspectivePitch` bằng `situation_read`,
  `assumptions`, `recommended_actions`, `evidence_needed`, `confidence_note`.
- **Runtime authorization:** Ghi nhận quyền kích hoạt của Product Owner trong
  metadata engine nhưng không đổi tài liệu nguồn sang Frozen.
- **Presentation:** Renderer chuyển từ grid tóm tắt sang báo cáo dọc, hiển thị
  toàn bộ trường và escape dữ liệu động.

---

## 2. Danh sách Tệp tin Tác động

| Tệp tin | Hành động | Vai trò |
| :--- | :--- | :--- |
| `backend/app/engine/philosophies/iching_engine.json` | Xác minh | Kiểm tra schema metadata, cấu trúc `six_dragon_states` |
| `backend/app/engine/philosophies/timing_engine.json` | Sửa | Bổ sung metadata runtime và hiệu chỉnh câu chữ tuyệt đối |
| `backend/app/engine/philosophies/router.py` | Sửa | Cho hai lens được PO cấp quyền tham gia routing |
| `src/nhan_thuat/council/models.py` | Sửa | Mở rộng hợp đồng pitch sâu |
| `src/nhan_thuat/council/council_engine.py` | Sửa | 7 lens, validation LLM và fallback đầy đủ |
| `frontend/app.html` | Sửa | Hiển thị báo cáo đủ 7 lens |
| `tests/test_iching_and_timing_engine.py` | Sửa | Test 7 lens và độ sâu |
| `tests/test_phase4_enterprise_council.py` | Sửa | Regression hợp đồng Hội đồng |
| `tests/test_commercial_and_iching_api.py` | Sửa | Oracle tiếp tục fail-closed |

---

## 3. Kế hoạch Kiểm chứng (Verification Plan)
1. Kiểm tra biên dịch & cú pháp:
   ```bash
   python -m py_compile backend/app/engine/philosophies/router.py
   python -m ruff check backend/app/engine/philosophies/
   ```
2. Chạy test suite riêng cho 2 thấu kính mới:
   ```bash
   pytest tests/test_iching_and_timing_engine.py -v
   ```
3. Chạy kiểm tra hồi quy toàn dự án:
   ```bash
   pytest
   python scripts/validate_all.py
   ```

## 4. Bằng chứng Thực thi
- `uv run --extra dev ruff check ...`: đạt.
- `uv run --extra dev pytest`: đạt 100%.
- `uv run python scripts/validate_all.py`: `Validation passed: all managed documents are valid.`
- Oracle 64 quẻ vẫn fail-closed với `ORACLE_UNAVAILABLE`.
