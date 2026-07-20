# Nhân Thuật

Nhân Thuật là một hệ tri thức có cấu trúc để lưu trữ, kiểm định và khai thác
tri thức về con người, tổ chức và hành động. Repository là nguồn sự thật chính
thức; nội dung trong hội thoại chỉ là đầu vào cho quy trình biên tập.

## Trạng thái

- Phiên bản: `0.1.0-dev`
- Giai đoạn: EPIC 1 — Hiến chương và nền tảng
- EPIC 0 đã được Frozen; EPIC 1 đang ở trạng thái Ready for Review.

## Bắt đầu nhanh

Yêu cầu Python 3.11 trở lên.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts/validate_all.py
pytest
```

## Nguyên tắc

1. Nội dung chính thức phải được lưu trong repository.
2. Nội dung và phần mềm được tách biệt.
3. Mọi thay đổi phải qua validation, review và test.
4. Chỉ Product Owner có quyền phê duyệt và quyết định Frozen.
5. Nội dung Frozen không được sửa trực tiếp.

Xem [PROJECT_CONSTITUTION.md](PROJECT_CONSTITUTION.md), [ROADMAP.md](ROADMAP.md),
[governance/charter.md](governance/charter.md) và
[governance/approval-process.md](governance/approval-process.md).
