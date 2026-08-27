"""
CHƯƠNG TRÌNH KHỞI CHẠY GIAO DIỆN WEB DASHBOARD & API GATEWAY NHÂN THUẬT

Cách chạy:
    python scripts/run_web_dashboard.py

Mặc định lắng nghe tại:
    http://0.0.0.0:8000 (Truy cập: http://localhost:8000)
Có thể tùy biến cổng qua biến môi trường PORT (ví dụ: PORT=8080 python scripts/run_web_dashboard.py).
"""

import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.main import create_app_server


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    local_url = f"http://localhost:{port}" if host == "0.0.0.0" else f"http://{host}:{port}"

    print("=" * 80)
    print("  KÍCH HOẠT NHÂN THUẬT & BUSINESSOS WEB DASHBOARD GATEWAY SERVER")
    print("=" * 80)
    print(f"✓ Web Server đang lắng nghe tại: http://{host}:{port}")
    print(f"✓ Địa chỉ truy cập trình duyệt : {local_url}")
    print("  (Bấm Ctrl + C tại Terminal nếu muốn dừng Web Server)")
    print("=" * 80)

    server = create_app_server(host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOPPED] Đã dừng Web Server.")
        server.server_close()


if __name__ == "__main__":
    main()
