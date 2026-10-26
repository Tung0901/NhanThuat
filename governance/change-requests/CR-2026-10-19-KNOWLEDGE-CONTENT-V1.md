---
id: CR-2026-10-19-KNOWLEDGE-CONTENT-V1
schema_version: 1.0.0
status: ready_for_review
created_at: '2026-10-19'
approval:
  approval_id: null
  approved_by: null
  approved_at: null
  approved_scope: null
  approved_base_commit_sha: null
  approved_review_commit_sha: null
  approved_manifest_sha256: null
---

# Hồ Sơ Yêu Cầu Thay Đổi (Change Request) — Xử Lý 352 Knowledge Units, Chuẩn Hóa Evidence & Pilot Batch 12 Đơn Vị

**Mã Change Request:** `CR-2026-10-19-KNOWLEDGE-CONTENT-V1`
**Ngày lập:** `2026-10-19`
**Trạng thái:** `ready_for_review`
**Thẩm quyền phê duyệt:** Product Owner (Chưa phê duyệt — Agent tuyệt đối không tự chuyển sang `approved`, `APPROVED_BY_PRODUCT_OWNER` hoặc `frozen`)
**Căn cứ quản trị:** `PROJECT_CONSTITUTION.md`, `governance/approval-process.md` (`NT-GOV-APPROVAL-001`), `governance/domain-freeze.md` (`NT-GOV-DOMAIN-FREEZE-001`)

---

## 1. Lý Do Thay Đổi (Rationale)

Trong đợt nâng cấp tự động trước đó, một script sinh nội dung hàng loạt theo mẫu (`upgrade_remaining_352_units.py`) đã tác động trực tiếp lên **352 đơn vị tri thức** (`knowledge/units/**/*.yaml`), gây ra các vi phạm quản trị và chất lượng học thuật nghiêm trọng:
1. **Vi phạm quy trình Change Control đối với nội dung Frozen:** Tự ý cập nhật `content`, tăng `version` lên `1.0.0` và thay đổi `evidence` trên **346 đơn vị đang ở trạng thái `frozen`** khi chưa có hồ sơ Change Request được Product Owner phê duyệt.
2. **Lạm phát mức độ bằng chứng (Evidence Inflation):**
   - Nâng khống `evidence.level` từ `provisional` lên `supported` cho **91 đơn vị** kèm danh sách tài liệu chung theo trục domain mà không gắn trực tiếp với mệnh đề của từng đơn vị.
   - Giữ mức `evidence.level: supported` cho **157 đơn vị** chỉ có mã giữ chỗ `EV-REQ-*` (trong đó có **93 đơn vị** chỉ tham chiếu `EV-REQ-0001-01` — vốn được định nghĩa là `status: placeholder` tại `docs/domains/human-nature/evidence-placeholders.yaml`) và **19 đơn vị** có `references: []`.
3. **Lặp câu chữ khuôn mẫu (Boilerplate Duplication):** Sinh đồng loạt trường `content` chứa các đoạn văn lặp và mệnh đề tuyệt đối hóa hành vi con người (như *"mọi thất bại trong việc xử lý..."*, *"Chúng ta không đánh cược vận mệnh dự án..."*, *"Trong một phiên họp quyết định nhân sự..."*, *"con người luôn vận hành trên hai tầng sóng..."*, *"cửa sổ duy nhất phơi bày cấu trúc nhân cách thật sự"*, *"chân lý bất biến"*, *"áp dụng hiệu quả cho mọi..."*).
4. **Thiếu chuẩn hóa độ bất định và phân loại nguồn:** Chưa tách bạch rõ nghiên cứu thực nghiệm (`[Empirical Study]`), mô hình lý thuyết (`[Theoretical Model]`), tổng quan hệ thống (`[Review/Meta-analysis]`), chuyên khảo học thuật (`[Academic Monograph]`), sách phổ thông (`[Popular Synthesis]`), tương đồng cổ điển (`[Classical Analogy]`), và suy luận biên tập (`[Editorial Inference]`).

Hiện tại, toàn bộ **177 đơn vị Frozen** có sai khác trong working tree đã được hoàn nguyên có chọn lọc về đúng trạng thái base commit `27a34bc` (`27a34bcd840713df1817517066b4cf1a9b1623a3`) bằng manifest và mã băm SHA-256. Audit artifact bất biến ghi nhận chi tiết pre-restore SHA và base SHA cho 177 đơn vị được lưu giữ tại `specs/REMEDIATION-CONTROLLED-RECOVERY/audit_frozen_restore_177_manifest.json`, đồng thời cây nguồn gốc `d28c7ee6451127122238336d91018cd89dc3d67e` đã được neo vĩnh viễn vào đồ thị Git tại tag `evidence/pre-restore-177-frozen` (commit `cb6a5ee15b6f3199239c9af08a038d5a1dc26eae`).

Không có bất kỳ đơn vị Frozen canonical nào bị sửa đổi trực tiếp khi chưa có phê duyệt. Hồ sơ Change Request này được đệ trình để Product Owner xem xét và ra quyết định độc lập trên hai phương án cụ thể bên dưới.

---

## 2. Kiểm Kê Chính Xác 352 Đơn Vị Tri Thức (Inventory Summary)

Bản kê chi tiết từng tệp trong 352 đơn vị được lưu trữ tại `specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json` (sinh từ base commit cố định `27a34bcd840713df1817517066b4cf1a9b1623a3`):

| Hạng mục kiểm kê | Số lượng | Chi tiết |
| :--- | :--- | :--- |
| **Tổng số đơn vị trong tập mục tiêu** | **352** | Trên tổng số 379 đơn vị tri thức của kho (`27` đơn vị còn lại thuộc Wave 1 trong commit `27a34bc`). |
| **Trạng thái quản trị (`status`)** | **346 Frozen / 6 Draft** | `346` đơn vị `frozen`; `6` đơn vị `draft` (`NT-LAW-3201`, `NT-LAW-4102`, `NT-PRINCIPLE-4101`, `NT-PHENOMENON-4101`, `NT-PHENOMENON-4102`, `NT-PHENOMENON-4103`). |
| **Đơn vị Frozen bị can thiệp đợt trước** | **177** | Đã được khôi phục 100% về nguyên trạng base commit `27a34bc` bằng manifest và hash SHA-256 (neo vĩnh viễn trong Git tag `evidence/pre-restore-177-frozen`). |
| **Đơn vị Frozen ghi nhận bằng chứng placeholder** | **171** | `153` đơn vị giữ placeholder `EV-REQ-*` + `18` đơn vị có `references: []` nhưng đang để `supported`. Tách riêng sang lộ trình Dedicated CR. |
| **Đơn vị Pilot đại diện** | **12** | **6 đơn vị Draft canonical** + **6 đơn vị Frozen proposal artifacts** tại `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/` (có slug, `proposed_version > current_version`). |

---

## 3. Hai Quyết Định Độc Lập Trình Product Owner Xem Xét

Hồ sơ này tách biệt rành mạch 2 quyết định phê duyệt để Product Owner có thể duyệt từng phần hoặc toàn bộ:

### QUYẾT ĐỊNH A: Tách Xử Lý 171 Đơn Vị Frozen Mang Bằng Chứng Placeholder Sang Quy Trình Change Request Chuyên Biệt (Dedicated CR)
- **Nội dung:** Theo nguyên tắc quản trị và semver, không được thay đổi trường `evidence` của 171 đơn vị Frozen mà giữ nguyên phiên bản, đồng thời không được tăng phiên bản hàng loạt khi chưa có hồ sơ proposal, đánh giá tác động và spec chi tiết cho từng đơn vị. Do đó, **chưa xây dựng đường áp dụng 171 đơn vị Frozen trong vòng khắc phục này**.
- **Kế hoạch quản trị:**
  1. Giữ nguyên 100% trạng thái canonical của 171 đơn vị Frozen tại base commit `27a34bc`.
  2. Ghi nhận telemetry kiểm kê trong `inventory_352_units.json` phục vụ quản trị minh bạch.
  3. Lập hồ sơ Change Request chuyên biệt riêng trong chu kỳ tiếp theo kèm spec, proposal artifact và semver bump độc lập cho từng đơn vị.
- **Trạng thái thực thi hiện tại:** Không áp dụng thay đổi nào lên 171 Frozen canonical units.

### QUYẾT ĐỊNH B: Áp Dụng 6 Đề Xuất Nâng Cấp Frozen Pilot Vào Canonical Units Theo Cơ Chế Rollback-Assisted Replacement
- **Nội dung:** Cho phép áp dụng 6 bản đề xuất chất lượng cao đã soạn sẵn tại `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/*.yaml` vào các file canonical tương ứng trong `knowledge/units/`. Mọi proposal đều có `proposed_version > current_version` và được áp dụng theo cơ chế giao dịch có hỗ trợ phục hồi (Rollback-Assisted Replacement: tạo staging tạm, thẩm định toàn bộ overlay bằng canonical schema, ghi durable transaction journal trước khi replace, hoán đổi có sao lưu và tự động rollback toàn bộ nếu có bất kỳ lỗi nào).
- **Phạm vi tác động:** 6 đơn vị Frozen đại diện:
  1. `NT-LAW-2101`: Định luật Entropy trong Khủng hoảng (Weick 1993, Perrow 1984, Tôn Tử) — Phiên bản đề xuất: `1.1.0` (hiện tại `1.0.0`).
  2. `NT-MODEL-2101`: Tam Giác Ứng Phó Khủng Hoảng (Bundy et al. 2017, Coombs 2007) — mức evidence giữ nguyên `provisional` trung thực vì là mô hình tổng hợp biên tập; Phiên bản đề xuất: `1.1.0` (hiện tại `1.0.0`).
  3. `NT-MODEL-2201`: Ma Trận Quyền Lực (French & Raven 1959, Podsakoff & Schriesheim 1985, Hàn Phi Tử) — Phiên bản đề xuất: `1.1.0` (hiện tại `1.0.0`).
  4. `NT-PRINCIPLE-0063`: Giảm thiểu quyền lực vai trò (Edmondson 1999, Tôn Tử) — Phiên bản đề xuất: `1.0.0` (hiện tại `0.2.0`).
  5. `NT-ANTI-PATTERN-0012`: Bẫy sức hút cá nhân (Khurana 2002, House & Howell 1992, Hàn Phi Tử) — Phiên bản đề xuất: `1.0.0` (hiện tại `0.2.0`).
  6. `NT-ANTI-PATTERN-0013`: Sự tuân thủ cưỡng ép (Kelman 1958, Deci & Ryan 2000, Quản Tử) — Phiên bản đề xuất: `1.0.0` (hiện tại `0.2.0`).
- **Trạng thái thực thi hiện tại:** Đang ở dạng hồ sơ đề xuất (`proposal artifacts` tại `specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/`) với trạng thái `ready_for_review`. Tuyệt đối chưa ghi đè vào file canonical `frozen`.
- **Nếu PO phê duyệt Quyết định B:** Cập nhật YAML frontmatter của Change Request sang `status: APPROVED_BY_PRODUCT_OWNER` cùng các trường bắt buộc (`approval_id`, `approved_by`, `approved_at`, `approved_scope: "pilot_batch_6_frozen"`, `approved_base_commit_sha: 27a34bcd840713df1817517066b4cf1a9b1623a3`, `approved_review_commit_sha: <40-HEX-REVIEW-COMMIT>`, `approved_manifest_sha256: <HASH-MANIFEST>`, `schema_version: 1.0.0`), sau đó chạy công cụ:
  ```powershell
  python scripts/knowledge_content_pilot_tool.py --apply-frozen --po-approval-id <APPROVAL-ID> --manifest specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json
  ```

---

## 4. Bảng Tổng Hợp 12 Đơn Vị Thuộc Pilot Batch

| STT | Mã Đơn Vị | Loại Hình | Trạng Thái Quản Trị | Vị Trí Lưu Trữ Hiện Tại | Phiên Bản (Hiện tại → Đề xuất) | Mức Bằng Chứng | Phân Loại Nguồn |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| 1 | `NT-LAW-3201` | `law` | `draft` | `knowledge/units/laws/` (canonical) | `0.2.0` → `1.0.0` | `supported` | Empirical Study, Theoretical Model, Popular Synthesis |
| 2 | `NT-LAW-4102` | `law` | `draft` | `knowledge/units/laws/` (canonical) | `0.2.0` → `1.0.0` | `strong` | Empirical Study, Classical Analogy, Editorial Inference |
| 3 | `NT-LAW-2101` | `law` | `frozen` | `specs/.../pilot_units/` (proposal) | `1.0.0` → `1.1.0` | `supported` | Empirical Study, Academic Monograph, Classical Analogy |
| 4 | `NT-PRINCIPLE-4101` | `principle` | `draft` | `knowledge/units/principles/` (canonical) | `0.2.0` → `1.0.0` | `strong` | Academic Monograph, Review/Meta-analysis, Editorial Inference |
| 5 | `NT-PRINCIPLE-0063` | `principle` | `frozen` | `specs/.../pilot_units/` (proposal) | `0.2.0` → `1.0.0` | `supported` | Empirical Study, Theoretical Model, Classical Analogy |
| 6 | `NT-MODEL-2101` | `model` | `frozen` | `specs/.../pilot_units/` (proposal) | `1.0.0` → `1.1.0` | `provisional` | Review/Meta-analysis, Theoretical Model, Editorial Inference |
| 7 | `NT-MODEL-2201` | `model` | `frozen` | `specs/.../pilot_units/` (proposal) | `1.0.0` → `1.1.0` | `strong` | Theoretical Model, Review/Meta-analysis, Classical Analogy |
| 8 | `NT-PHENOMENON-4101` | `phenomenon` | `draft` | `knowledge/units/phenomena/` (canonical) | `0.2.0` → `1.0.0` | `supported` | Academic Monograph, Theoretical Model, Popular Synthesis |
| 9 | `NT-PHENOMENON-4102` | `phenomenon` | `draft` | `knowledge/units/phenomena/` (canonical) | `0.2.0` → `1.0.0` | `strong` | Empirical Study, Popular Synthesis, Editorial Inference |
| 10 | `NT-PHENOMENON-4103` | `phenomenon` | `draft` | `knowledge/units/phenomena/` (canonical) | `0.2.0` → `1.0.0` | `strong` | Empirical Study, Review/Meta-analysis, Classical Analogy |
| 11 | `NT-ANTI-PATTERN-0012` | `anti-pattern` | `frozen` | `specs/.../pilot_units/` (proposal) | `0.2.0` → `1.0.0` | `supported` | Academic Monograph, Theoretical Model, Classical Analogy |
| 12 | `NT-ANTI-PATTERN-0013` | `anti-pattern` | `frozen` | `specs/.../pilot_units/` (proposal) | `0.2.0` → `1.0.0` | `supported` | Theoretical Model, Empirical Study, Classical Analogy |

---

## 5. Kế Hoạch Áp Dụng (Promotion Workflow) & Hoàn Nguyên Bằng Giao Dịch Đã Xác Thực (Verified Rollback)

### 5.1. Quy Trình Đẩy Lên Sản Phẩm Của Product Owner (PO Promotion Workflow)

Nếu Product Owner phê duyệt Quyết định B, việc áp dụng 6 đề xuất vào canonical `knowledge/units/` được thực thi thông qua **Product Owner Promotion Workflow** trong worktree Git tạm độc lập hoàn toàn để bảo đảm cây làm việc chính không bao giờ bị can thiệp ngoài kiểm soát:

1. **Bước 1 — Review Commit:** Toàn bộ đề xuất, manifest và hồ sơ CR được commit lên nhánh làm việc, tạo mã băm Git 40-hex (`approved_review_commit_sha`).
2. **Bước 2 — PO Phê Duyệt:** Product Owner kiểm tra đối chiếu mã băm manifest (`approved_manifest_sha256`), mã băm base commit (`approved_base_commit_sha`) và review commit (`approved_review_commit_sha`), ký cấp `approval_id` trên frontmatter của CR.
   Các trường này cung cấp ràng buộc integrity giữa nội dung và Git tree; danh tính/quyết định của PO vẫn được kiểm soát bằng quy trình review và quyền merge, không được mô tả như chữ ký mật mã.
3. **Bước 3 — Tạo Isolated Git Worktree:** Khởi tạo worktree tạm độc lập từ review commit:
   ```powershell
   git worktree add ../temp-promotion-worktree <approved_review_commit_sha>
   ```
   Công cụ chỉ chấp nhận linked worktree có `.git` dạng pointer file, đang ở detached HEAD và có `HEAD` khớp tuyệt đối với `approved_review_commit_sha`; truyền riêng cờ CLI không đủ để vượt qua chốt bảo vệ.
4. **Bước 4 — Áp Dụng Giao Dịch Có Khóa Độc Quyền (Exclusive Transaction Apply):**
   Trong worktree, thực thi với cờ bắt buộc `--isolated-worktree`:
   ```powershell
   .venv\Scripts\python.exe -X utf8 scripts/knowledge_content_pilot_tool.py --apply-frozen --isolated-worktree --manifest specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json --po-approval-id <APPROVAL_ID>
   ```
   - Công cụ đọc và xác minh toàn bộ manifest và proposal trực tiếp từ cây Git của `approved_review_commit_sha`.
   - Chiếm khóa giao dịch độc quyền (`ExclusiveTransactionLock`) trước khi quét hoặc phục hồi journal, ghi journal bền vững sớm (`PREPARING_STAGING` -> `STAGED`), kiểm định overlay và thay thế nguyên tử kèm rollback tự động nếu lỗi.
   - Staging/backup path trong journal phải là đường dẫn tuyệt đối đã confinement, cùng thư mục canonical và khớp đầy đủ transaction type/PID; path tương đối bị từ chối.
5. **Bước 5 — Kiểm Tra Toàn Bộ Cổng Chất Lượng (Full Quality Gates):**
   Trong worktree, thực thi tuần tự:
   - `.venv\Scripts\ruff check src backend tests scripts`
   - `.venv\Scripts\pytest -q` (toàn bộ test được thu thập)
   - `.venv\Scripts\python scripts/validate_all.py`
   - `.venv\Scripts\python scripts/audit_content_inventory.py --check`
   - `git diff --check`
6. **Bước 6 — Tạo Promotion Commit:** Tạo commit sản phẩm trong worktree chứa các canonical units đã cập nhật.
7. **Bước 7 — Product Owner Merge:** PO kiểm tra commit promotion và merge vào nhánh chính `main`, sau đó dọn dẹp worktree tạm.

### 5.2. Kế Hoạch Hoàn Nguyên An Toàn (Staged, Journaled, Hash-Verified Rollback)

Tuyệt đối cấm sử dụng các lệnh nguy hiểm như `git checkout HEAD -- knowledge/units/` hoặc `git reset`.
Kế hoạch hoàn nguyên khi cần được thiết kế dựa trên manifest bắt buộc và công cụ repo-resident chạy theo giao dịch staged, journaled, hash-verified:

1. **Bước 1: Chạy thử nghiệm khô (Dry-Run — Tuyệt Đối Read-Only):**
   ```powershell
   .venv\Scripts\python.exe -X utf8 scripts/knowledge_content_pilot_tool.py --rollback --manifest specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json --dry-run
   ```
   Lệnh này chỉ đọc các entry có trong manifest, kiểm tra path confinement, hiển thị danh sách các file cần hoàn nguyên; tuyệt đối không ghi file, không tạo journal, không unlink bất kỳ file nào.

2. **Bước 2: Hoàn nguyên bằng giao dịch có khóa độc quyền và kiểm tra mã băm SHA-256 từng file:**
   ```powershell
   .venv\Scripts\python.exe -X utf8 scripts/knowledge_content_pilot_tool.py --rollback --manifest specs/REMEDIATION-CONTROLLED-RECOVERY/inventory_352_units.json --confirm-rollback
   ```
   - Cơ chế: Chiếm khóa độc quyền `ExclusiveTransactionLock` trước recovery, tạo journal `.apply_journal_<pid>.json`, chuẩn bị file staging `.tmp_rollback_<pid>`, thay thế nguyên tử và tạo bản lưu `.bak_rollback_<pid>`.
   - Manifest có entry thiếu đường dẫn, trùng đường dẫn, thoát khỏi `knowledge/units/`, trỏ symlink hoặc thiếu canonical file đều bị từ chối fail-closed.
   - Đọc lại toàn bộ canonical và đối chiếu mã băm khớp 100% với `sha256_base`.
   - Nếu có bất kỳ sai lệch mã băm nào, cơ chế rollback lập tức phục hồi lại từ file backup (fail-closed).
   - Chỉ tác động đúng các file thuộc phạm vi manifest được chỉ định, bảo toàn tuyệt đối mọi file và thay đổi ngoài phạm vi.

---

## 6. Bằng Chứng Kiểm Thử Kỹ Thuật (Verification Evidence)

1. `python -m ruff check src backend tests scripts` → `All checks passed!` (Exit code `0`)
2. `python scripts/validate_all.py` → `Validation passed: all managed documents are valid.` (Exit code `0`)
3. `python scripts/audit_content_inventory.py --check` → Khớp 100% với `docs/content-inventory.json` (Exit code `0`)
4. `git diff --check` → `0 issues` (Exit code `0`)
5. `python scripts/knowledge_content_pilot_tool.py --audit-only` → `Audit passed: all 12 pilot units (6 draft canonical + 6 frozen proposals) and evidence levels are valid.` (Exit code `0`)
6. Kiểm thử đơn vị pilot và an toàn governance:
   `pytest -v tests/test_knowledge_pilot_and_evidence.py` → Vượt qua toàn bộ các test kiểm chứng:
   - Parse CR bằng cấu trúc YAML frontmatter chính thức, cấm nhận dạng bằng substring hay văn xuôi.
   - Bắt buộc `proposed_version > current_version` cho mọi Frozen proposal.
   - Xác nhận mọi `target_path` trong manifest đều tồn tại trên disk và có slug.
   - Thử chạy `--apply-frozen --po-approval-id "Product Owner"` khi CR đang ở trạng thái `ready_for_review` $\rightarrow$ Bị từ chối và thoát với mã lỗi 1 (fail-closed).
   - Thử chạy `--apply-frozen` thiếu từng hash hoặc sai định dạng 64 hex $\rightarrow$ Bị từ chối và thoát với mã lỗi 1 (fail-closed).
   - Kiểm thử fixture CR approved hợp lệ (`status: APPROVED_BY_PRODUCT_OWNER`, đầy đủ `approval_id`, `approved_by`, `approved_at`) với `--apply-frozen --dry-run` $\rightarrow$ Vượt qua xác thực thành công.
   - Thử chạy `--rollback` thiếu `--manifest` $\rightarrow$ Bị từ chối và thoát với mã lỗi 1.
   - Thử nghiệm rollback `--dry-run` $\rightarrow$ Hoạt động chuẩn xác, không làm bẩn working tree.

---

## 7. Trạng Thái Phê Duyệt Của Product Owner (Pending Sign-off)

- **Trạng thái hiện tại:** `ready_for_review`
- **Ghi chú quản trị:** Hồ sơ này dừng lại ở mức đề xuất kỹ thuật và kiểm thử hoàn tất. Agent không tự duyệt, không tự chuyển sang `APPROVED_BY_PRODUCT_OWNER` hay `frozen`, không thực hiện `git commit` và không thực hiện `git push`.
