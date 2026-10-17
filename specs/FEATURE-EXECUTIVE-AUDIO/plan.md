# PLAN-EXECUTIVE-AUDIO: Tính năng Tham Mưu Thao Lược Bằng Âm Thanh — Technical Plan

**ID:** PLAN-EXECUTIVE-AUDIO  
**Spec Tham Chiếu:** SPEC-EXECUTIVE-AUDIO  
**Người lập:** Main Agent  
**Trạng thái:** ready_for_review  

---

## 1. Thiết kế Kiến trúc (Architectural Blueprint)

Chúng ta áp dụng kiến trúc **Browser-Native Audio** nhằm tối ưu chi phí, độ trễ
và quyền riêng tư:

```
[ Kết quả Tham mưu / Hội đồng ]
               │
               ▼
   [ Text-to-Speech Normalizer ]  <─── Làm sạch Markdown, định dạng số, ngắt nghỉ câu
               │
               ▼
【 CLIENT-SIDE ENGINE 】
- Web Speech API (`speechSynthesis`)
- Ưu tiên voice tiếng Việt hiện có trên thiết bị
- Không gửi nội dung tham mưu tới dịch vụ TTS ngoài
- Chế độ offline phụ thuộc voice cục bộ của hệ điều hành
               │
               ▼
   [ Executive Audio Player UI ]
   - Thanh điều khiển nổi (Floating bar)
   - Visualizer sóng âm thanh
- Điều khiển tốc độ, chọn giọng đọc và chuyển đoạn
```

---

## 2. Danh sách Tệp tin Tác động

| Tệp tin | Hành động | Vai trò |
| :--- | :--- | :--- |
| `src/nhan_thuat/audio/speech_normalizer.py` | Thêm mới | Bộ lọc văn bản chuẩn hóa văn phong nói cho tiếng Việt |
| `backend/app/main.py` | Bổ sung | Endpoint `/api/v1/audio/extract-modes` chuẩn hóa kịch bản |
| `frontend/js/executive_audio.js` | Bổ sung | Controller Web Speech và bản đọc Hội đồng 7 lăng kính |
| `frontend/css/executive_audio.css` | Bổ sung | Sticky player responsive |
| `frontend/app.html` | Bổ sung | Audio Controller JS, Sticky Player UI, nút kích hoạt tại cards |
| `tests/test_audio_speech_normalizer.py` | Thêm mới | Unit tests cho logic chuẩn hóa văn bản đọc |

---

## 3. Chi tiết Giải pháp Kỹ thuật

### 3.1. Bộ Chuẩn hóa Văn bản Đọc (Speech Normalizer)
- Web Speech API thường gặp lỗi đơ (freeze) trên Chrome/Safari nếu gửi chuỗi văn bản dài quá 200 từ.
- Giải pháp: Cắt văn bản thành các `utterance chunks` dựa theo dấu chấm câu (`.`, `!`, `?`, `;\n`).
- Làm sạch các ký tự đặc biệt của Markdown:
  - Bỏ `**`, `*`, `###`, `---`, `>`.
  - Thay thế danh sách gạch đầu dòng `- ` thành khoảng ngắt giọng tự nhiên.
  - Xử lý các từ viết tắt chuyên môn ("KPI", "P > 0.8", "Plan B", "Verbatim") sang dạng phát âm thuần Việt rõ nghĩa.

### 3.2. Giao diện Trình phát Âm thanh (Executive Sticky Player)
- Thiết kế theo phong cách Dark Luxury Glassmorphism đồng bộ với Studio:
  - Nền đen mờ viền ánh kim (`#dfc47f`).
  - Nút Play/Pause cỡ lớn, phím tua nhanh 10 giây.
  - Bộ chọn tốc độ: `[ 0.85x | 1.0x | 1.25x | 1.5x ]`.
  - Danh sách voice lấy trực tiếp từ trình duyệt, ưu tiên tiếng Việt.
  - Hiệu ứng sóng âm thanh (Waveform bar animation) phát sáng nhịp nhàng khi giọng nói đang vang lên.

---

## 4. Kế hoạch Kiểm chứng & Đo lường (Verification Strategy)
1. Viết test suite cho `SpeechNormalizer` kiểm tra việc làm sạch markdown và phân đoạn câu.
2. Kiểm tra hợp đồng frontend cho bản đọc đủ 7 lăng kính và bộ chọn voice.
3. Kiểm tra thủ công trên Chrome/Edge; Safari/iOS cần thiết bị thật trước khi
   tuyên bố tương thích hoàn toàn.
4. Đảm bảo toàn bộ test hiện hành và `scripts/validate_all.py` tiếp tục đạt.
