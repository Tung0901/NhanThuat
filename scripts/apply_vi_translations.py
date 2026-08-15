"""Merge per-unit Vietnamese translations (JSON) into knowledge-unit YAML files.

The translation JSON maps unit id -> dict with translated text fields:
    {"NT-PRINCIPLE-0001": {
        "title": "...", "summary": "...", "definition": "...",
        "mechanism": [...], "conditions": [...], "exceptions": [...],
        "applications": {...}, "risks": [...], "en_tags": [...],
    }, ...}

- Preserves all non-text fields (id, type, status, version, primary_domain,
  secondary_domains, domain_area, evidence, relations, tags, created_at).
- Merges translated fields over the original; keeps missing fields as-is.
- Enriches tags: original tags + optional en_tags (kebab-case), capped at 8.
- Updates ``updated_at`` to 2026-08-15.

Usage:
    python scripts/apply_vi_translations.py translations_batch.json
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TAG_CAP = 8
UPDATED_AT = "2026-08-15"
TEXT_FIELDS = ("title", "summary", "definition", "mechanism", "conditions", "exceptions", "risks")


def find_unit_files() -> dict[str, Path]:
    base = REPO_ROOT / "knowledge" / "units"
    mapping: dict[str, Path] = {}
    for path in base.rglob("*.yaml"):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("id"):
            mapping[str(data["id"])] = path
    return mapping


def merge_translation(original: dict, translated: dict) -> dict:
    merged = dict(original)
    for field in TEXT_FIELDS:
        if field in translated:
            merged[field] = translated[field]
    if isinstance(translated.get("applications"), dict):
        merged["applications"] = translated["applications"]
    tags = [str(tag) for tag in original.get("tags", [])]
    for keyword in translated.get("en_tags", []):
        cleaned = re.sub(r"[^a-z0-9-]", "-", str(keyword).strip().lower())
        cleaned = re.sub(r"-+", "-", cleaned).strip("-")
        if cleaned and cleaned not in tags and len(tags) < TAG_CAP:
            tags.append(cleaned)
    merged["tags"] = tags
    merged["updated_at"] = UPDATED_AT
    return merged


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
    if len(sys.argv) != 2:
        print("usage: python scripts/apply_vi_translations.py translations.json")
        return 1
    payload_path = Path(sys.argv[1])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    files = find_unit_files()

    done = skipped = missing = 0
    for unit_id, translated in payload.items():
        path = files.get(unit_id)
        if path is None:
            print(f"MISSING FILE: {unit_id}")
            missing += 1
            continue
        original = yaml.safe_load(path.read_text(encoding="utf-8"))
        merged = merge_translation(original, translated)
        write_unit(path, merged)
        done += 1
        print(f"  OK {unit_id} | {merged['title']}")
    print(f"\nDone: {done} written, {skipped} skipped, {missing} missing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())