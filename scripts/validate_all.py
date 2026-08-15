"""Validate every managed document in the repository."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

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

