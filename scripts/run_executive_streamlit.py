"""
Runner script for BusinessOS Streamlit Native UI (Milestone M16).
Launches Streamlit app directly in headless mode using project's virtual environment.
Usage: python scripts/run_executive_streamlit.py
"""

import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
APP_SCRIPT = REPO_ROOT / "scripts" / "app_executive.py"

if __name__ == "__main__":
    python_cmd = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    cmd = [
        python_cmd,
        "-m",
        "streamlit",
        "run",
        str(APP_SCRIPT),
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
        "--server.port",
        "8501"
    ]
    print("Launching BusinessOS Executive Streamlit UI on http://localhost:8501...")
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(REPO_ROOT))
