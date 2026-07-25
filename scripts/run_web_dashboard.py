"""
CHƯƠNG TRÌNH KHỞI CHẠY GIAO DIỆN WEB DASHBOARD BUSINESSOS & NHÂN THUẬT (M16)

Cách chạy:
    python scripts/run_web_dashboard.py

Sau khi chạy, mở trình duyệt web tại địa chỉ:
    http://localhost:8000
"""

import sys
import subprocess
import webbrowser
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent

# Auto-switch to project virtual environment .venv if running under global python
try:
    import yaml
    import jsonschema
except ImportError:
    venv_python = repo_root / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists() and str(venv_python) != sys.executable:
        res = subprocess.run([str(venv_python)] + sys.argv, check=False)
        sys.exit(res.returncode)

# Ensure src and backend are accessible in sys.path
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from backend.app.main import create_app_server


def main() -> None:
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}"

    print("=" * 80)
    print("  KÍCH HOẠT DỰNG WEB APP DASHBOARD BUSINESSOS & NHÂN THUẬT (MILESTONE M16)")
    print("=" * 80)
    print(f"✓ Web Server đang lắng nghe tại: {url}")
    print("✓ Tự động mở trình duyệt web trong giây lát...")
    print("  (Bấm Ctrl + C tại Terminal nếu muốn dừng Web Server)")
    print("=" * 80)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    server = create_app_server(host=host, port=port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOPPED] Đã dừng Web Server BusinessOS.")
        server.server_close()


if __name__ == "__main__":
    main()
