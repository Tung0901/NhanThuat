# SPEC-UNCONSTRAINED-AI-SYNTHESIS: Khai Phóng Độ Sâu & Mở Khóa Giới Hạn Sinh Chữ Của AI (Unconstrained AI Synthesis)

**ID:** SPEC-UNCONSTRAINED-AI-SYNTHESIS  
**Epic Liên Quan:** NT-EPIC-05 (Knowledge Engine AI) & NT-EPIC-06 (Usable Product)  
**Tác giả:** Main Agent  
**Người duyệt:** Product Owner  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-11-09  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)

### 1.1. Vấn đề thực tế
- Người dùng khi tương tác với hệ thống Nhân Thuật (ở các module: Cố vấn Chiến lược, Đấu trí Sparring, Hội đồng Cố vấn, Sa bàn War Room) mong muốn nhận được các phân tích sâu sắc, toàn diện, lập luận đa tầng nấc và kịch bản lời thoại thực chiến trau chuốt từng câu chữ.
- Tuy nhiên, trong mã nguồn hiện tại tồn tại 4 điểm nghẽn khiến nội dung sinh ra bị giới hạn hoặc cắt cụt (truncated):
  1. **Thiếu tham số Token trần (`max_tokens`):** Adapter `synthesizer.py` và `war_room.py` không cấu hình `max_tokens` khi gọi API (OpenAI-compatible / Gemini / DeepSeek), khiến model bị chặn bởi trần mặc định thấp của nhà cung cấp.
  2. **Ràng buộc cứng trong Prompts:** Prompts trong `sparring_engine.py` và `synthesizer.py` có các mệnh lệnh hạn chế cơ học ("Tối đa 4 câu", "1 câu", "cô đọng nhất"), làm triệt tiêu khả năng biện giải sâu.
  3. **Giới hạn Timeout HTTP đồng bộ:** Khi sinh văn bản lớn (1.500 - 4.000 từ), thời gian xử lý kéo dài (15s - 45s) dễ chạm trần timeout đồng bộ 25s - 60s.
  4. **Thiếu cơ chế Streaming SSE:** Người dùng phải chờ đợi toàn bộ payload sinh xong mới được hiển thị, gây cảm giác chậm trễ nếu văn bản quá dài.

### 1.2. Mục tiêu đạt được
- **Không giới hạn số từ (Uncapped Output):** Cho phép AI khai triển toàn diện mọi góc nhìn, lập luận, bằng chứng và kịch bản thực thi mà không bị áp trần số câu hay số từ nhân tạo.
- **Cấu hình Token linh hoạt:** Thiết lập `AI_MAX_OUTPUT_TOKENS` (mặc định mở rộng tối đa theo context window của model, ví dụ 8.192 hoặc 16.384 tokens) và `AI_REQUEST_TIMEOUT=120`.
- **Tái thiết kế Prompt chuyên sâu:** Loại bỏ mọi chỉ dẫn co cụm độ dài; khuyến khích AI phân tích đa tầng nấc, mổ xẻ tâm lý vi mô và đưa ra các kịch bản đối thoại chi tiết.
- **Hỗ trợ Streaming SSE (Server-Sent Events):** Cung cấp khả năng truyền tải dữ liệu theo dòng (chunk-by-chunk) cho module tương tác, giúp chữ tuôn ra thời gian thực, đọc ngay lập tức và triệt tiêu nguy cơ timeout.

### 1.3. Ngoài phạm vi (Out of Scope)
- Không chỉnh sửa 379 tri thức đã Frozen trong `knowledge/`.
- Không thay đổi các quy tắc định tuyến triết học (`PhilosophyRouter`).

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories & Requirements)

### User Story 1: Bản Tham Mưu Chiến Lược Chuyên Sâu Toàn Diện
- **Mô tả:** Lãnh đạo nhập một tình huống phức tạp (mâu thuẫn cổ đông, khủng hoảng vận hành), mong muốn nhận bản tham mưu nghị luận đầy đủ 5 phần không bị cắt cụt.
- **Kịch bản kiểm thử:**
  - *Given:* Người dùng gửi câu hỏi phân tích tại `/api/v1/analyze`.
  - *When:* AI xử lý với provider được cấu hình.
  - *Then:* Kết quả trả về đầy đủ luận đề, phân tích ngầm ẩn, bảng bẫy nhận thức, và kịch bản 3 giai đoạn chi tiết mà không có dấu hiệu bị ngắt câu giữa chừng.

### User Story 2: Đấu Trí Gai Góc & Mổ Xẻ Điểm Mù Đa Tầng
- **Mô tả:** Người dùng đưa ra lập luận tại phòng Đấu Trí (Sparring), mong muốn đối thủ phản biện sâu sắc, không bị gò bó trong "4 câu ngắn ngủi".
- **Kịch bản kiểm thử:**
  - *Given:* Người dùng gửi tin nhắn tại `/api/v1/sparring/messages`.
  - *When:* `SparringEngine` kích hoạt tạo phản hồi.
  - *Then:* Đối thủ phản biện đanh thép, phân tích chi tiết sơ hở tâm lý, chỉ ra đòn bẩy triết học đối trọng và cung cấp nhiều phương án lời thoại lật ngược thế cờ.

### User Story 3: Truyền Tải Dữ Liệu Thời Gian Thực (Streaming SSE)
- **Mô tả:** Khi AI sinh văn bản dài hàng nghìn từ, giao diện hiển thị chữ tuôn ra ngay lập tức theo thời gian thực thay vì chờ đợi toàn bộ phản hồi.
- **Kịch bản kiểm thử:**
  - *Given:* Client gọi endpoint streaming `/api/v1/analyze/stream` hoặc `/api/v1/sparring/stream`.
  - *When:* Model sinh từng token.
  - *Then:* Server gửi từng chunk dữ liệu qua giao thức SSE (`data: {"chunk": "..."}\n\n`), client cập nhật giao diện mượt mà và kết thúc bằng `data: [DONE]\n\n`.

---

## 3. Ranh giới Tách biệt Tầng (Architecture Boundary Check - ADR-0002)

- [x] **Knowledge Content:** Giữ nguyên vẹn 100%. Không sửa đổi bất kỳ file tri thức YAML hay Book Markdown nào.
- [x] **Knowledge Engine & Runtime:** Nâng cấp `synthesizer.py`, `sparring_engine.py`, `war_room.py`, `nhan_thuat_api.py`, `backend/app/main.py`.
- [x] **Presentation Layer:** Cập nhật `frontend/app.html` & `frontend/scroll_demo.html` để hỗ trợ hiển thị văn bản dài và xử lý streaming nếu được kích hoạt.

---

## 4. Đánh giá Tác động Quản trị (Governance & Impact Analysis)

- **Ảnh hưởng đến Frozen Items?** Không.
- **Ảnh hưởng đến Schema YAML/JSON?** Không.
- **Backward Compatibility:** Giữ nguyên 100% hợp đồng API JSON hiện tại (`/api/v1/analyze`, `/api/v1/sparring/messages`), endpoint stream là tiện ích bổ sung không phá vỡ logic cũ.

---

## 5. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)

- [ ] **AC-1:** Payload gửi đến LLM có tham số `max_tokens` (hoặc `max_completion_tokens`) mở rộng (mặc định cấu hình linh hoạt theo `AI_MAX_OUTPUT_TOKENS`), không bị trần thấp mặc định của provider.
- [ ] **AC-2:** Toàn bộ prompts trong `sparring_engine.py`, `synthesizer.py`, `nhan_thuat_api.py` được dỡ bỏ các giới hạn câu/từ cứng ("tối đa 4 câu", "1 câu", "cô đọng nhất").
- [ ] **AC-3:** Endpoint `/api/v1/analyze/stream` và/hoặc `/api/v1/sparring/stream` hoạt động đúng chuẩn SSE, truyền stream mượt mà và an toàn.
- [ ] **AC-4:** Timeout được nâng cấp có thể tùy biến qua biến môi trường `AI_REQUEST_TIMEOUT` (mặc định 120s).
- [ ] **AC-5:** Test suite chuyên biệt `tests/test_unconstrained_synthesis.py` pass 100%.
- [ ] **AC-6:** `python scripts/validate_all.py` đạt exit code 0.
- [ ] **AC-7:** `ruff check src backend tests scripts` không có lỗi linting.

