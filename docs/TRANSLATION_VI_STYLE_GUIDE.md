# Hướng dẫn dịch thuật ngữ Nhân Thuật (tiếng Anh → tiếng Việt)

Dùng khi Việt hóa nội dung kho tri thức trong `knowledge/units/**/*.yaml`.

## Nguyên tắc chung
- Dịch sang tiếng Việt chuẩn, tự nhiên, chuyên nghiệp, phong cách biên tập tri thức (không viết câu quá dài, không dùng khẩu ngữ).
- **KHÔNG thay đổi** các field cấu trúc: `id`, `type`, `status`, `version`, `primary_domain`, `secondary_domains`, `domain_area`, `evidence`, `relations`, `tags`, `created_at`. Chỉ cập nhật `updated_at` thành `2026-08-15`.
- Dịch các field văn bản: `title`, `summary`, `definition`, `mechanism[]`, `conditions[]`, `exceptions[]`, `applications{...}[]`, `risks[]`.
- **Giữ nguyên số lượng phần tử** trong mỗi mảng.
- **applications**: giữ nguyên khóa section (management, negotiation, leadership, review, environment...), chỉ dịch chuỗi bên trong.
- **evidence.references** (trích dẫn học thuật): giữ nguyên tiếng Anh.
- Độ dài tối thiểu (schema): title ≥ 3 ký tự, summary ≥ 20 ký tự, definition ≥ 20 ký tự, mỗi phần tử mảng ≥ 3 ký tự.
- Viết lại file với `yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000)`.

## Bảng thuật ngữ cố định (đã thống nhất với các unit đã Việt hóa)
- `law` → Quy luật | `principle` → Nguyên tắc | `model` → Mô hình | `anti-pattern` → Phản-mẫu | `phenomenon` → Hiện tượng
- `tri-nhan` → tri nhân | `tu-than` → tự thân | `dung-nhan` → dụng nhân | `hop-chung` → hợp chúng | `thanh-su` → thành sự
- incentives → động lực/khuyến khích | bias → thiên kiến | cognitive load → tải nhận thức
- accountability → trách nhiệm giải trình | agency → quyền hành động/chủ thể | autonomy → quyền tự chủ
- trust → niềm tin | candor → sự thẳng thắn | psychological safety → an toàn tâm lý
- feedback → phản hồi | coordination → phối hợp | decision rights → quyền ra quyết định
- default → mặc định | friction → ma sát/trở ngại | willpower → ý chí
- framing → đóng khung/diễn giải | status quo → hiện trạng | sunk cost → chi phí chìm
- cognitive dissonance → bất hòa nhận thức | conformity → sự tuân thủ | groupthink → tư duy bầy đàn

## Phong cách dịch title
- Dịch thành cụm danh từ/động từ ngắn gọn, đúng trọng tâm. Ví dụ đã chuẩn:
  - "Truth under threat" → "Sự thật bị đe dọa"
  - "Quy luật lợi ích chi phối hành vi" (giữ nguyên)
- Không thêm dấu ngoặc diễn giải vào title trừ khi thuật ngữ gốc cần ghi chú (ví dụ: "Present Bias (Thiên kiến hiện tại)" có thể giữ phần tiếng Anh trong ngoặc để tra cứu).

## Tags (KHÔNG dịch, nhưng làm giàu)
- Giữ nguyên tags tiếng Anh gốc.
- Bổ sung thêm 3-6 từ khóa tiếng Anh (kebab-case, chỉ a-z0-9 và dấu gạch ngang) trích từ nội dung tiếng Anh gốc để tìm kiếm song ngữ, tổng ≤ 8 tags.