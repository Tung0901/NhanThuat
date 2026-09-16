"""
Test suite for Temporary Authentication Mechanism & Treatise-Style Situation Overview.
"""

import json
from unittest.mock import MagicMock

from backend.app.main import _ACTIVE_SESSIONS, BusinessOSGatewayHandler
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer


def test_situation_overview_prompt_contains_argumentative_treatise_guidelines():
    """Verify that the synthesizer prompt explicitly guides the LLM to write an argumentative strategic essay."""
    synthesizer = KnowledgeSynthesizer()
    prompt = synthesizer._build_prompt("Nhân sự cấp dưới chống đối ngầm", [])
    assert "TỔNG QUAN TÌNH THẾ" in prompt
    assert "BÀI NGHỊ LUẬN CHIẾN LƯỢC SÂU SẮC, TRAU CHUỐT" in prompt
    assert "Luận đề thế trận" in prompt
    assert "Biện giải chiều sâu" in prompt
    assert "Luận kết & Tâm thế định cục" in prompt


def test_deterministic_situation_overview_treatise_depth():
    """Verify that deterministic synthesis generates an in-depth, multi-paragraph argumentative essay."""
    engine = KnowledgeEngine()
    units = [KnowledgeUnit.from_mapping(iu.raw_data, source_path=None) for iu in list(engine.units_by_id.values())[:3]]

    synthesizer = KnowledgeSynthesizer()
    result = synthesizer.synthesize("Đối tác đòi hủy hợp đồng và đe dọa khởi kiện", units)
    text = result["synthesis"]

    assert "### 👁️ TỔNG QUAN TÌNH THẾ" in text
    # Extract the situation overview section
    parts = text.split("### 👁️ TỔNG QUAN TÌNH THẾ")
    assert len(parts) >= 2
    overview_content = parts[1].split("### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM")[0].strip()

    # The overview should be multi-paragraph, substantive, not a mere 2-sentence stub
    paragraphs = [p.strip() for p in overview_content.split("\n\n") if p.strip()]
    assert len(paragraphs) >= 3, f"Expected at least 3 paragraphs, got {len(paragraphs)}"
    assert "Lợi ích cốt lõi" in overview_content
    assert "Cấu trúc quyền hạn" in overview_content
    assert "Tâm Trai" in overview_content
    assert len(overview_content) > 400


def test_auth_login_and_session_endpoints():
    """Test the temporary authentication endpoints in BusinessOSGatewayHandler."""
    # 1. Test Login with executive credentials
    _ACTIVE_SESSIONS.clear()

    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler.headers = {"Content-Length": "0"}
    handler._send_json_response = MagicMock()

    # Simulate POST /api/v1/auth/login
    handler.path = "/api/v1/auth/login"
    handler.rfile = MagicMock()

    # Login as admin
    login_body = json.dumps({"username": "admin", "password": "nhanthuat2026"}).encode("utf-8")
    handler.headers = {"Content-Length": str(len(login_body))}
    handler.rfile.read = MagicMock(return_value=login_body)

    handler.do_POST()

    assert handler._send_json_response.called
    status_code, data = handler._send_json_response.call_args[0]
    assert status_code == 200
    assert data["status"] == "success"
    token = data["session"]["token"]
    assert token.startswith("NT-SESSION-")
    assert data["session"]["role"] == "EXECUTIVE"
    assert token in _ACTIVE_SESSIONS

    # 2. Test GET /api/v1/auth/session with valid token
    handler.path = "/api/v1/auth/session"
    handler.headers = {"Authorization": f"Bearer {token}"}
    handler.do_GET()

    status_code, session_data = handler._send_json_response.call_args[0]
    assert status_code == 200
    assert session_data["status"] == "success"
    assert session_data["authenticated"] is True
    assert session_data["session"]["token"] == token

    # 3. Test GET /api/v1/auth/session with invalid token
    handler.path = "/api/v1/auth/session"
    handler.headers = {"Authorization": "Bearer INVALID-TOKEN"}
    handler.do_GET()

    status_code, err_data = handler._send_json_response.call_args[0]
    assert status_code == 401
    assert err_data["authenticated"] is False

    # 4. Test POST /api/v1/auth/logout
    handler.path = "/api/v1/auth/logout"
    handler.headers = {"Authorization": f"Bearer {token}", "Content-Length": "0"}
    handler.rfile.read = MagicMock(return_value=b"{}")
    handler.do_POST()

    status_code, _logout_data = handler._send_json_response.call_args[0]
    assert status_code == 200
    assert token not in _ACTIVE_SESSIONS


def test_auth_quick_login_roles():
    """Test quick login by role without password."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler.rfile = MagicMock()
    handler._send_json_response = MagicMock()
    handler.path = "/api/v1/auth/login"

    for role, expected_role in [("EXECUTIVE", "EXECUTIVE"), ("ADVISOR", "ADVISOR"), ("GUEST", "GUEST")]:
        body = json.dumps({"role": role}).encode("utf-8")
        handler.headers = {"Content-Length": str(len(body))}
        handler.rfile.read = MagicMock(return_value=body)
        handler.do_POST()

        status_code, data = handler._send_json_response.call_args[0]
        assert status_code == 200
        assert data["session"]["role"] == expected_role
