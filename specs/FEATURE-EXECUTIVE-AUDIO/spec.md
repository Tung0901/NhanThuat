# SPEC-EXECUTIVE-AUDIO: Tính năng Tham Mưu Thao Lược Bằng Âm Thanh (Executive Audio Briefing)

**ID:** SPEC-EXECUTIVE-AUDIO  
**Epic Liên Quan:** NT-EPIC-06 (Usable Product) & NT-EPIC-04 (Application Layer)  
**Tác giả:** Main Agent  
**Người duyệt:** Product Owner  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-10-15  

---

## 1. Tóm tắt & Bối cảnh (Summary & Context)

### 1.1. Vấn đề thực tế
- Các bản tham mưu chiến lược của Nhân Thuật (Advisory Analysis, Council Deliberation, Diagnostic Reports) chứa hàm lượng tri thức rất cao: phân tích thế trận đa thấu kính, kịch bản lời thoại mẫu từng câu chữ (Verbatim Script), các bước can thiệp và chỉ đạo điều hành.
- Tuy nhiên, độ dài văn bản thường từ 1.000 đến 3.000 từ. Nhiều lãnh đạo, nhà quản lý bận rộn khi di chuyển, lái xe, hoặc người dùng có xu hướng "lười đọc" văn bản dài trên màn hình điện thoại/máy tính sẽ dễ bỏ lỡ các chỉ đạo then chốt.

### 1.2. Mục tiêu đạt được
- Cung cấp tính năng **Executive Audio Briefing**: Một chạm chuyển toàn bộ bản tham mưu chiến lược thành giọng đọc âm thanh đĩnh đạc, rõ ràng, giàu tính thuyết phục.
- Hỗ trợ trải nghiệm nghe thông minh: Người dùng có thể nghe toàn văn, hoặc chọn chỉ nghe phần cốt lõi (như "Kịch bản Lời thoại Thực chiến" hoặc "Hội đồng Tranh biện").
- Hoạt động không cần dịch vụ TTS phía máy chủ; khả năng offline phụ thuộc voice
  cục bộ mà hệ điều hành và trình duyệt cung cấp.

### 1.3. Ngoài phạm vi (Out of Scope)
- Đợt 1 không làm voice cloning (nhân bản giọng nói cá nhân).
- Không can thiệp vào logic tính toán tri thức cốt lõi (Core Reasoning Engine).

---

## 2. Kịch bản Người dùng & Yêu cầu Chức năng (User Stories)

### User Story 1: Nghe Tham Mưu Nhanh Trong Xe / Khi Di Chuyển
- **Mô tả:** Lãnh đạo vừa nhập tình huống mâu thuẫn nhân sự hoặc đàm phán hợp đồng, bấm nút "Phát Audio Tham Mưu", hệ thống phát âm thanh tóm lược thế trận và hướng dẫn xử lý qua loa xe hơi/tai bluetooth.
- **Kịch bản kiểm thử:**
  - *Given:* Người dùng vừa nhận kết quả phân tích tham mưu tại tab Cố Vấn hoặc Sa Bàn.
  - *When:* Bấm nút `Nghe tham mưu`.
  - *Then:* Hệ thống khởi tạo thanh phát âm thanh, đọc mạch lạc phần "Phân tích Thế trận" và "Kịch bản 3 bước", thanh player hiển thị trạng thái đang đọc kèm nút Tạm dừng/Tiếp tục.

### User Story 2: Lựa Chọn Nội Dung Nghe Chuyên Biệt
- **Mô tả:** Người dùng chỉ muốn nghe nhanh câu từ đối đáp để chuẩn bị vào phòng họp.
- **Kịch bản kiểm thử:**
  - *When:* Người dùng chọn chế độ `Chỉ nghe Lời thoại Mẫu (Verbatim Script)`.
  - *Then:* Audio chỉ phát phần trích dẫn câu từ thực chiến, lược bỏ các phần lý thuyết nền tảng.

### User Story 3: Tùy Biến Trải Nghiệm Lắng Nghe
- **Mô tả:** Người dùng có thể chỉnh tốc độ đọc và chọn trong danh sách giọng
  mà trình duyệt/hệ điều hành thực sự cung cấp; hệ thống ưu tiên tiếng Việt.

### User Story 4: Nghe Hội đồng 7 Lăng kính
- **Mô tả:** Bản đọc Hội đồng bao gồm đủ 7 bản tham mưu, phản biện chéo,
  phương án A/B/C, điều kiện thận trọng và chỉ thị thực thi.

---

## 3. Ranh giới Tách biệt Tầng (ADR-0002 Boundary Check)

- **Tầng Content:** Giữ nguyên vẹn 100%. Các file tri thức YAML và Book Markdown không bị sửa đổi.
- **Tầng Engine & Backend:** Module `src/nhan_thuat/audio/speech_normalizer.py`
  và endpoint `/api/v1/audio/extract-modes` chỉ chuẩn hóa văn bản; không giả lập
  một dịch vụ Neural TTS chưa tồn tại.
- **Tầng Presentation (Web App):** Web Speech Controller và Sticky Audio Player
  dùng voice có sẵn trên thiết bị, không gửi nội dung sang dịch vụ TTS ngoài.

---

## 4. Tiêu chuẩn Nghiệm thu (Acceptance Criteria)

- [x] **AC-1:** Giao diện có nút nghe tại kết quả Tham mưu và Hội đồng.
- [x] **AC-2:** Sticky Player hỗ trợ phát, tạm dừng, tiếp tục, dừng, chuyển
  đoạn và hiển thị tiến trình theo đoạn.
- [x] **AC-3:** Hỗ trợ tốc độ 0.85x, 1.0x, 1.25x, 1.5x và chọn voice thực có.
- [x] **AC-4:** Bộ lọc loại Markdown, bảng biểu và ký tự trang trí trước khi đọc.
- [x] **AC-5:** Không phụ thuộc server TTS; tự ưu tiên voice tiếng Việt và báo
  rõ khi trình duyệt không hỗ trợ.
- [x] **AC-6:** Bản đọc Hội đồng bao phủ đủ 7 lăng kính, phản biện và Plan A/B/C.
- [x] **AC-7:** Toàn suite, Ruff và `scripts/validate_all.py` đạt sau thay đổi cuối.
