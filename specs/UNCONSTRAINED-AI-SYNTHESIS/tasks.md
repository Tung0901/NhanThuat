# TASKS-UNCONSTRAINED-AI-SYNTHESIS: Khai Phóng Độ Sâu & Mở Khóa Giới Hạn Sinh Chữ Của AI — Task Breakdown

**ID:** TASKS-UNCONSTRAINED-AI-SYNTHESIS  
**Spec & Plan Tham Chiếu:** SPEC-UNCONSTRAINED-AI-SYNTHESIS / PLAN-UNCONSTRAINED-AI-SYNTHESIS  
**Trạng thái:** completed  

---

## Danh Sách Công Việc Tuần Tự (Ordered Implementation Tasks)

### Giai đoạn 1: Runtime Uncapping & Streaming Adapter (Synthesizer & War Room)
- [x] **TASK-01**: Cập nhật `src/nhan_thuat/runtime/synthesizer.py`:
  - Đọc `AI_MAX_OUTPUT_TOKENS` (mặc định 8192) và `AI_REQUEST_TIMEOUT` (mặc định 120s).
  - Truyền `max_tokens` vào `_call_provider` và xử lý an toàn.
  - Thêm phương thức `generate_stream(prompt: str) -> Iterator[str]`.
  - Cập nhật `_build_prompt` dỡ bỏ các ràng buộc co ngắn bài viết ("Tối đa 4 câu", "3-4 gạch đầu dòng cô đọng nhất").
- [x] **TASK-02**: Cập nhật `src/nhan_thuat/runtime/war_room.py`:
  - Nâng cấp `_call_llm_json` bổ sung `max_tokens` và cấu hình timeout.

### Giai đoạn 2: Prompt Uncapping & Sparring Expansion
- [x] **TASK-03**: Cập nhật `src/nhan_thuat/engine/sparring_engine.py`:
  - Gỡ bỏ "Tối đa 4 câu", "[1 câu]", chỉ dẫn AI đào sâu tâm lý vi mô và cung cấp các kịch bản đối thoại đối trọng toàn diện.
  - Bổ sung `process_turn_stream` hỗ trợ streaming đối kháng từng lượt.
- [x] **TASK-04**: Cập nhật `backend/app/engine/nhan_thuat_api.py`:
  - Gỡ bỏ các giới hạn ngắn gọn trong `process_nhan_thuat_analysis` (sparring prompt và diagnostic prompts).

### Giai đoạn 3: Gateway Streaming Endpoints & Frontend Polish
- [x] **TASK-05**: Bổ sung endpoint SSE trong `backend/app/main.py`:
  - `POST /api/v1/sparring/stream` trả về sự kiện chuẩn SSE với metadata, chunks và done signal.
- [x] **TASK-06**: Cập nhật `frontend/app.html`:
  - Tích hợp stream reader cho giao diện phòng Đấu trí (Sparring), hiển thị chữ tuôn ra thời gian thực.

### Giai đoạn 4: Viết Test Chuyên Biệt & Kiểm Chứng Hồi Quy (Verification)
- [x] **TASK-07**: Tạo test suite `tests/test_unconstrained_synthesis.py`:
  - Test `KnowledgeSynthesizer` truyền `max_tokens`.
  - Test `generate_stream` phát sinh chunks.
  - Test `SparringEngine` prompt không còn chứa cụm từ hạn chế độ dài.
  - Test `process_turn_stream` lưu trữ tin nhắn đúng quy chuẩn.
- [x] **TASK-08**: Chạy toàn bộ bộ kiểm tra hồi quy:
  - `pytest tests/test_unconstrained_synthesis.py --basetemp=tmp_pytest` (PASS 6/6)
  - `pytest tests/test_synthesizer.py tests/test_sparring_security.py --basetemp=tmp_pytest` (PASS 13/13)
  - `ruff check` (All checks passed)
  - `python scripts/validate_all.py` (Valid)
