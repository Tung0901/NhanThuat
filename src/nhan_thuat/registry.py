"""In-memory knowledge registry (foundation for EPIC 2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .loader import iter_documents, load_document


def build_registry(root: str | Path) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for path in iter_documents(Path(root) / "knowledge" / "units"):
        document = load_document(path)
        record_id = document.get("id")
        if not isinstance(record_id, str):
            raise ValueError(f"Missing id: {path}")
        if record_id in registry:
            raise ValueError(f"Duplicate id: {record_id}")
        registry[record_id] = document
    return registry

