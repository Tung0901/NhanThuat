"""
CHƯƠNG TRÌNH KHỞI CHẠY GIAO DIỆN WEB DASHBOARD NHÂN THUẬT KNOWLEDGE WORKBENCH

Cách chạy:
    python scripts/run_web_dashboard.py

Sau khi chạy, mở trình duyệt web tại địa chỉ:
    http://localhost:8000
"""

import os
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
APP_SCRIPT = REPO_ROOT / "app" / "streamlit_app.py"

def main() -> None:
    host = "127.0.0.1"
    port = "8000"
    url = f"http://{host}:{port}"

    print("=" * 80)
    print("  KÍCH HOẠT NHÂN THUẬT KNOWLEDGE WORKBENCH (STREAMLIT)")
    print("=" * 80)
    print(f"✓ Web Server sẽ lắng nghe tại: {url}")
    print("  (Bấm Ctrl + C tại Terminal nếu muốn dừng Web Server)")
    print("=" * 80)

    python_cmd = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    cmd = [
        python_cmd,
        "-m",
        "streamlit",
        "run",
        str(APP_SCRIPT),
        "--server.port",
        port,
        "--browser.gatherUsageStats",
        "false",
        "--theme.base",
        "light"
    ]
    
    try:
        subprocess.run(cmd, cwd=str(REPO_ROOT))
    except KeyboardInterrupt:
        print("\n[STOPPED] Đã dừng Web Server.")

if __name__ == "__main__":
    main()
