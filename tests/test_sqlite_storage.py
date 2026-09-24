"""
Unit tests for SQLiteStorageAdapter in backend.app.engine.storage.
"""

from backend.app.engine.storage import SQLiteStorageAdapter


def test_sqlite_storage_adapter_crud(tmp_path):
    db_file = tmp_path / "test_runtime.db"
    adapter = SQLiteStorageAdapter(db_path=db_file)

    # 1. Test Set and Get
    adapter.set("sessions", "sess_01", {"user": "ceo", "role": "EXECUTIVE"})
    record = adapter.get("sessions", "sess_01")
    assert record is not None
    assert record["user"] == "ceo"
    assert record["role"] == "EXECUTIVE"

    # 2. Test Get Non-existent
    assert adapter.get("sessions", "non_existent") is None

    # 3. Test Update (Upsert)
    adapter.set("sessions", "sess_01", {"user": "ceo", "role": "ADMIN"})
    updated = adapter.get("sessions", "sess_01")
    assert updated["role"] == "ADMIN"

    # 4. Test List
    adapter.set("sessions", "sess_02", {"user": "advisor", "role": "ADVISOR"})
    items = adapter.list("sessions")
    assert len(items) == 2

    # 5. Test Delete
    assert adapter.delete("sessions", "sess_01") is True
    assert adapter.get("sessions", "sess_01") is None
    assert adapter.delete("sessions", "sess_01") is False
    assert len(adapter.list("sessions")) == 1
