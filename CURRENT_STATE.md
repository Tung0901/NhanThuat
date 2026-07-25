# Current Repository State - NhanThuat Knowledge Repository

**Last Updated:** 2026-07-23  
**Status:** **100% ACTIVATED AND INTEGRATED (FIVE PHILOSOPHY LENS SYSTEM)**

---

## 1. System Overview

NhanThuat is a formal knowledge repository and governance framework for human nature, organizational behavior, decision intelligence, leadership, and operational management.

With the completion of the **BusinessOS Five Philosophy Lens System Upgrade**, NhanThuat incorporates five foundational philosophical systems into executable documentation, structured JSON engines with standardized SemVer metadata, and an advanced multi-lens context router.

---

## 2. Five Philosophy Lens Infrastructure (`docs/knowledge/` & `backend/app/engine/philosophies/`)

### Single Source of Truth Documentation (`docs/knowledge/`)
1. **`01_THUAT_HUNG_BIEN.md` (Thuật Hùng Biện / Rhetoric Lens):**
   - 4 Tầng Tri Thức: Nguyên tắc logic, Mô thức đối đáp (PAS, Gậy ông đập lưng ông), Kỹ thuật xử lý từ chối (Rút củi đáy nồi, Phản chứng, Đảo ngược góc nhìn), Tiêu chí hiệu quả giao tranh ngôn ngữ.
2. **`02_TU_THU_KNOWLEDGE_PACK.md` (Nho Gia / Confucian Lens):**
   - Tri thức Nho gia: Tam Cương Lĩnh, Bát Điều Mục, Ngũ Thường, Đức Trị & Nhân Chính, Mô thức "Hòa nhi bất đồng", Bảng phân biệt Quân tử vs. Tiểu nhân.
3. **`03_HAN_PHI_TU_KNOWLEDGE_PACK.md` (Pháp Gia / Legalism Lens):**
   - Tri thức Hàn Phi Tử: Bộ ba Quản trị (Pháp - Thế - Thuật), Nguyên tắc Hình Danh Tham Đồng, Mô thức Nhị Bỉnh (Thưởng - Phạt), Nhận diện Bát Gian (8 nguy cơ thao túng/nịnh bợ), Tiêu chí kỷ luật & minh bạch.
4. **`04_TRANG_TU_KNOWLEDGE_PACK.md` (Đạo Gia / Taoism Lens):**
   - Tri thức Trang Tử: Tiêu Dao Du (Tư duy bứt phá), Tề Vật Luận (Góc nhìn đa chiều), Vô Vi (Thuận tự nhiên), Mô thức "Dụng Vô Dụng", Phương pháp Tâm Trai / Tọa Vọng, Rubric đánh giá tính Linh hoạt & Thích ứng.
5. **`05_TUAN_TU_KNOWLEDGE_PACK.md` (Tuân Tử / Xunzi Lens):**
   - Tri thức Tuân Tử: Thuyết Tính Ác & Uốn nắn (Vĩ), Khuyên Học (Học tập liên tục & Mentorship), Dùng Lễ Định Phần (Quy chuẩn vai trò & ranh giới), Mô hình Huấn luyện & Sửa đổi Hành vi Nhân sự, Rubric Đánh giá Kỷ luật.

---

### Executable JSON Engines & Standardized Metadata (`backend/app/engine/philosophies/`)
1. **`rhetoric_engine.json` (`LENS-RHETORIC` v1.1.0):** Ma trận bẻ luận điểm (Refutation Matrix) & Kịch bản xử lý từ chối.
2. **`confucian_engine.json` (`LENS-CONFUCIAN` v1.1.0):** Quy chuẩn Đạo đức Lãnh đạo, Bộ lọc "Quân tử vs. Tiểu nhân", Quy tắc "Hòa nhi bất đồng".
3. **`legalism_engine.json` (`LENS-LEGALISM` v1.1.0):** Quy trình Hình Danh Tham Đồng, Bảng quy chế Nhị Bỉnh (Thưởng/Phạt), Bộ lọc chống Bát Gian.
4. **`taoism_engine.json` (`LENS-TAOISM` v1.1.0):** Quy trình xử lý khủng hoảng Tâm Trai/Tọa Vọng, Đàm phán thấu cảm, Thuật Dụng Vô Dụng.
5. **`xunzi_engine.json` (`LENS-XUNZI` v1.1.0):** Quy trình Huấn luyện Nhân sự 4 bước, Sửa đổi hành vi, Khuyên Học, Dùng Lễ Định Phần.

All 5 engine files expose standardized Program 8 & 9 metadata blocks: `philosophy_id`, `philosophy_name`, `version`, `source_document`, `supported_domains`, `supported_personas`, `preferred_reasoning_modes`, `compatible_lenses`, `incompatible_lenses`, `confidence_modifier`, `governance_status`, and `last_reviewed`.

---

### BusinessOS Philosophy Lens Router (`backend/app/engine/philosophies/router.py`)
- `PhilosophyRouter` supports Multi-Lens Composition (Primary, Secondary, Tertiary):
  - **Customer Price Objection** $\rightarrow$ Primary: `Rhetoric` ($0.70$), Secondary: `Taoism` ($0.30$)
  - **Leadership** $\rightarrow$ Primary: `Confucianism` ($0.70$), Secondary: `Xunzi` ($0.30$)
  - **Corporate Governance** $\rightarrow$ Primary: `Legalism` ($0.70$), Secondary: `Confucianism` ($0.30$)
  - **Organization Transformation** $\rightarrow$ Primary: `Taoism` ($0.70$), Secondary: `Xunzi` ($0.30$)
  - **Training / Coaching / Capability Building** $\rightarrow$ Primary: `Xunzi` ($0.70$), Secondary: `Confucianism` ($0.30$)
  - **Organizational Conflict** $\rightarrow$ Tri-Lens: `Confucianism` ($0.60$), `Legalism` ($0.30$), `Taoism` ($0.10$)
- Features Lens Priority, Lens Weights, Lens Confidence Scores, Lens Conflict Resolution, and Explanation Generation.

---

## 3. Domain & Knowledge Unit Catalog

- **Domain Areas:** 20 Frozen Domains (`NT-DA-0001` through `NT-DA-0020`).
- **Knowledge Units:** 274 Frozen Units (75 Laws, 113 Principles, 31 Models, 55 Anti-Patterns).
- **Validation Status:** `scripts/validate_all.py` passes 100% clean.
- **Test Suite Status:** `pytest` passes 100% cleanly.
