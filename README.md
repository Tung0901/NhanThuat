# Nhân Thuật

Nhân Thuật là một hệ tri thức có cấu trúc để lưu trữ, kiểm định và khai thác
tri thức về con người, tổ chức và hành động. Repository là nguồn sự thật chính
thức; nội dung trong hội thoại chỉ là đầu vào cho quy trình biên tập.

## Trạng thái

- Phiên bản: `1.0.0` (Nhánh nội dung tiếng Việt, cập nhật 2026-09-14)
- 31 lĩnh vực tri thức (`NT-DA-0001`..`NT-DA-0031`)
- Canonical content inventory: `docs/content-inventory.json` (379 units: 85 Laws, 135 Principles, 45 Models, 61 Anti-patterns, 52 Phenomena, 1 Strategy; 373 Frozen and 6 draft pending Product Owner review)
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
python scripts/audit_content_inventory.py --check
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
xuất tri thức deterministic. Production có thể dùng DeepSeek làm provider chính
và Gemini làm dự phòng. Chỉ cấu hình provider thực sự sử dụng trong biến môi
trường hoặc file `.env`:

```bash
NHAN_THUAT_LLM_PROVIDER="auto"  # auto ưu tiên DeepSeek rồi mới Gemini
DEEPSEEK_API_KEY="..."
DEEPSEEK_MODEL="deepseek-chat"
GOOGLE_API_KEY="..."           # tùy chọn, provider dự phòng
GEMINI_MODEL="gemini-3.6-flash"
```

Base URL mặc định đã được thiết lập sẵn. Chỉ đặt khi dùng gateway tương thích:

```bash
DEEPSEEK_BASE_URL="https://api.deepseek.com"
```

## Triển khai (Render là chuẩn)

`render.yaml` là cấu hình triển khai chuẩn:

```yaml
buildCommand: pip install -r requirements.txt
startCommand: PYTHONPATH=src python -m backend.app.main
```

Đặt secret `DEEPSEEK_API_KEY` và, nếu cần failover, `GOOGLE_API_KEY` trong
Render Dashboard → Environment. Endpoint `/health` chỉ công bố tên
provider/model đã cấu hình và không trả khóa bí mật.
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
