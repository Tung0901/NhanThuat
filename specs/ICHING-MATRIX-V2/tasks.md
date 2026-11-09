# TASKS-ICHING-MATRIX-V2: Phân Rã Công Việc Thực Thi

**ID:** TASKS-ICHING-MATRIX-V2  
**Spec Tham Chiếu:** [SPEC-ICHING-MATRIX-V2](spec.md)  
**Plan Tham Chiếu:** [PLAN-ICHING-MATRIX-V2](plan.md)  
**Trạng thái:** ready_for_review  

---

## Danh Sách Tasks Tuần Tự

### Pha 1: Dữ Liệu & Backend Service
- [x] **Task 1.1**: Xây dựng thuật toán tính toán và làm giàu toàn bộ 64 quẻ trong `backend/app/engine/philosophies/iching_64_hexagrams.json` (bổ sung upper/lower trigram, binary_pattern, nuclear_hex_number, opposite_hex_number, inverted_hex_number, twelve_sovereign, six_lines, strategic_stance, diagnostic_tags, related_knowledge_units).
- [x] **Task 1.2**: Mở rộng `backend/app/engine/philosophies/iching_service.py` hỗ trợ `get_matrix_8x8()`, `get_sovereign_hexagrams()`, `simulate_transition()`, `diagnose()`.
- [x] **Task 1.3**: Bổ sung routing các endpoints IChing mở rộng trong `backend/app/main.py`.
- [x] **Task 1.4**: Viết unit test mới `tests/test_iching_matrix_v2.py` và chạy kiểm tra pass 100%.

### Pha 2: Giao Diện Người Dùng Đa Chế Độ Xem & SVG Lục Hào
- [x] **Task 2.1**: Cập nhật CSS Glassmorphism trong `frontend/app.html` cho Bàn cờ 8x8, Đồ thị 12 Tức Quái, Thẻ Lục Hào SVG và Inspector Modal.
- [x] **Task 2.2**: Thiết kế HTML markup cho khu vực `#iching-matrix-section` với View Mode Switcher và các container tương ứng.
- [x] **Task 2.3**: Xây dựng hàm render Bàn cờ Ma trận 8x8 trực quan, cho phép hover chiếu sáng hàng/cột và click mở quẻ.
- [x] **Task 2.4**: Xây dựng hàm render Vòng Chu Kỳ 12 Tức Quái theo hình sin năng lượng Âm/Dương.
- [x] **Task 2.5**: Nâng cấp hàm render Cards Grid với đồ họa Lục Hào SVG và tags chiến lược.

### Pha 3: Động Cơ Chuyển Pha & Inspector Modal Chuyên Sâu
- [x] **Task 3.1**: Xây dựng Trình Chẩn Đoán Tình Thế Doanh Nghiệp (bộ lọc triệu chứng thực tế và tư thế chiến lược Tiến/Thoái/Thủ/Biến).
- [x] **Task 3.2**: Xây dựng Modal Inspector 4 tab chuyên sâu (Thời Thế & Cảnh Báo, Đồ Giải Lục Hào, Chuyển Pha & Hệ Quẻ, Tri Thức & Case Study) kèm tính năng Click Hào $\rightarrow$ Sinh Quẻ Biến.
- [x] **Task 3.3**: Đảm bảo toàn bộ element IDs và functions cũ (`loadIChingHexagrams`, `selectIChingPalace`, `filterIChingHexagrams`, `showIChingHexagramDetail`) tiếp tục hoạt động tương thích tuyệt đối với `tests/test_frontend_dom_behavior.py`.

### Pha 4: Kiểm Thử Toàn Diện & Trình Duyệt Nghiệm Thu
- [x] **Task 4.1**: Chạy `pytest tests/test_iching_matrix_v2.py` -> PASS 100%.
- [x] **Task 4.2**: Chạy `pytest tests/test_commercial_and_iching_api.py` và `pytest tests/test_frontend_dom_behavior.py` -> PASS 100%.
- [x] **Task 4.3**: Chạy regression tests -> PASS.
- [x] **Task 4.4**: Chạy `python scripts/validate_all.py` (Exit code 0) và `ruff check` (All checks passed).
- [x] **Task 4.5**: Cập nhật trạng thái `ready_for_review` và lập hồ sơ bàn giao Product Owner.
