# SPEC-LENS-ICHING-TIMING: Tích hợp Thấu kính Dịch Học & Thời Thế — Specification

**ID:** SPEC-LENS-ICHING-TIMING  
**Epic Liên Quan:** NT-EPIC-05 / NT-EPIC-06  
**Tác giả:** Main Agent  
**Người duyệt:** Product Owner  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-10-15  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)
- **Vấn đề cần giải quyết:** Hội đồng hiện chỉ trả về 5 trường phái, phần trình bày
  quá ngắn và fallback viết cứng theo một tình huống nhà cung cấp. Hai lens Dịch
  học và Thời thế có dữ liệu nhưng đang bị loại khỏi phân tích runtime.
- **Mục tiêu đạt được:** 
  1. Cho đủ 7 trường phái cùng tham gia Hội đồng theo chỉ thị runtime của Product Owner.
  2. Mỗi trường phái phải trả về nhận định tình thế, giả định, tối thiểu 4 lập luận,
     tối thiểu 3 hành động, dữ liệu cần kiểm chứng, cảnh báo và ghi chú độ tin cậy.
  3. Giữ Dịch học là khung ẩn dụ định tính, không gieo quẻ, dự báo số phận hoặc
     thay thế dữ liệu pháp lý, tài chính và nhân sự.
  4. Đảm bảo toàn bộ regression tests và validator đạt.
- **Ngoài phạm vi:** Không mở oracle casting, không Frozen tài liệu và không dùng
  danh mục 64 quẻ làm cơ chế bói toán.

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories)
- **Story 1 (Hội đồng 7 trường phái):** Khi người dùng triệu tập Hội đồng, kết quả
  luôn có đúng 7 pitch duy nhất: `LEGALISM`, `TAOISM`, `CONFUCIAN`, `XUNZI`,
  `SUNZI`, `ICHING`, `TIMING`.
- **Story 2 (Dịch học - Sáu trạng thái):** Lens Dịch học đọc tình huống như một
  giả thuyết chuyển trạng thái, nêu dấu hiệu ủng hộ/phản bác và điều kiện đổi pha.
- **Story 3 (Thời thế - Ba giai đoạn thời vận):** Khi người dùng cần xác định "điểm rơi vàng" để ra đòn can thiệp (timing & pacing), thấu kính thời thế phân tích trạng thái `so_thoi`, `duong_thoi`, hoặc `mat_thoi` để định hướng tiến thoái.
- **Story 4 (Phân tích đầy đủ):** Giao diện hiển thị trọn vẹn từng pitch và không
  cắt mất hành động, dữ liệu cần kiểm chứng, cảnh báo hoặc ghi chú độ tin cậy.
- **Story 5 (Bảo toàn Governance):** Quyền runtime của hai lens được ghi nhận tách
  biệt với trạng thái nội dung; yêu cầu này không tự Frozen tài liệu nguồn.

---

## 3. Ranh giới Tách biệt Tầng (ADR-0002)
- **Tầng Content:** Sách nguồn tại `docs/knowledge/23_DICH_HOC_VA_THOI_THE.md` và file dữ liệu engine tại `backend/app/engine/philosophies/iching_engine.json`, `timing_engine.json`.
- **Tầng Engine:** `backend/app/engine/philosophies/router.py` và `nhan_thuat/council/council_engine.py`.
- **Quy chuẩn:** Router chỉ đọc dữ liệu từ engine json thông qua giao diện `PhilosophyRouter`, tuyệt đối không hardcode text tri thức vào Python engine.

---

## 4. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)
- [x] AC-1: Hội đồng trả đúng 7 agent ID, không thiếu và không trùng.
- [x] AC-2: Mỗi pitch có ít nhất 4 lập luận, 3 hành động, 2 mục dữ liệu cần kiểm
  chứng, một cảnh báo rủi ro và một ghi chú độ tin cậy.
- [x] AC-3: Dịch học và Thời thế sử dụng content JSON; không hardcode lời khuyên
  của hai lens trong controller/API.
- [x] AC-4: Nhánh LLM thiếu/sai cấu trúc phải fail sang fallback 7 lens đầy đủ.
- [x] AC-5: UI hiển thị đủ nội dung của cả 7 pitch.
- [x] AC-6: Oracle casting tiếp tục fail-closed.
- [x] AC-7: `scripts/validate_all.py`, Ruff và toàn bộ `pytest` đạt.
