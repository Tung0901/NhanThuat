# BẢN THIẾT KẾ KIẾN TRÚC: MODULE "SA BÀN TÌNH THẾ" (WAR ROOM SANDBOX)
*Hệ thống mô phỏng hành vi & diễn biến tình thế đa tác nhân cho Nhân Thuật (Kế thừa và tối ưu từ MiroFish - 666ghj/MiroFish)*

---

## 1. MỤC TIÊU & ĐỊNH VỊ
- **Mục tiêu:** Biến tri thức quản trị & nhân tâm của Nhân Thuật (379 Knowledge Units) thành một **Thao trường mô phỏng không rủi ro (Zero-Risk Stress-Testing Sandbox)**.
- **Cơ chế cốt lõi:** Thay vì tư vấn tĩnh, hệ thống khởi tạo một thế giới vi mô gồm các AI Agent có nhân cách, động cơ, nỗi sợ và ranh giới an toàn. Cho phép chạy mô phỏng phản ứng của các nhân vật qua nhiều vòng (rounds) trước một chính sách, biến cố hoặc quyết định chiến lược.
- **Điểm cải tiến so với MiroFish gốc:**
  - Không phụ thuộc vào hạ tầng Zep Cloud hay OASIS cồng kềnh.
  - Sử dụng trực tiếp LLM Engine của Nhân Thuật (hỗ trợ OpenAI, Gemini, DeepSeek).
  - Tích hợp sâu vào tri thức 5 phái (Nho, Pháp, Đạo, Tuân, Hùng biện) và các bẫy tâm lý có sẵn trong repository.

---

## 2. QUY TRÌNH MÔ PHỎNG (WORKFLOW 5 BƯỚC)

1. **Khởi tạo Sa Bàn (Scenario Seeding):**
   - Người dùng nhập tình huống (ví dụ: cắt giảm nhân sự, phát hiện gián điệp nội bộ, đàm phán mua bán sáp nhập...).
   - Hệ thống tự động phân tích các phe phái và vị thế quyền lực liên quan.

2. **Sinh nhân cách đa chiều (Persona Generation):**
   - Sinh từ 4 - 8 nhân vật trọng yếu.
   - Mỗi nhân vật có: Họ tên, Chức vụ/Vai trò, Lợi ích cốt lõi (Core Interest), Nỗi sợ ngầm (Hidden Fear), Xu hướng hành vi (Bảo thủ / Cấp tiến / Cơ hội / Trung thành).

3. **Vòng lặp mô phỏng đa tầng (Multi-Round Simulation Loop):**
   - **Vòng 1 (Thăm dò & Lan truyền):** Thông tin rò rỉ, các nhân vật phản ứng sơ bộ, xuất hiện tin đồn và các cuộc trò chuyện hành lang.
   - **Vòng 2 (Phân hóa & Liên minh):** Xuất hiện phe cánh, thỏa hiệp ngầm hoặc phản kháng thụ động.
   - **Vòng 3 (Đỉnh điểm & Xung đột):** Đụng độ quyền lợi trực tiếp hoặc bùng nổ khủng hoảng.

4. **Can thiệp của Người điều hành (God-mode Intervention):**
   - Giữa các vòng, người dùng có thể can thiệp bằng cách tung ra một mệnh lệnh, phát ngôn hoặc sự kiện mới để định hình lại hành vi của bầy đàn.

5. **Tổng kết tham mưu (Strategic War Room Report):**
   - Tổng hợp biến chuyển qua các vòng.
   - Chỉ ra: Mắt xích nguy hiểm nhất, Điểm gãy của tổ chức, Đề xuất kế sách xử lý tối ưu theo quy luật Nhân Thuật.

---

## 3. THIẾT KẾ KỸ THUẬT (SYSTEM ARCHITECTURE)

### Backend (`src/nhan_thuat/runtime/` & `backend/app/`)
- `src/nhan_thuat/runtime/war_room.py`:
  - `Persona`: Dataclass đại diện cho từng nhân vật mô phỏng.
  - `WarRoomEngine`: Quản lý trạng thái mô phỏng (Stateful engine lưu theo `session_id`).
  - `generate_personas(scenario, knowledge_context)`: Gọi LLM sinh nhân vật có chiều sâu.
  - `step_round(session_id, user_intervention)`: Chạy 1 vòng mô phỏng tương tác giữa các nhân vật.
  - `synthesize_report(session_id)`: Trích xuất báo cáo tổng kết tình thế.
- `backend/app/main.py`:
  - Bổ sung 5 REST Endpoints:
    - `POST /api/v1/war-room/init` (Nạp tình huống & sinh nhân vật)
    - `POST /api/v1/war-room/step` (Chạy vòng tiếp theo kèm lệnh can thiệp)
    - `POST /api/v1/war-room/report` (Xuất báo cáo tham mưu)
    - `GET /api/v1/war-room/state` (Lấy trạng thái hiện tại)
    - `GET /api/v1/war-room/presets` (Danh sách kịch bản mẫu)

### Frontend (`frontend/app.html`)
- Bổ sung Module thứ 6 vào thanh điều hướng: **♟️ Sa Bàn Tình Thế**.
- **Layout 3 khối trực quan:**
  1. *Cột trái:* Khởi tạo kịch bản & Danh sách thẻ nhân vật (thẻ căn cước tâm lý).
  2. *Cột giữa:* Dòng thời gian đối thoại & Hành vi của các nhân vật qua từng vòng (War Room Live Feed).
  3. *Cột phải:* Khung can thiệp ("Lệnh Thượng Đế") + Nút sang vòng kế tiếp + Khung Báo Cáo Tham Mưu Tổng Kết.
