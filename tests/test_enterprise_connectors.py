"""
Unit tests for Enterprise Webhook Connectors & Executive Whisper Bot.
Module: tests/test_enterprise_connectors.py
"""

from modules.connectors.webhook_connector import EnterpriseWebhookConnector


def test_parse_slack_webhook():
    connector = EnterpriseWebhookConnector()
    slack_data = {
        "event": {
            "user": "U12345",
            "text": "Tôi quá tải công việc, không thể tiếp tục đảm nhận thêm dự án này nữa.",
            "channel": "C998877",
        }
    }
    parsed = connector.parse_webhook("slack", slack_data)
    assert parsed.source == "slack"
    assert parsed.author_id == "U12345"
    assert "quá tải" in parsed.content
    assert parsed.channel_or_context == "C998877"


def test_parse_teams_webhook():
    connector = EnterpriseWebhookConnector()
    teams_data = {
        "from": {"id": "TEAMS_USER_99"},
        "text": "Cần chốt mục tiêu và hoàn thành dứt điểm trước 17h.",
        "conversation": {"id": "CONV_1122"},
    }
    parsed = connector.parse_webhook("teams", teams_data)
    assert parsed.source == "teams"
    assert parsed.author_id == "TEAMS_USER_99"
    assert "chốt mục tiêu" in parsed.content


def test_parse_hris_webhook():
    connector = EnterpriseWebhookConnector()
    hris_data = {
        "employee_id": "EMP-HRIS-01",
        "notes": "Nhân viên liên tục nộp đơn xin nghỉ phép đột xuất do kiệt sức.",
        "department": "Engineering",
    }
    parsed = connector.parse_webhook("hris", hris_data)
    assert parsed.source == "hris"
    assert parsed.author_id == "EMP-HRIS-01"
    assert parsed.channel_or_context == "Engineering"


def test_process_incoming_webhook_critical_burnout():
    connector = EnterpriseWebhookConnector()
    raw_slack = {
        "event": {
            "user": "EMP-BURNOUT-SLACK",
            "text": "Tôi đang quá tải và kiệt sức nghiêm trọng với khối lượng công việc này, áp lực liên tục mệt mỏi cùng cực.",
            "channel": "C-GENERAL",
        }
    }

    brief = connector.process_incoming_webhook(
        source="slack",
        raw_data=raw_slack,
        task_context="Release phiên bản cổng thanh toán",
    )

    assert brief.brief_id.startswith("WHISPER-")
    assert brief.source == "slack"
    assert brief.author_id == "EMP-BURNOUT-SLACK"
    assert brief.urgency_level == "CRITICAL"
    assert "CRITICAL" in brief.headline
    assert "CÓ" in brief.behavioral_summary
    assert "NT-MODEL-0008" in brief.load_risk_warning

    # Check Slack blocks
    assert len(brief.slack_blocks) >= 3
    assert brief.slack_blocks[0]["type"] == "header"
    assert "Cố Vấn Bí Mật" in brief.slack_blocks[0]["text"]["text"]

    # Check Teams card
    assert brief.teams_adaptive_card["type"] == "AdaptiveCard"
    assert len(brief.teams_adaptive_card["body"]) >= 4

    assert len(connector.history) == 1


def test_connectors_http_endpoints():
    """Test HTTP API endpoints for Enterprise Connectors and Whisper Bot."""
    import json
    from io import BytesIO
    from unittest.mock import MagicMock

    from backend.app.main import BusinessOSGatewayHandler

    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # 1. POST /api/v1/connectors/webhook/slack
    webhook_payload = json.dumps({
        "source": "slack",
        "payload": {
            "event": {
                "user": "U-HTTP-TEST",
                "text": "Công việc ngập đầu, tôi quá tải không thở nổi với tiến độ này.",
                "channel": "C-EXEC",
            }
        },
        "task_context": "Dự án chuyển đổi số",
    }).encode("utf-8")

    handler.path = "/api/v1/connectors/webhook/slack"
    handler.headers = {"Content-Length": str(len(webhook_payload))}
    handler.rfile = BytesIO(webhook_payload)
    handler.do_POST()

    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "brief" in data
    assert data["brief"]["source"] == "slack"
    assert data["brief"]["author_id"] == "U-HTTP-TEST"

    # 2. GET /api/v1/connectors/whispers
    handler._send_json_response.reset_mock()
    handler.path = "/api/v1/connectors/whispers"
    handler.headers = {}
    handler.do_GET()

    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["total"] >= 1
    assert len(data["whispers"]) >= 1

