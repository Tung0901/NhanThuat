"""
Unit and integration tests for Nhan Thuat 2.0 UI components & backend endpoints.
Verifies:
1. Frontend delivery (/app) contains all 2.0 DOM elements.
2. War Room 2.0 Faction Alliances & Socratic Debate endpoints.
3. Continuous Profiler & Flight Risk Radar endpoints.
4. Enterprise Connectors & Executive Whisper Bot endpoints.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from backend.app.main import BusinessOSGatewayHandler, war_room_engine


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


def test_home_embeds_scroll_native_app_and_legacy_routes_open_app_mode():
    """Homepage keeps its story and embeds the app; legacy routes open app mode."""
    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_html_response = MagicMock()
    rendered: dict[str, str] = {}

    for path in ("/", "/index.html", "/app", "/dashboard"):
        handler._send_html_response.reset_mock()
        assert handler._handle_static_or_page(path) is True
        code, html = handler._send_html_response.call_args[0]
        assert code == 200
        rendered[path] = html

    assert rendered["/"] == rendered["/index.html"]
    assert rendered["/app"] == rendered["/dashboard"]
    assert '<body class="home-entry">' in rendered["/"]
    assert '<body class="app-entry">' in rendered["/app"]

    for html in rendered.values():
        assert 'id="landing-page-wrapper"' in html
        assert 'id="application-start"' in html
        assert 'id="hero-advisory-input"' in html
        assert "initScrollNativeWorkspace" in html
        assert "core-app-wrapper" not in html
        assert "function enterApp" in html
        assert 'href="#application-start"' in html
        assert 'id="knowledge"' not in html
        assert "terminal-container" not in html
        assert 'id="terminal-input"' not in html
        assert 'id="terminal-output"' not in html
        assert 'id="loginOverlay"' not in html
        assert 'class="strategy-method"' in html
        assert "horizontal-scroll-container" not in html
        assert "horizontal-scroll-wrapper" not in html
        assert "const horizontalContainer" not in html
        assert "closing-statement" in html
        assert 'class="landing-nav"' in html
        assert 'class="landing-nav-link"' in html
        assert "mix-blend-difference" not in html
        assert "--type-ui: 13px" in html
        assert "--type-body: 15px" in html
        assert "scroll-margin-top: 56px" in html
        assert 'id="scenario-workspace"' in html
        assert 'href="/css/scenario-workspace.css"' in html
        assert 'src="/js/scenario-workspace.js"' in html

        for image_name in (
            "behavioral-intelligence.webp",
            "multi-lens-council.webp",
            "negotiation-signals.webp",
            "power-map.webp",
        ):
            assert f'/assets/landing/{image_name}' in html

        assert "photo-1507413245164-6160d8298b31" not in html
        assert "photo-1529699211952-734e80c4d42b" not in html
        assert "photo-1506544777-64cfbe1142df" not in html
        assert "photo-1574510005727-414841dc30c1" not in html

    assert "body.home-entry .workspace-module > .cockpit-layout" in rendered["/"]
    assert "#philosophy .pillar-media" in rendered["/"]
    assert ".workspace-viewport > #view-war-room { order: 5; }" in rendered["/"]
    assert ".workspace-viewport > #view-codex { order: 6; }" in rendered["/"]
    assert rendered["/"].index("Sa bàn tình thế</button>") < rendered["/"].index("Nguồn tham khảo</button>")


def test_scenario_workspace_is_single_session_scoped_draft():
    """Scenario spine stays tab-scoped and keeps inference separate from facts."""
    script = Path("frontend/js/scenario-workspace.js").read_text(encoding="utf-8")
    styles = Path("frontend/css/scenario-workspace.css").read_text(encoding="utf-8")

    assert "sessionStorage.getItem(STORAGE_KEY)" in script
    assert "sessionStorage.setItem(STORAGE_KEY" in script
    assert "localStorage" not in script
    assert "engine_inference: 'Kết quả: suy luận của hệ thống'" in script
    assert "simulation: 'Kết quả: mô phỏng'" in script
    assert "/api/v1/cases" not in script
    assert "html.scenario-active .workspace-module" in styles


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
