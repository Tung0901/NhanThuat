# Hồ Sơ Yêu Cầu Thay Đổi (Change Request) — Xử Lý 352 Knowledge Units, Chuẩn Hóa Evidence & Pilot Batch 12 Đơn Vị

**Mã Change Request:** `CR-2026-10-19-KNOWLEDGE-CONTENT-V1`  
**Ngày lập:** `2026-10-19`  
**Trạng thái:** `ready_for_review`  
**Thẩm quyền phê duyệt:** Product Owner (Chưa phê duyệt — Agent tuyệt đối không tự chuyển sang `approved` hoặc `frozen`)  
**Căn cứ quản trị:** `PROJECT_CONSTITUTION.md`, `governance/approval-process.md` (`NT-GOV-APPROVAL-001`), `governance/domain-freeze.md` (`NT-GOV-DOMAIN-FREEZE-001`)  

---

## 1. Lý Do Thay Đổi (Rationale)

Trong đợt nâng cấp tự động trước đó, một script sinh nội dung hàng loạt theo mẫu (`upgrade_remaining_352_units.py`) đã tác động trực tiếp lên **352 đơn vị tri thức** (`knowledge/units/**/*.yaml`), gây ra 4 vi phạm quản trị và chất lượng học thuật:
1. **Vi phạm quy trình Change Control đối với nội dung Frozen:** Tự ý cập nhật `content`, tăng `version` lên `1.0.0` và thay đổi `evidence` trên **346 đơn vị đang ở trạng thái `frozen`** khi chưa có hồ sơ Change Request được Product Owner phê duyệt.
2. **Lạm phát mức độ bằng chứng (Evidence Inflation):**
   - Nâng khống `evidence.level` từ `provisional` lên `supported` cho **91 đơn vị** kèm danh sách tài liệu chung theo trục domain mà không gắn trực tiếp với mệnh đề của từng đơn vị, đồng thời làm sai lệch 2 bộ kiểm thử miền (`tests/test_motivation_domain.py`, `tests/test_personality_domain.py`).
   - Giữ mức `evidence.level: supported` cho **157 đơn vị** chỉ có mã giữ chỗ `EV-REQ-*` (trong đó có **93 đơn vị** chỉ tham chiếu `EV-REQ-0001-01` — vốn được định nghĩa là `status: placeholder` tại `docs/domains/human-nature/evidence-placeholders.yaml`) và **19 đơn vị** có `references: []`.
3. **Lặp câu chữ khuôn mẫu (Boilerplate Duplication):** Sinh đồng loạt trường `content` chứa các đoạn văn lặp và mệnh đề tuyệt đối hóa hành vi con người (như *"mọi thất bại trong việc xử lý..."*, *"Chúng ta không đánh cược vận mệnh dự án..."*, *"Trong một phiên họp quyết định nhân sự..."*, *"con người luôn vận hành trên hai tầng sóng..."*, *"cửa sổ duy nhất phơi bày cấu trúc nhân cách thật sự"*, *"chân lý bất biến"*).
4. **Thiếu chuẩn hóa độ bất định và phân loại nguồn:** Chưa tách bạch rõ nghiên cứu thực nghiệm (`[Nghiên cứu thực nghiệm]`), nguồn cổ điển (`[Nguồn cổ điển]`), sách phổ thông (`[Sách phổ thông]`) và suy luận biên tập (`[Suy luận biên tập]`).

---

## 2. Kiểm Kê Chính Xác 352 Đơn Vị Tri Thức (Inventory Summary)

Bản kê chi tiết từng tệp trong 352 đơn vị được lưu trữ đầy đủ tại `specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json`. Tổng hợp số liệu đối chiếu giữa `HEAD` và đợt chạy hàng loạt trước khi phục hồi:

| Hạng mục kiểm kê | Số lượng | Chi tiết |
| :--- | :--- | :--- |
| **Tổng số file bị sửa trong đợt batch** | **352** | Trên tổng số 379 đơn vị tri thức của kho (`27` đơn vị còn lại thuộc commit `HEAD` `27a34bc`). |
| **Trạng thái (`status`)** | **346 Frozen / 6 Draft** | `346` đơn vị `frozen -> frozen`; `6` đơn vị `draft -> draft` (`NT-LAW-3201`, `NT-LAW-4102`, `NT-PRINCIPLE-4101`, `NT-PHENOMENON-4101`, `NT-PHENOMENON-4102`, `NT-PHENOMENON-4103`). |
| **Biến động `version` (trước → sau batch)** | **352** | `0.2.0 -> 1.0.0`: **179** đơn vị; `0.1.0 -> 1.0.0`: **147** đơn vị; `1.0.0 -> 1.0.0`: **26** đơn vị (`20` Frozen, `6` Draft). |
| **Biến động `evidence.level` (trước → sau batch)** | **352** | `provisional -> supported` (lạm phát): **91** đơn vị (`85` đơn vị từ `0` ref lên `3` refs chung, `6` đơn vị giữ `1` ref); `supported -> supported`: **186** đơn vị (gồm `93` đơn vị `EV-REQ-0001-01`, `64` đơn vị `EV-REQ-0009-01..0020-01`, `19` đơn vị `0` ref bị chèn `3` refs chung, `10` đơn vị có ref riêng); `strong -> strong`: **75** đơn vị. |
| **Nội dung tạo bằng boilerplate** | **352 / 352** | Toàn bộ 352 đơn vị đều bị chèn trường `content` sinh từ template cố định chứa các cụm từ lặp bị cấm. |

---

## 3. Phạm Vi Thực Thi Trong Hồ Sơ Change Request Này (Scope)

1. **Hoàn nguyên toàn bộ nội dung boilerplate và version tự tăng trên 340 đơn vị ngoài Pilot:**
   - Khôi phục `content` và `version` của 340 đơn vị về đúng trạng thái `HEAD`, chấm dứt việc viết lại đồng loạt bằng template khi chưa có phê duyệt của Product Owner.
   - Khôi phục 91 đơn vị bị nâng khống `provisional -> supported` về lại `provisional` như `HEAD`, đồng thời khôi phục nguyên trạng 2 file test `tests/test_motivation_domain.py` và `tests/test_personality_domain.py`.
2. **Hạ mức bằng chứng về mức trung thực (`provisional`) cho 171 đơn vị Frozen chỉ có placeholder hoặc rỗng:**
   - Đối với **153 đơn vị Frozen ngoài Pilot** chỉ tham chiếu `EV-REQ-*` (`89` đơn vị `EV-REQ-0001-01` và `64` đơn vị `EV-REQ-0009-01..0020-01`) cùng **18 đơn vị Frozen ngoài Pilot** có `references: []` nhưng đang để `level: supported` trong `HEAD`, hạ `evidence.level` từ `supported` xuống `provisional` để phản ánh trung thực trạng thái giữ chỗ.
3. **Biên soạn Pilot Batch 12 đơn vị đại diện (6 Draft + 6 Frozen) trình Product Owner duyệt mẫu:**
   - Đại diện đầy đủ 5 chủng loại (`law`, `principle`, `model`, `phenomenon`, `anti-pattern`).
   - Mỗi đơn vị được biên soạn chuyên biệt (zero boilerplate, không có cụm từ tuyệt đối hóa) với đầy đủ: **Điều kiện áp dụng**, **Ngoại lệ**, **Mức bất định**, **Rủi ro diễn giải sai**, và **Nguồn truy nguyên phân loại** (`[Nghiên cứu thực nghiệm]`, `[Nguồn cổ điển]`, `[Sách phổ thông]`, `[Suy luận biên tập]`).

### Danh Sách 12 Đơn Vị Thuộc Pilot Batch

| STT | Mã Đơn Vị | Loại | Trạng Thái | Tiêu Đề | Mức Bằng Chứng Sau Chuẩn Hóa |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `NT-LAW-3201` | `law` | `draft` | Quy luật Giá trị Cảm nhận | `supported` (4 nguồn phân loại) |
| 2 | `NT-LAW-4102` | `law` | `draft` | Quy luật Ngại Mất Mát (Loss Aversion) | `strong` (4 nguồn phân loại) |
| 3 | `NT-LAW-2101` | `law` | `frozen` | Định luật Entropy trong Khủng hoảng | `supported` (4 nguồn phân loại) |
| 4 | `NT-PRINCIPLE-4101` | `principle` | `draft` | Nguyên tắc Giảm Tải trọng Nhận thức | `strong` (4 nguồn phân loại) |
| 5 | `NT-PRINCIPLE-0063` | `principle` | `frozen` | Giảm thiểu quyền lực vai trò | `supported` (thay thế `EV-REQ-0001-01`) |
| 6 | `NT-MODEL-2101` | `model` | `frozen` | Tam Giác Ứng Phó Khủng Hoảng | `supported` (4 nguồn phân loại) |
| 7 | `NT-MODEL-2201` | `model` | `frozen` | Ma Trận Quyền Lực | `strong` (4 nguồn phân loại) |
| 8 | `NT-PHENOMENON-4101` | `phenomenon` | `draft` | Hiệu ứng Hàng hiệu (Veblen Effect) | `supported` (4 nguồn phân loại) |
| 9 | `NT-PHENOMENON-4102` | `phenomenon` | `draft` | Hiệu ứng Chim mồi (Decoy Effect) | `strong` (4 nguồn phân loại) |
| 10 | `NT-PHENOMENON-4103` | `phenomenon` | `draft` | Hiệu ứng Ảo tưởng Sự thật | `strong` (4 nguồn phân loại) |
| 11 | `NT-ANTI-PATTERN-0012` | `anti-pattern` | `frozen` | Bẫy sức hút cá nhân | `supported` (thay thế `EV-REQ-0001-01`) |
| 12 | `NT-ANTI-PATTERN-0013` | `anti-pattern` | `frozen` | Sự tuân thủ cưỡng ép | `supported` (thay thế `EV-REQ-0001-01`) |

---

## 4. Đánh Giá Tác Động (Impact Analysis)

- **Tác động Schema (`schemas/knowledge-unit.schema.json`):** Không thay đổi schema. Mọi trường (`evidence.level`, `evidence.references`, `content`) tuân thủ 100% Draft 2020-12 JSON Schema hiện hành.
- **Tác động Taxonomy & Ontology (`knowledge/domains/`, `knowledge/domain-registry.yaml`):** Không thay đổi phân loại miền (`primary_domain`, `secondary_domains`, `domain_area`) hay liên kết quan hệ (`relations`). Bản kê `docs/content-inventory.json` giữ nguyên 100% số lượng miền, đơn vị và trạng thái.
- **Tác động Nội dung & Bằng chứng (`knowledge/units/`):**
  - `12` đơn vị Pilot (6 `draft`, 6 `frozen`) có nội dung học thuật chuyên sâu và danh mục tài liệu tham khảo phân loại rõ ràng.
  - `171` đơn vị Frozen chỉ có `EV-REQ-*` hoặc `references: []` được điều chỉnh `evidence.level` từ `supported` về `provisional`.
  - `169` đơn vị Frozen còn lại trong nhóm 352 được khôi phục nguyên vẹn 100% về `HEAD`.

---

## 5. Kế Hoạch Rollback (Rollback Plan)

- Nếu Product Owner yêu cầu hoàn nguyên toàn bộ các thay đổi trên nhóm đơn vị Frozen về trạng thái commit `HEAD` (`27a34bc`):
  ```powershell
  git checkout HEAD -- knowledge/units/
  ```
- Công cụ `scripts/knowledge_content_pilot_tool.py` hỗ trợ chế độ `--dry-run` và xuất `--manifest` giúp kiểm soát chính xác từng file trước khi ghi.

---

## 6. Bằng Chứng Kiểm Thử (Verification Evidence)

1. `python -m ruff check src backend tests scripts` → `All checks passed!` (Exit code `0`)
2. `pytest -q` → Toàn bộ test suite vượt qua 100%, bao gồm `tests/test_motivation_domain.py`, `tests/test_personality_domain.py` (nguyên bản `HEAD`) và `tests/test_knowledge_pilot_and_evidence.py` (Exit code `0`)
3. `python scripts/validate_all.py` → `Validation passed: all managed documents are valid.` (Exit code `0`)
4. `python scripts/audit_content_inventory.py --check` → Khớp 100% với `docs/content-inventory.json` (Exit code `0`)
5. `python scripts/knowledge_content_pilot_tool.py --audit-only` → `Audit passed: all pilot units and evidence levels are valid.` (Exit code `0`)

---

## 7. Phê Duyệt Của Product Owner (Pending Product Owner Sign-off)

- **Trạng thái hiện tại:** `ready_for_review`
- **Quyết định cần Product Owner phê chuẩn:**
  1. Phê duyệt việc hạ `evidence.level` về `provisional` cho 171 đơn vị Frozen chỉ chứa placeholder `EV-REQ-*` hoặc `references: []`.
  2. Phê duyệt chất lượng mẫu của 12 đơn vị trong Pilot Batch trước khi cho phép mở rộng biên soạn cho các đơn vị còn lại theo từng đợt nhỏ.

