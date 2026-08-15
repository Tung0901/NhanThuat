"""
BusinessOS Persistence Storage Boundary Module.
Provides abstract storage interfaces and adapters for state persistence:
- InMemoryStorageAdapter (In-memory testing)
- FileStateStorageAdapter (File-backed development state)
- Prepared extension interfaces for PostgreSQL, Redis, and Vector Storage.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseStorageAdapter(ABC):
    """Abstract Base Class for BusinessOS Storage Adapters."""

    @abstractmethod
    def get(self, collection: str, key: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def set(self, collection: str, key: str, value: dict[str, Any]) -> None: ...

    @abstractmethod
    def list(self, collection: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def delete(self, collection: str, key: str) -> bool: ...


class InMemoryStorageAdapter(BaseStorageAdapter):
    """In-Memory Testing Storage Adapter."""

    def __init__(self) -> None:
        self._store: dict[str, dict[str, dict[str, Any]]] = {}

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        return self._store.get(collection, {}).get(key)

    def set(self, collection: str, key: str, value: dict[str, Any]) -> None:
        self._store.setdefault(collection, {})[key] = value

    def list(self, collection: str) -> list[dict[str, Any]]:
        return list(self._store.get(collection, {}).values())

    def delete(self, collection: str, key: str) -> bool:
        if collection in self._store and key in self._store[collection]:
            del self._store[collection][key]
            return True
        return False


class FileStateStorageAdapter(BaseStorageAdapter):
    """File-Backed Development State Storage Adapter."""

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "generated" / "storage_state"
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, collection: str, key: str) -> Path:
        col_dir = self.base_dir / collection
        col_dir.mkdir(parents=True, exist_ok=True)
        clean_key = "".join(c for c in key if c.isalnum() or c in ("-", "_"))
        return col_dir / f"{clean_key}.json"

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        file_p = self._get_path(collection, key)
        if file_p.exists():
            with open(file_p, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def set(self, collection: str, key: str, value: dict[str, Any]) -> None:
        file_p = self._get_path(collection, key)
        with open(file_p, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, default=str, ensure_ascii=False)

    def list(self, collection: str) -> list[dict[str, Any]]:
        col_dir = self.base_dir / collection
        if not col_dir.exists():
            return []
        items = []
        for file_p in col_dir.glob("*.json"):
            with open(file_p, "r", encoding="utf-8") as f:
                items.append(json.load(f))
        return items

    def delete(self, collection: str, key: str) -> bool:
        file_p = self._get_path(collection, key)
        if file_p.exists():
            file_p.unlink()
            return True
        return False
