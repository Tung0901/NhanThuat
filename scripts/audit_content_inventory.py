"""Audit the canonical knowledge registry and optionally write its manifest."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from nhan_thuat.registry import load_registry


def build_inventory() -> dict[str, object]:
    registry = load_registry(REPO_ROOT)
    return {
        "source": "knowledge/",
        "top_level_domains": len(registry.domains),
        "domains": [
            {
                "id": domain.id,
                "slug": domain.slug,
                "name": domain.name,
                "status": domain.status,
                "topic_count": len(domain.topics),
            }
            for domain in registry.domains.values()
        ],
        "knowledge_units": len(registry.units),
        "units_by_type": dict(sorted(Counter(unit.type for unit in registry.units.values()).items())),
        "units_by_status": dict(sorted(Counter(unit.status for unit in registry.units.values()).items())),
        "evidence_records": len(registry.evidence),
        "relations": len(registry.relations),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write docs/content-inventory.json")
    parser.add_argument("--check", action="store_true", help="Fail if the committed manifest is stale")
    args = parser.parse_args()

    inventory = build_inventory()
    output = REPO_ROOT / "docs" / "content-inventory.json"
    encoded = json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
    if args.write:
        output.write_text(encoded, encoding="utf-8")
    if args.check:
        if not output.exists() or json.loads(output.read_text(encoding="utf-8")) != inventory:
            print(f"Content inventory is stale: {output}", file=sys.stderr)
            return 1
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
