"""Unit and Integration tests for Team Structural Fit diagnostic module.

Covers NT-PRINCIPLE-0066 (Structural Fit), NT-MODEL-0009 (Emergent Interaction),
and NT-ANTI-PATTERN-0011 (Homogeneity Trap).
"""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock

import pytest

from backend.app.engine.nhan_thuat_api import diagnose_team_structural_fit
from backend.app.main import BusinessOSGatewayHandler


def test_diagnose_team_structural_fit_homogeneity_trap():
    payload = {
        "candidate": {
            "name": "Lê Văn An",
            "role": "Thành viên Ban Chiến Lược",
            "traits": ["Ngại xung đột trực diện", "Thích hòa hoãn dĩ hòa", "Kỷ luật quy trình chi tiết"]
        },
        "team": {
            "name": "Ban Điều Hành",
            "mission": "Ổn định vận hành",
            "traits": ["Kỷ luật quy trình nghiêm ngặt", "Giám sát số liệu chi tiết", "Ngại xung đột trực diện"]
        }
    }

    result = diagnose_team_structural_fit(payload)
    assert result["status"] == "success"
    assert result["candidate_name"] == "Lê Văn An"
    assert result["team_name"] == "Ban Điều Hành"
    assert result["homogeneity_risk_score"] >= 70
    assert "Bẫy Đồng Nhất" in result["structural_alignment_level"]
    assert len(result["systemic_blind_spots"]) > 0
    assert any("Devil's Advocate" in d or "đối nghịch" in d for d in result["structural_directives"])
    
    cited_ids = [u["id"] for u in result["cited_units"]]
    assert "NT-ANTI-PATTERN-0011" in cited_ids
    assert "NT-PRINCIPLE-0066" in cited_ids


def test_diagnose_team_structural_fit_power_conflict():
    payload = {
        "candidate": {
            "name": "Nguyễn Hùng Dũng",
            "role": "Phó Tổng Giám Đốc",
            "traits": ["Quyết đoán nhanh", "Tham vọng quyền lực"]
        },
        "team": {
            "name": "Ban Giám Đốc Hiện Tại",
            "mission": "Kiểm soát mở rộng",
            "traits": ["Quyết đoán áp đặt", "Tham vọng quyền lực cao"]
        }
    }

    result = diagnose_team_structural_fit(payload)
    assert result["status"] == "success"
    assert "Xung Đột" in result["structural_alignment_level"]
    assert len(result["emergent_frictions"]) > 0
    assert any("Lễ Định Phần" in d for d in result["structural_directives"])


def test_diagnose_team_structural_fit_complementary():
    payload = {
        "candidate": {
            "name": "Hoàng Minh Trí",
            "role": "Giám Đốc Đổi Mới Sáng Tạo",
            "traits": ["Tự do sáng tạo", "Tư duy cơ hội bứt phá"]
        },
        "team": {
            "name": "Khối Vận Hành Cốt Lõi",
            "mission": "Chuẩn hóa quy trình sản xuất",
            "traits": ["Kỷ luật quy trình nghiêm ngặt", "Giám sát số liệu chi tiết"]
        }
    }

    result = diagnose_team_structural_fit(payload)
    assert result["status"] == "success"
    assert result["diversity_score"] >= 70
    assert "Khớp Cấu Trúc Bổ Trợ" in result["structural_alignment_level"]
    assert any("Tương Thuộc Bắt Buộc" in d or "NT-PRINCIPLE-0071" in d for d in result["structural_directives"])


def test_team_structural_fit_gateway_integration():
    """Verify HTTP POST to /api/v1/diagnostics/team-structural-fit returns HTTP 200 with JSON payload."""
    payload = {
        "candidate": {
            "name": "Đặng Quốc Bảo",
            "role": "Trưởng Phòng R&D",
            "traits": ["Tự do sáng tạo"]
        },
        "team": {
            "name": "Nhóm Kỹ Thuật",
            "mission": "Phát triển công nghệ",
            "traits": ["Kỷ luật quy trình chi tiết"]
        }
    }
    body = json.dumps(payload).encode("utf-8")

    handler = object.__new__(BusinessOSGatewayHandler)
    handler.path = "/api/v1/diagnostics/team-structural-fit"
    handler.headers = {
        "Content-Length": str(len(body)),
        "Content-Type": "application/json",
    }
    handler.rfile = BytesIO(body)
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.wfile = BytesIO()

    handler.do_POST()

    handler.send_response.assert_called_with(200)
    response_data = json.loads(handler.wfile.getvalue().decode("utf-8"))
    assert response_data["status"] == "success"
    assert response_data["candidate_name"] == "Đặng Quốc Bảo"
    assert "structural_alignment_level" in response_data
    assert "diversity_score" in response_data
    assert "homogeneity_risk_score" in response_data
