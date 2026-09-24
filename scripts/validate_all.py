"""Validate every managed document in the repository."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Tự động kích hoạt môi trường ảo .venv nếu chạy từ Python hệ thống thiếu thư viện
try:
    import yaml  # noqa: F401
except ImportError:
    import os
    venv_py = (
        REPO_ROOT / ".venv" / "Scripts" / "python.exe"
        if os.name == "nt"
        else REPO_ROOT / ".venv" / "bin" / "python"
    )
    if venv_py.exists() and sys.executable != str(venv_py):
        import subprocess
        sys.exit(subprocess.call([str(venv_py), str(Path(__file__).resolve()), *sys.argv[1:]]))
    raise

from nhan_thuat.validator import validate_repository


def main() -> int:
    issues = validate_repository(REPO_ROOT)
    if issues:
        print(f"Validation failed with {len(issues)} issue(s):")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("Validation passed: all managed documents are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

