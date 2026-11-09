# PLAN-ICHING-MATRIX-V2: Kế Hoạch Thiết Kế Kỹ Thuật Ma Trận Quẻ Dịch 2.0

**ID:** PLAN-ICHING-MATRIX-V2  
**Spec Tham Chiếu:** [SPEC-ICHING-MATRIX-V2](spec.md)  
**Tác giả:** Main Agent  
**Trạng thái:** ready_for_review  
**Ngày tạo:** 2026-11-09  

---

## 1. Kiến Trúc Kỹ Thuật & Luồng Dữ Liệu

```
[ Frontend: app.html ]
   ├── View 1: 8x8 Interactive Matrix Board (Ngoại Quái × Nội Quái)
   ├── View 2: 12 Sovereign Hexagrams Sine-Wave Timeline (Thập Nhị Tức Quái)
   ├── View 3: Strategy Hexagram Cards Grid (SVG Lục Hào + Quick Badges)
   ├── View 4: Executive Phase Diagnostics (Chọn Triệu Chứng → Ra Quẻ & Tư Thế)
   └── Inspector Modal: 4 Tab Deep-Dive (Thời Thế / Lục Hào / Chuyển Pha / Tri Thức Liên Đới)
         │
         ▼ HTTP REST API
[ Backend: main.py Gateway ]
   ├── GET /api/v1/iching/hexagrams (danh sách 64 quẻ, lọc theo palace, query, diagnostic tags)
   ├── GET /api/v1/iching/hexagrams/{id} (chi tiết 1 quẻ + quẻ hỗ + quẻ thác + quẻ tung)
   ├── GET /api/v1/iching/matrix-8x8 (ma trận 8 hàng x 8 cột)
   ├── GET /api/v1/iching/sovereign (12 quẻ tức kèm thứ tự chu kỳ & tỷ lệ âm dương)
   └── POST /api/v1/iching/simulate-transition (quẻ gốc + hào biến → quẻ biến)
         │
         ▼ Engine Service
[ backend/app/engine/philosophies/iching_service.py ]
         │
         ▼ Data Store
[ backend/app/engine/philosophies/iching_64_hexagrams.json ]
```

---

## 2. Danh Sách Files Tác Động

1. **`backend/app/engine/philosophies/iching_64_hexagrams.json`**:
   - Cập nhật toàn bộ 64 quẻ bổ sung các trường:
     - `upper_trigram` (`name`, `symbol`, `nature`, `element`)
     - `lower_trigram` (`name`, `symbol`, `nature`, `element`)
     - `binary_pattern` (chuỗi 6 ký tự `0` và `1`, từ hào 1 đến hào 6)
     - `nuclear_hex_number` (số quẻ Hỗ, tạo từ hào 2-3-4 làm nội quái, hào 3-4-5 làm ngoại quái)
     - `opposite_hex_number` (số quẻ Thác, đảo toàn bộ bit 0 $\leftrightarrow$ 1)
     - `inverted_hex_number` (số quẻ Tung, đảo ngược thứ tự hào 1..6)
     - `twelve_sovereign` (`is_sovereign`, `phase_order`, `phase_name`, `energy_ratio`)
     - `six_lines` (danh sách 6 hào với `line`, `name`, `type`, `org_role`, `action`)
     - `strategic_stance` ("Tiến" | "Thoái" | "Thủ" | "Biến")
     - `diagnostic_tags` (mảng các nhãn chẩn đoán)
     - `related_knowledge_units` (mảng ID tri thức như `NT-LAW-0001`, `NT-PRINCIPLE-0004`...)
2. **`backend/app/engine/philosophies/iching_service.py`**:
   - Thêm phương thức `get_matrix_8x8()`: trả về cấu trúc 8x8 bảng giao điểm.
   - Thêm phương thức `get_sovereign_hexagrams()`: trả về 12 quẻ tức sắp xếp theo chu kỳ.
   - Thêm phương thức `simulate_transition(hex_number, moving_lines)`: tính toán quẻ biến theo luật nhị phân.
   - Thêm phương thức `diagnose(tags, stance)`: lọc quẻ theo triệu chứng chẩn đoán.
   - Mở rộng `get_hexagram()` đính kèm thông tin đầy đủ về quẻ Hỗ, Thác, Tung.
3. **`backend/app/main.py`**:
   - Bổ sung routing cho các endpoint mới:
     - `/api/v1/iching/matrix-8x8`
     - `/api/v1/iching/sovereign`
     - `/api/v1/iching/simulate-transition`
4. **`frontend/app.html`**:
   - Tái cấu trúc khu vực `#iching-matrix-section`:
     - Thanh chuyển chế độ View (`matrix-8x8`, `sovereign-12`, `cards-grid`, `diagnostics`).
     - Giao diện Bàn cờ 8x8 với header 8 Ngoại Quái và 8 Nội Quái.
     - Giao diện Vòng 12 Tức Quái với đường cong hình sin tỷ lệ Âm Dương.
     - Giao diện Bộ Chẩn Đoán với các pills triệu chứng chọn lọc.
     - Nâng cấp Thẻ Lục Hào SVG sắc nét, xóa bỏ giới hạn `max-height: 380px`.
     - Modal Inspector 4 tab chuẩn mực `#iching-modal-backdrop` (vẫn giữ `#iching-detail-drawer` tương thích kiểm thử).
     - Động cơ JavaScript xử lý biến hào và chuyển pha trực quan.
5. **`tests/test_iching_matrix_v2.py`**:
   - Test suites mới xác thực các tính năng mở rộng của `iching_service`, API endpoints và mô phỏng chuyển pha.

---

## 3. Kế Hoạch Kiểm Thử & Kiểm Chứng
- Chạy `pytest tests/test_iching_matrix_v2.py`
- Chạy `pytest tests/test_commercial_and_iching_api.py`
- Chạy `pytest tests/test_frontend_dom_behavior.py`
- Chạy toàn bộ test suite `pytest`
- Chạy `python scripts/validate_all.py`
- Chạy `ruff check backend/ tests/`
