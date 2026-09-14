# Nhân Thuật

Nhân Thuật là một hệ tri thức có cấu trúc để lưu trữ, kiểm định và khai thác
tri thức về con người, tổ chức và hành động. Repository là nguồn sự thật chính
thức; nội dung trong hội thoại chỉ là đầu vào cho quy trình biên tập.

## Trạng thái

- Phiên bản: `1.0.0` (Nhánh nội dung tiếng Việt, cập nhật 2026-09-14)
- 31 lĩnh vực tri thức (`NT-DA-0001`..`NT-DA-0031`)
- 379 knowledge units (85 Quy luật, 135 Nguyên tắc, 45 Mô hình, 61 Phản-mẫu, 52 Hiện tượng hành vi, 1 Chiến lược) — 373 units Frozen, 6 units draft chờ Product Owner duyệt freeze
- 18 cẩm nang tri thức (`docs/knowledge/*.md`) + 3 hồ sơ thực chiến (`knowledge/cases/*.yaml`)
- Governance: Frozen Register (`governance/frozen-register.yaml`), validator, CI
- Kiến trúc 5 Lăng kính Triết học (Hùng Biện, Nho gia, Pháp gia, Đạo gia, Tuân Tử)
- Knowledge Runtime: graph traversal, keyword resolver, prompt builder, heuristic evaluator
- Web app "Executive Studio" (`frontend/app.html` + `backend/app/main.py`): Tham Mưu, Hội Đồng Cố Vấn, Đấu Trí, Chẩn Đoán Nhân Sự, Tủ Sách & Tri Thức
- LLM synthesis (EPIC 5, capability `NHANTHUAT-CAP-002`): fallback-first — hoạt động deterministic nếu không cấu hình API key

## Bắt đầu nhanh

Yêu cầu Python 3.11 trở lên.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts/validate_all.py
pytest
ruff check src scripts tests
python -m backend.app.main   # khởi chạy web app tại http://localhost:8000
```

- Landing page: `http://localhost:8000/`
- Web app: `http://localhost:8000/app`

Hoặc dùng Docker:

```bash
docker compose up --build
```

## Cấu hình LLM synthesis (tùy chọn)

Synthesis hoạt động fallback-first: nếu không có key, hệ thống trả về dòng truy
xuất tri thức deterministic. Để kích hoạt LLM synthesis, đặt API key Google AI
Studio (Gemini) vào biến môi trường hoặc file `.env`:

```bash
GEMINI_API_KEY="AIzaSy-..."   # tạo miễn phí tại https://aistudio.google.com/apikey
```

Base URL và mô hình mặc định (`https://generativelanguage.googleapis.com/v1beta/openai`,
`gemini-3.6-flash`) đã được thiết lập sẵn. Chỉ cần đặt khi muốn tùy chỉnh:

```bash
GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai"
GEMINI_MODEL="gemini-3.6-flash"
```

## Triển khai (Render là chuẩn)

`render.yaml` là cấu hình triển khai chuẩn:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: PYTHONPATH=src python -m backend.app.main
```

Đặt secret `GEMINI_API_KEY` trong Render Dashboard → Environment.
Dockerfile và docker-compose dùng cùng entry point (`python -m backend.app.main`).

## Nguyên tắc

1. Nội dung chính thức phải được lưu trong repository.
2. Nội dung và phần mềm được tách biệt.
3. Mọi thay đổi phải qua validation, review và test.
4. Chỉ Product Owner có quyền phê duyệt và quyết định Frozen.
5. Nội dung Frozen không được sửa trực tiếp.

Xem [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md), [ROADMAP.md](ROADMAP.md),
[governance/charter.md](governance/charter.md) và
[governance/approval-process.md](governance/approval-process.md).
