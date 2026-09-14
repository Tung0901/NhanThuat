"""Apply content upgrades (real content) to knowledge-unit YAML files.

Input: JSON mapping unit id -> dict of content fields:
    {"NT-LAW-0037": {
        "summary": "...", "definition": "...", "mechanism": [...],
        "conditions": [...], "exceptions": [...], "applications": {...},
        "risks": [...],
    }, ...}

Behaviour:
- Merges provided fields over the original document, preserving all other
  fields (id, type, status, version, domains, evidence, relations, tags...).
- Bumps ``version`` from 0.1.0 to 0.2.0 for upgraded units.
- Sets ``updated_at`` to the given date (default 2026-09-14).
- Writes YAML with ``sort_keys=False, allow_unicode=True``.

Usage:
    python scripts/apply_content_upgrade.py content_batch.json [--date 2026-09-14]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_FIELDS = (
    "summary",
    "definition",
    "mechanism",
    "conditions",
    "exceptions",
    "applications",
    "risks",
)


def find_unit_files() -> dict[str, Path]:
    base = REPO_ROOT / "knowledge" / "units"
    mapping: dict[str, Path] = {}
    for path in base.rglob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("id"):
            mapping[str(data["id"])] = path
    return mapping


def write_unit(path: Path, data: dict) -> None:
    text = yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=1000,
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("payload")
    parser.add_argument("--date", default="2026-09-14")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    files = find_unit_files()

    done = missing = 0
    for unit_id, fields in payload.items():
        path = files.get(unit_id)
        if path is None:
            print(f"  MISSING {unit_id}")
            missing += 1
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for key in CONTENT_FIELDS:
            if key in fields:
                data[key] = fields[key]
        version = str(data.get("version", "0.1.0"))
        if version == "0.1.0":
            data["version"] = "0.2.0"
        data["updated_at"] = args.date
        write_unit(path, data)
        done += 1
        print(f"  OK {unit_id} v{data['version']} | {data['title']}")
    print(f"\nDone: {done} written, {missing} missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
