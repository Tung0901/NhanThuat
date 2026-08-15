# Nhân Thuật

Nhân Thuật là một hệ tri thức có cấu trúc để lưu trữ, kiểm định và khai thác
tri thức về con người, tổ chức và hành động. Repository là nguồn sự thật chính
thức; nội dung trong hội thoại chỉ là đầu vào cho quy trình biên tập.

## Trạng thái

- Phiên bản: `1.0.0`
- 30 lĩnh vực tri thức (`NT-DA-0001`..`NT-DA-0030`)
- 370 knowledge units (82 Luật, 134 Nguyên tắc, 45 Mô hình, 60 Phản-mẫu, 49 Hiện tượng hành vi) — tất cả ở trạng thái Frozen
- Governance: Frozen Register (`governance/frozen-register.yaml`), validator, CI
- Kiến trúc 5 Lăng kính Triết học (Hùng Biện, Nho gia, Pháp gia, Đạo gia, Tuân Tử)
- Knowledge Runtime: graph traversal, keyword resolver, prompt builder, heuristic evaluator
- Knowledge Workbench (Streamlit): 6 trang — Hỏi Nhân Thuật, Khám phá Tri thức, Lĩnh vực, Bằng chứng & Nguồn, Hệ thống, Chi tiết Tri thức
- LLM synthesis (EPIC 5, capability `NHANTHUAT-CAP-002`): fallback-first — hoạt động deterministic nếu không cấu hình API key

## Bắt đầu nhanh

Yêu cầu Python 3.11 trở lên.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts/validate_all.py
pytest
python scripts/run_web_dashboard.py   # khởi chạy Knowledge Workbench
```

### Cấu hình LLM synthesis (tùy chọn)

EPIC 5 synthesis hoạt động fallback-first: nếu không có key, trang Hỏi Nhân Thuật
trả về dòng truy xuất deterministic. Để kích hoạt LLM synthesis, đặt API key
Google AI Studio (Gemini) vào `.streamlit/secrets.toml` (tham khảo `secrets.toml.example`):

```toml
GEMINI_API_KEY = "AIzaSy-..."   # tạo miễn phí tại https://aistudio.google.com/apikey
```

Base URL và mô hình mặc định (`https://generativelanguage.googleapis.com/v1beta/openai`,
`gemini-3.6-flash`) đã được thiết lập sẵn. Chỉ cần đặt chúng khi muốn tùy chỉnh:

```toml
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
GEMINI_MODEL = "gemini-3.6-flash"
```

Trên Streamlit Community Cloud, dán nguyên khối TOML ở trên vào
**app → Settings → Secrets** (không cần file `.streamlit/secrets.toml`).

## Nguyên tắc

1. Nội dung chính thức phải được lưu trong repository.
2. Nội dung và phần mềm được tách biệt.
3. Mọi thay đổi phải qua validation, review và test.
4. Chỉ Product Owner có quyền phê duyệt và quyết định Frozen.
5. Nội dung Frozen không được sửa trực tiếp.

Xem [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md), [ROADMAP.md](ROADMAP.md),
[governance/charter.md](governance/charter.md) và
[governance/approval-process.md](governance/approval-process.md).