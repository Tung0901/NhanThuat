"""
Security regression tests for Sparring API authentication, session ownership (IDOR prevention),
SQLite backward-compatible schema migration, and Stored XSS neutralization in exports.
"""

from __future__ import annotations

import io
import json
import sqlite3
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from nhan_thuat.engine.sparring_engine import SparringEngine
from nhan_thuat.export.executive_brief import ExecutiveBriefExporter
from nhan_thuat.storage.db import DatabaseManager
from nhan_thuat.storage.models import SparringMessage, SparringSession


@pytest.fixture
def sparring_security_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from backend.app import main

    isolated_db = DatabaseManager(db_path=tmp_path / "test_sparring_sec.db")
    isolated_sparring = SparringEngine(
        db_manager=isolated_db,
        knowledge_engine=main.knowledge_engine,
    )
    monkeypatch.setattr(main, "db_manager", isolated_db)
    monkeypatch.setattr(main, "sparring_engine", isolated_sparring)

    session_a = main.auth_manager.create_session(
        {"name": "User A", "role": "ADVISOR", "avatar": "A"},
        "user-a",
        custom_ttl=120,
    )
    session_b = main.auth_manager.create_session(
        {"name": "User B", "role": "EXECUTIVE", "avatar": "B"},
        "user-b",
        custom_ttl=120,
    )
    session_admin = main.auth_manager.create_session(
        {"name": "System Admin", "role": "EXECUTIVE", "avatar": "AD"},
        "admin",
        custom_ttl=120,
    )

    def call_api(
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        token: str | None = None,
    ) -> tuple[int, Any]:
        handler = main.BusinessOSGatewayHandler.__new__(main.BusinessOSGatewayHandler)
        handler.path = path
        body = json.dumps(payload or {}).encode("utf-8")
        handler.rfile = io.BytesIO(body)
        handler.headers = {
            "Content-Length": str(len(body)),
            "Authorization": f"Bearer {token}" if token else "",
        }
        handler._send_json_response = MagicMock()
        handler._send_html_response = MagicMock()
        getattr(handler, f"do_{method}")()
        if handler._send_json_response.called:
            return handler._send_json_response.call_args.args
        if handler._send_html_response.called:
            return handler._send_html_response.call_args.args
        raise AssertionError("No response sent by handler")

    yield call_api, isolated_db, session_a, session_b, session_admin

    main.auth_manager.revoke_session(session_a["token"])
    main.auth_manager.revoke_session(session_b["token"])
    main.auth_manager.revoke_session(session_admin["token"])


def test_sparring_endpoints_require_authentication(sparring_security_env) -> None:
    call_api, _, session_a, _, _ = sparring_security_env

    # Create a valid session as user A first so we have a real session ID to test against
    code, created = call_api(
        "POST",
        "/api/v1/sparring/sessions",
        {"title": "Phiên của User A", "philosophy_lens": "LEGALISM"},
        token=session_a["token"],
    )
    assert code == 201
    session_id = created["session"]["id"]

    # All 5 endpoints must reject unauthenticated requests with 401
    assert call_api("POST", "/api/v1/sparring/sessions", {"title": "Unauth"})[0] == 401
    assert (
        call_api(
            "POST",
            "/api/v1/sparring/messages",
            {"session_id": session_id, "message": "Hello"},
        )[0]
        == 401
    )
    assert call_api("GET", "/api/v1/sparring/sessions")[0] == 401
    assert call_api("GET", f"/api/v1/sparring/sessions/{session_id}")[0] == 401
    assert call_api("GET", f"/api/v1/sparring/sessions/{session_id}/export")[0] == 401
    assert (
        call_api("GET", f"/api/v1/sparring/sessions/{session_id}/export?format=markdown")[0]
        == 401
    )


def test_sparring_ownership_prevents_cross_user_idor(sparring_security_env) -> None:
    call_api, _, session_a, session_b, session_admin = sparring_security_env

    # User A creates a sparring session
    code, created = call_api(
        "POST",
        "/api/v1/sparring/sessions",
        {
            "title": "Đàm phán chiến lược của User A",
            "philosophy_lens": "LEGALISM",
            "initial_context": "Bối cảnh bảo mật riêng của User A.",
        },
        token=session_a["token"],
    )
    assert code == 201
    session_id = created["session"]["id"]
    assert created["session"]["owner_id"] == "user-a"

    # User B cannot read User A's session by ID (403)
    code, err = call_api(
        "GET", f"/api/v1/sparring/sessions/{session_id}", token=session_b["token"]
    )
    assert code == 403
    assert err["status"] == "error"

    # User B cannot post messages into User A's session (403)
    code, err = call_api(
        "POST",
        "/api/v1/sparring/messages",
        {"session_id": session_id, "message": "User B chèn tin nhắn trái phép"},
        token=session_b["token"],
    )
    assert code == 403

    # User B cannot export User A's session in HTML or Markdown (403)
    assert (
        call_api(
            "GET",
            f"/api/v1/sparring/sessions/{session_id}/export?format=html",
            token=session_b["token"],
        )[0]
        == 403
    )
    assert (
        call_api(
            "GET",
            f"/api/v1/sparring/sessions/{session_id}/export?format=markdown",
            token=session_b["token"],
        )[0]
        == 403
    )

    # User B listing sessions only sees User B's sessions (0), never User A's
    code, list_b = call_api("GET", "/api/v1/sparring/sessions", token=session_b["token"])
    assert code == 200
    assert list_b["count"] == 0
    assert list_b["sessions"] == []

    # Owner (User A) can read, post messages, list, and export their own session
    code, list_a = call_api("GET", "/api/v1/sparring/sessions", token=session_a["token"])
    assert code == 200
    assert list_a["count"] == 1
    assert list_a["sessions"][0]["id"] == session_id

    code, turn_a = call_api(
        "POST",
        "/api/v1/sparring/messages",
        {"session_id": session_id, "message": "Lập luận hợp lệ của chủ sở hữu."},
        token=session_a["token"],
    )
    assert code == 200
    assert turn_a["status"] == "success"

    code, detail_a = call_api(
        "GET", f"/api/v1/sparring/sessions/{session_id}", token=session_a["token"]
    )
    assert code == 200
    assert detail_a["session"]["id"] == session_id
    assert len(detail_a["messages"]) >= 2

    code, html_a = call_api(
        "GET",
        f"/api/v1/sparring/sessions/{session_id}/export?format=html",
        token=session_a["token"],
    )
    assert code == 200
    assert "<!DOCTYPE html>" in html_a

    # Explicit Admin account can inspect/audit the session
    code, detail_admin = call_api(
        "GET", f"/api/v1/sparring/sessions/{session_id}", token=session_admin["token"]
    )
    assert code == 200
    assert detail_admin["session"]["id"] == session_id


def test_sqlite_legacy_sparring_schema_migration_backward_compatibility(
    tmp_path: Path,
) -> None:
    db_file = tmp_path / "legacy_sparring.db"
    conn = sqlite3.connect(str(db_file))
    conn.execute(
        """
        CREATE TABLE sparring_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            philosophy_lens TEXT NOT NULL DEFAULT 'auto',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            summary TEXT NOT NULL DEFAULT '',
            metadata TEXT NOT NULL DEFAULT '{}'
        );
        """
    )
    conn.execute(
        """
        INSERT INTO sparring_sessions (id, title, status, philosophy_lens, created_at, updated_at, summary, metadata)
        VALUES ('SPAR-LEGACY-01', 'Legacy Session', 'active', 'LEGALISM', '2026-01-01T00:00:00Z', '2026-01-01T00:00:00Z', '', '{}')
        """
    )
    conn.commit()
    conn.close()

    # Initializing DatabaseManager on legacy DB must migrate owner_id safely
    migrated_db = DatabaseManager(db_path=db_file)
    legacy = migrated_db.get_session("SPAR-LEGACY-01")
    assert legacy is not None
    assert legacy.owner_id == "system"

    # Regular user listing sessions does not see unowned 'system' legacy sessions
    assert migrated_db.list_sessions(owner_id="user-a") == []
    assert len(migrated_db.list_sessions()) == 1


def test_sparring_export_escapes_stored_xss_in_html_and_markdown(
    sparring_security_env,
) -> None:
    call_api, _, session_a, _, _ = sparring_security_env
    exporter = ExecutiveBriefExporter()
    xss_session = SparringSession(
        id='SPAR-XSS-1"><script>alert("id")</script>',
        title='<script>alert("title")</script><img src=x onerror="alert(1)">',
        status="active",
        philosophy_lens='LEGALISM"><svg onload=alert(2)>',
        created_at='2026-10-19"><script>alert("date")</script>',
        summary="",
        metadata={
            "persona_label": '<b onmouseover="alert(3)">Đối thủ độc hại</b>',
            "opening_challenge": '<script>alert("meta")</script>',
            "resolved_lens": '<iframe src="javascript:alert(4)"></iframe>',
        },
        owner_id="user-a",
    )
    xss_messages = [
        SparringMessage(
            id="MSG-1",
            session_id=xss_session.id,
            role="user",
            content='Dòng 1: <script>alert("msg1")</script>\nDòng 2: <a href="javascript:alert(5)" onclick="evil()">Click</a>',
            matched_unit_ids=['NT-LAW-0001"><script>alert("unit")</script>'],
            created_at='2026-10-19T01:00:00Z"><img src=x onerror=alert(6)>',
        ),
        SparringMessage(
            id="MSG-2",
            session_id=xss_session.id,
            role="assistant",
            content='Phản hồi dòng 1\nPhản hồi dòng 2 <img src=x onerror="stealCookie()">',
            matched_unit_ids=[],
            created_at="2026-10-19T01:01:00Z",
        ),
    ]

    html_out = exporter.export_sparring_session(xss_session, xss_messages, format="html")
    md_out = exporter.export_sparring_session(xss_session, xss_messages, format="markdown")

    for rendered in (html_out, md_out):
        assert "<script>" not in rendered
        assert "</script>" not in rendered
        assert "<img" not in rendered
        assert "<svg" not in rendered
        assert "<iframe" not in rendered
        assert 'onerror="alert(1)"' not in rendered
        assert 'onmouseover="alert(3)"' not in rendered
        assert 'onclick="evil()"' not in rendered
        assert "&lt;script&gt;" in rendered
        assert "&lt;img src=x onerror=alert(6)&gt;" in rendered

    # Verify line breaks and pre-wrap styling are preserved in HTML transcript
    assert "white-space:pre-wrap" in html_out or "white-space: pre-wrap" in html_out
    assert "Dòng 1: &lt;script&gt;alert(&quot;msg1&quot;)&lt;/script&gt;\nDòng 2:" in html_out
    assert "Phản hồi dòng 1\nPhản hồi dòng 2" in html_out
    assert "Đối thủ độc hại" in html_out
    assert "Đối thủ độc hại" in md_out

    # Also test end-to-end via HTTP API export endpoints
    code, created = call_api(
        "POST",
        "/api/v1/sparring/sessions",
        {
            "title": '<script>alert("xss-title")</script>',
            "philosophy_lens": 'LEGALISM"><img src=x onerror=alert(9)>',
            "initial_context": 'Bối cảnh dòng 1\nBối cảnh dòng 2 <svg onload="alert(8)">',
            "metadata": {
                "opponent_opening": '<script>alert("xss-opening")</script>',
            },
        },
        token=session_a["token"],
    )
    assert code == 201
    api_sess_id = created["session"]["id"]

    code, _ = call_api(
        "POST",
        "/api/v1/sparring/messages",
        {
            "session_id": api_sess_id,
            "message": 'Phản biện dòng 1\nPhản biện dòng 2 <img src=x onerror="evil()">',
        },
        token=session_a["token"],
    )
    assert code == 200

    code, api_html = call_api(
        "GET",
        f"/api/v1/sparring/sessions/{api_sess_id}/export?format=html",
        token=session_a["token"],
    )
    assert code == 200
    assert "<script>" not in api_html
    assert 'onerror="evil()"' not in api_html
    assert 'onload="alert(8)"' not in api_html
    assert "&lt;script&gt;alert(&quot;xss-title&quot;)&lt;/script&gt;" in api_html
    assert "Phản biện dòng 1\nPhản biện dòng 2" in api_html

    code, api_md = call_api(
        "GET",
        f"/api/v1/sparring/sessions/{api_sess_id}/export?format=markdown",
        token=session_a["token"],
    )
    assert code == 200
    assert "<script>" not in api_md["content"]
    assert 'onerror="evil()"' not in api_md["content"]
    assert "&lt;script&gt;alert(&quot;xss-title&quot;)&lt;/script&gt;" in api_md["content"]
