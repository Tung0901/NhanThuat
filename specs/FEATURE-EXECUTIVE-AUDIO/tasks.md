# TASKS-EXECUTIVE-AUDIO: Tính năng Tham Mưu Thao Lược Bằng Âm Thanh — Tasks

**ID:** TASKS-EXECUTIVE-AUDIO  
**Spec & Plan:** SPEC-EXECUTIVE-AUDIO / PLAN-EXECUTIVE-AUDIO  
**Trạng thái:** ready_for_review  

---

## Danh sách Công việc Tuần tự (Execution Checklist)

### Giai đoạn 1: Chuẩn bị & Thuật toán Chuẩn hóa Văn bản Nói (Normalizer)
- [x] **TASK-AUDIO-01**: Xây dựng module `src/nhan_thuat/audio/speech_normalizer.py` làm sạch markdown, bẻ nhỏ câu (sentence chunking), và chuẩn hóa từ ngữ chuyên môn thành văn nói tự nhiên.
- [x] **TASK-AUDIO-02**: Viết unit test suite `tests/test_audio_speech_normalizer.py` bao phủ các trường hợp làm sạch bảng, ký tự đặc biệt, và ngắt nhịp câu.
  - *Kết quả:* 5/5 passed.

### Giai đoạn 2: Trình phát Âm thanh & Web Speech Controller (Frontend)
- [x] **TASK-AUDIO-03**: Xây dựng lớp điều khiển `ExecutiveAudioController` trong `frontend/js/executive_audio.js` quản lý hàng đợi phát `window.speechSynthesis`, tự động nhận diện voice tiếng Việt tốt nhất trên hệ điều hành, xử lý pause/resume/seek/speed.
- [x] **TASK-AUDIO-04**: Thiết kế giao diện **Executive Sticky Player** (`frontend/css/executive_audio.css`):
  - Nút Play/Pause/Stop, thanh thời gian / thanh tiến trình.
  - Bộ nút điều chỉnh tốc độ đọc (0.85x, 1.0x, 1.25x, 1.5x).
  - Sóng âm visualizer phản hồi theo trạng thái đọc.
- [x] **TASK-AUDIO-05**: Gắn nút hành động `[ 🎧 Nghe Toàn Bộ ]`, `[ 💬 Nghe Lời Thoại ]`, `[ ⚡ Nghe Tóm Tắt 1 Phút ]` tại các thẻ kết quả tham mưu chiến lược, và `[ 🎧 Nghe Hội Đồng Tranh Biện ]` tại khối Hội đồng.

### Giai đoạn 3: Tích hợp Backend Normalization API
- [x] **TASK-AUDIO-06**: Xây dựng endpoint `POST /api/v1/audio/extract-modes` trong `backend/app/main.py` phục vụ chuẩn hóa kịch bản đa chế độ.

### Giai đoạn 4: Kiểm chứng Toàn diện & Trình duyệt Nghiệm thu
- [x] **TASK-AUDIO-07**: Chạy toàn bộ bộ kiểm tra tự động:
  - `pytest tests/test_audio_speech_normalizer.py -v`: 5 passed.
  - `python scripts/validate_all.py`: Exit code 0.
  - `ruff check src/nhan_thuat/audio/`: Exit code 0.
- [x] **TASK-AUDIO-08**: Bàn giao tính năng và tài liệu hướng dẫn cho Product Owner.

### Giai đoạn 5: Đồng bộ Hội đồng 7 Lăng kính
- [x] **TASK-AUDIO-09**: Mở rộng bản đọc Hội đồng cho đủ nội dung 7 lăng kính,
  phản biện chéo và phương án A/B/C.
- [x] **TASK-AUDIO-10**: Bổ sung bộ chọn voice thực tế và bỏ ký hiệu trang trí
  khỏi điều khiển trình phát.
- [x] **TASK-AUDIO-11**: Chạy toàn suite, validator và kiểm chứng cú pháp frontend.
  - `node --check frontend/js/executive_audio.js`: đạt.
  - `uv run --extra dev pytest`: đạt 100%.
  - `uv run --extra dev ruff check src scripts tests`: đạt.
  - `uv run python scripts/validate_all.py`: đạt.
  - Kiểm chứng lại ngày 2026-10-17: 16 test tập trung LLM/audio đạt; validator đạt;
    lint các tệp thuộc phạm vi audio/LLM đạt.
  - QA trực quan đạt trên desktop 1422x804 và viewport hẹp 504x748; trình phát
    nhận 22 giọng hệ thống và hiển thị bộ chọn giọng.
  - Full suite hiện còn 2 lỗi ngoài phạm vi audio do test kho tri thức vẫn kỳ
    vọng version `0.1.0` và evidence `provisional` trong khi dữ liệu đang được
    nâng lên `1.0.0`; bài latency RAG đã đạt khi đo lại độc lập.
