"""
Unit and integration tests for Nhan Thuat 2.0 UI components & backend endpoints.
Verifies:
1. Frontend delivery (/app) contains all 2.0 DOM elements.
2. War Room 2.0 Faction Alliances & Socratic Debate endpoints.
3. Continuous Profiler & Flight Risk Radar endpoints.
4. Enterprise Connectors & Executive Whisper Bot endpoints.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from backend.app.main import BusinessOSGatewayHandler, continuous_profiler, enterprise_connector, war_room_engine


def test_frontend_delivery_contains_all_2_0_components():
    """Verify frontend/app.html serves all 2.0 visual elements."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_html_response = MagicMock()

    handler._handle_static_or_page("/app")
    assert handler._send_html_response.called
    code, html = handler._send_html_response.call_args[0]
    assert code == 200

    # 1. Executive Whisper Bot elements
    assert "whisper-inbox-top-btn" in html
    assert "whisper-modal-backdrop" in html
    assert "whisper-feed-list" in html
    assert "webhook-source-select" in html

    # 2. Flight Risk Radar elements
    assert "tab-btn-radar-fit" in html
    assert "diag-subview-radar" in html
    assert "radar-roster-list" in html
    assert "radar-detail-panel" in html
    assert "stream-content-input" in html

    # 3. War Room 2.0 Alliances & Socratic Debate elements
    assert "war-alliances-toggle-btn" in html
    assert "war-alliances-card" in html
    assert "war-socratic-btn" in html
    assert "socratic-modal-backdrop" in html
    assert "socratic-rounds-grid" in html
    assert "socratic-synthesis-content" in html


def test_war_room_2_0_alliances_and_debate_api():
    """Verify /api/v1/war-room/alliances and /api/v1/war-room/socratic-debate."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # Create active session
    session = war_room_engine.create_session("Mâu thuẫn phân chia quyền lực giữa phe cựu trào và phe đổi mới")
    session_id = session.session_id

    # 1. Test Alliances GET
    from urllib.parse import urlparse
    parsed = urlparse(f"/api/v1/war-room/alliances?session_id={session_id}")
    handler._handle_get_api("/api/v1/war-room/alliances", parsed)

    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "faction_analysis" in data
    assert "dominant_faction" in data
    assert "friction_index" in data

    # 2. Test Socratic Debate POST
    handler._send_json_response.reset_mock()
    handler._handle_post_api(
        "/api/v1/war-room/socratic-debate",
        {
            "scenario": "Xung đột lợi ích cấp bách giữa các cổ đông chiến lược",
            "session_id": session_id,
        },
    )
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert len(data["rounds"]) >= 4
    assert "executive_synthesis" in data
    assert "Cương Nhu Tương Tế" in data["executive_synthesis"]


def test_behavioral_radar_and_stream_api():
    """Verify /api/v1/behavioral/radar and /api/v1/behavioral/analyze-stream."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # 1. Test Radar GET
    from urllib.parse import urlparse
    parsed = urlparse("/api/v1/behavioral/radar")
    handler._handle_get_api("/api/v1/behavioral/radar", parsed)

    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["total_monitored"] >= 4
    assert len(data["profiles"]) >= 4

    # 2. Test Stream POST
    handler._send_json_response.reset_mock()
    handler._handle_post_api(
        "/api/v1/behavioral/analyze-stream",
        {
            "author_id": "EMP-STREAM-TEST",
            "content": "Tôi quá mệt mỏi với quy trình rườm rà này rồi, không thể chịu nổi nữa!",
            "context_clarity": 0.4,
            "context_constraints": 0.3,
        },
    )
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["profile"]["author_id"] == "EMP-STREAM-TEST"
    assert "flight_risk_score" in data["profile"]
    assert "under_load_forecast" in data["profile"]


def test_enterprise_whisper_and_webhook_api():
    """Verify /api/v1/connectors/whispers and /api/v1/connectors/webhook."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # 1. Test Whispers GET
    from urllib.parse import urlparse
    parsed = urlparse("/api/v1/connectors/whispers")
    handler._handle_get_api("/api/v1/connectors/whispers", parsed)

    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["total"] >= 2
    assert len(data["whispers"]) >= 2

    # 2. Test Webhook POST
    handler._send_json_response.reset_mock()
    handler._handle_post_api(
        "/api/v1/connectors/webhook",
        {
            "channel": "slack",
            "event": {
                "user": "EMP-WEBHOOK-TEST",
                "text": "Chúng tôi cần họp khẩn cấp để xử lý khủng hoảng truyền thông ngay trong hôm nay.",
            },
        },
    )
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "whisper_brief" in data
    assert data["whisper_brief"]["author_id"] == "EMP-WEBHOOK-TEST"
