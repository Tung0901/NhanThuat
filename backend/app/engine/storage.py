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


class SQLiteStorageAdapter(BaseStorageAdapter):
    """SQLite-backed Persistence Storage Adapter for Enterprise Execution State."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        import sqlite3
        self._sqlite3 = sqlite3
        if db_path is None:
            db_dir = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "generated" / "storage_state"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "nhanthuat_runtime.db"
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = self._sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = self._sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    collection TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    updated_at REAL NOT NULL,
                    PRIMARY KEY (collection, key)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_records_collection ON records(collection)"
            )
            conn.commit()

    def get(self, collection: str, key: str) -> dict[str, Any] | None:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value_json FROM records WHERE collection = ? AND key = ?",
                (collection, key),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row["value_json"])
            return None

    def set(self, collection: str, key: str, value: dict[str, Any]) -> None:
        import time
        val_str = json.dumps(value, default=str, ensure_ascii=False)
        now = time.time()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO records (collection, key, value_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(collection, key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (collection, key, val_str, now),
            )
            conn.commit()

    def list(self, collection: str) -> list[dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value_json FROM records WHERE collection = ? ORDER BY updated_at DESC",
                (collection,),
            )
            return [json.loads(row["value_json"]) for row in cursor.fetchall()]

    def delete(self, collection: str, key: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM records WHERE collection = ? AND key = ?",
                (collection, key),
            )
            conn.commit()
            return cursor.rowcount > 0

