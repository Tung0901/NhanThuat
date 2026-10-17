# BUG-[MÃ_BUG]: [Mô tả ngắn gọn lỗi] — Bug Fix Record

**ID:** BUG-[MÃ_BUG]  
**Mức độ nghiêm trọng (Severity):** Low | Medium | High | Critical  
**Người xử lý:** Agent / Kỹ sư  
**Trạng thái:** triaged | reproducing | in_fix | verified | closed  
**Ngày ghi nhận:** YYYY-MM-DD  

---

## 1. Triệu chứng & Tác động (Symptoms & Impact)
- **Hành vi sai lệch:** Hệ thống trả về lỗi gì hoặc xử lý sai ở bước nào?
- **Hành vi kỳ vọng:** Đúng chuẩn theo Hiến chương / Spec là gì?
- **Phạm vi tác động:** Có ảnh hưởng tới dữ liệu Frozen hay người dùng Web App không?

---

## 2. Phân tích Nguyên nhân Gốc rễ (Root Cause Analysis - RCA)
- **Tệp tin & dòng code gây lỗi:** `path/to/file.py:LXX`
- **Nguyên nhân cốt lõi:** Lỗi logic, lỗi schema, thiếu case xử lý ngoại lệ hay lỗi môi trường?

---

## 3. Test Case Tái Hiện (Reproduction Test)
- **File test tái hiện:** `tests/test_bug_[id].py` (hoặc test function trong test suite có sẵn)
- **Lệnh chạy tái hiện:** `pytest tests/... -k "test_bug_..."` (Phải FAILED trước khi sửa)

---

## 4. Phương án Khắc phục (Scoped Fix)
- Mô tả phạm vi chỉnh sửa tối thiểu (Minimal Scoped Fix), không làm phình code thừa.
- Danh sách tệp sửa:
  - `...`

---

## 5. Bằng chứng Kiểm chứng (Verification Evidence)
- [ ] Test tái hiện đã chuyển sang **PASS**.
- [ ] Toàn bộ test suite hồi quy `pytest` pass 100%.
- [ ] `scripts/validate_all.py` pass.
- [ ] `ruff check` pass.
