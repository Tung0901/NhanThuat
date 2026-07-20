"""Build a deterministic JSON catalog from knowledge units."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nhan_thuat.registry import build_registry  # noqa: E402


def main() -> int:
    registry = build_registry(REPO_ROOT)
    output = REPO_ROOT / "docs" / "generated" / "catalog.json"
    output.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(registry)} record(s) to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

