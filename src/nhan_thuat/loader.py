"""Load repository data without coupling callers to YAML or JSON details."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

SUPPORTED_SUFFIXES = {".yaml", ".yml", ".json"}


class LoadError(ValueError):
    """Raised when a structured data file cannot be loaded safely."""


def load_document(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise LoadError(f"Unsupported file type: {source}")
    try:
        with source.open(encoding="utf-8") as stream:
            data = json.load(stream) if source.suffix.lower() == ".json" else yaml.safe_load(stream)
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise LoadError(f"Cannot load {source}: {exc}") from exc
    if not isinstance(data, dict):
        raise LoadError(f"Document root must be an object: {source}")
    return data


def iter_documents(root: str | Path) -> list[Path]:
    base = Path(root)
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*") if path.suffix.lower() in SUPPORTED_SUFFIXES)

