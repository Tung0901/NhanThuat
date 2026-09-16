"""
Tests for War Room Sandbox Runtime Engine (Sa Bàn Tình Thế).
Tests session initialization, persona generation, multi-round simulation,
God-mode intervention, and strategic reporting.
"""

import pytest
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.runtime.war_room import WarRoomEngine, WarRoomSession, Persona


@pytest.fixture
def war_room_engine():
    ke = KnowledgeEngine()
    return WarRoomEngine(knowledge_engine=ke)


def test_get_presets(war_room_engine):
    presets = war_room_engine.get_presets()
    assert len(presets) >= 4
    for p in presets:
        assert "id" in p
        assert "title" in p
        assert "category" in p
        assert "default_scenario" in p
        assert len(p["default_scenario"]) > 20


def test_initialize_session_default(war_room_engine):
    session = war_room_engine.initialize_session("Cắt giảm 30% nhân sự để tái cấu trúc")
    assert session.session_id.startswith("WAR-ROOM-")
    assert session.current_round == 0
    assert session.status == "INITIALIZED"
    assert len(session.personas) >= 4

    for persona in session.personas:
        assert persona.id
        assert persona.name
        assert persona.role
        assert persona.faction
        assert persona.core_interest
        assert persona.hidden_fear
        assert persona.stance
        assert 0 <= persona.loyalty_score <= 100
        assert 0 <= persona.stress_level <= 100
        assert 0 <= persona.influence_score <= 100

    # Ensure session retrieval
    retrieved = war_room_engine.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id


def test_initialize_session_custom_personas(war_room_engine):
    custom = [
        {
            "id": "cp_1",
            "name": "Nguyễn Văn A",
            "role": "CEO",
            "faction": "HĐQT",
            "core_interest": "Tăng trưởng",
            "hidden_fear": "Mất vốn",
            "stance": "Quyết liệt",
            "loyalty_score": 95,
            "stress_level": 50,
            "influence_score": 90,
            "avatar": "👑",
        },
        {
            "id": "cp_2",
            "name": "Trần Thị B",
            "role": "CFO",
            "faction": "Tài chính",
            "core_interest": "Dòng tiền an toàn",
            "hidden_fear": "Bị thanh tra",
            "stance": "Kỷ luật",
            "loyalty_score": 85,
            "stress_level": 60,
            "influence_score": 80,
            "avatar": "📊",
        },
        {
            "id": "cp_3",
            "name": "Lê Văn C",
            "role": "CTO",
            "faction": "Kỹ thuật",
            "core_interest": "Độc lập công nghệ",
            "hidden_fear": "Mất nhân sự",
            "stance": "Bảo thủ",
            "loyalty_score": 50,
            "stress_level": 70,
            "influence_score": 75,
            "avatar": "💻",
        },
    ]
    session = war_room_engine.initialize_session("Thử nghiệm tùy biến", custom_personas=custom)
    assert len(session.personas) == 3
    assert session.personas[0].name == "Nguyễn Văn A"


def test_step_round_and_intervention(war_room_engine):
    session = war_room_engine.initialize_session("Phát hiện Giám đốc Kinh doanh bán tệp khách sang đối thủ")
    sid = session.session_id

    # Round 1
    r1 = war_room_engine.step_round(sid)
    assert r1.round_number == 1
    assert "Vòng 1" in r1.stage_name
    assert len(r1.actions) >= 3
    assert session.current_round == 1
    assert session.status == "RUNNING"

    for act in r1.actions:
        assert act.persona_id
        assert act.persona_name
        assert act.public_action
        assert act.private_thought

    # Round 2 with intervention
    intervention_text = "Chủ tịch ban hành chỉ thị phong tỏa tài khoản dữ liệu và mời công an kinh tế vào cuộc"
    r2 = war_room_engine.step_round(sid, intervention=intervention_text)
    assert r2.round_number == 2
    assert "Vòng 2" in r2.stage_name
    assert r2.intervention == intervention_text
    assert len(session.interventions) == 1
    assert session.interventions[0]["text"] == intervention_text


def test_generate_strategic_report(war_room_engine):
    session = war_room_engine.initialize_session("Xung đột quyền lực giữa CTO và Phó TGĐ mới")
    sid = session.session_id

    war_room_engine.step_round(sid)
    war_room_engine.step_round(sid)

    report = war_room_engine.generate_strategic_report(sid)
    assert "executive_summary" in report
    assert "vulnerable_link" in report
    assert "critical_breakdown_point" in report
    assert "factional_matrix" in report
    assert "actionable_strategies" in report
    assert len(report["actionable_strategies"]) >= 3

    for strat in report["actionable_strategies"]:
        assert "name" in strat
        assert "philosophy" in strat
        assert "steps" in strat
        assert len(strat["steps"]) >= 2
        assert "expected_outcome" in strat

    assert session.status == "COMPLETED"
    assert session.report is not None


def test_session_not_found(war_room_engine):
    with pytest.raises(ValueError, match="not found"):
        war_room_engine.step_round("INVALID-SESSION-ID")

    with pytest.raises(ValueError, match="not found"):
        war_room_engine.generate_strategic_report("INVALID-SESSION-ID")


def test_war_room_api_endpoints():
    """Test War Room REST endpoints in BusinessOSGatewayHandler."""
    import json
    from unittest.mock import MagicMock
    from io import BytesIO
    from backend.app.main import BusinessOSGatewayHandler

    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # 1. GET /api/v1/war-room/presets
    handler.path = "/api/v1/war-room/presets"
    handler.do_GET()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert len(data["presets"]) >= 4

    # 2. POST /api/v1/war-room/init
    handler._send_json_response.reset_mock()
    init_payload = json.dumps({"scenario": "Cắt giảm 30% nhân sự toàn công ty"}).encode("utf-8")
    handler.path = "/api/v1/war-room/init"
    handler.headers = {"Content-Length": str(len(init_payload))}
    handler.rfile = BytesIO(init_payload)
    handler.do_POST()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 201
    assert data["status"] == "success"
    session_id = data["session"]["session_id"]
    assert session_id.startswith("WAR-ROOM-")

    # 3. POST /api/v1/war-room/step
    handler._send_json_response.reset_mock()
    step_payload = json.dumps({
        "session_id": session_id,
        "intervention": "Chủ tịch tổ chức họp mặt bí mật với các trưởng phòng",
    }).encode("utf-8")
    handler.path = "/api/v1/war-room/step"
    handler.headers = {"Content-Length": str(len(step_payload))}
    handler.rfile = BytesIO(step_payload)
    handler.do_POST()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["round"]["round_number"] == 1

    # 4. GET /api/v1/war-room/state
    handler._send_json_response.reset_mock()
    handler.path = f"/api/v1/war-room/state?session_id={session_id}"
    handler.do_GET()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["session"]["session_id"] == session_id

    # 5. POST /api/v1/war-room/report
    handler._send_json_response.reset_mock()
    rep_payload = json.dumps({"session_id": session_id}).encode("utf-8")
    handler.path = "/api/v1/war-room/report"
    handler.headers = {"Content-Length": str(len(rep_payload))}
    handler.rfile = BytesIO(rep_payload)
    handler.do_POST()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "executive_summary" in data["report"]

    # 6. POST /api/v1/war-room/interrogate
    handler._send_json_response.reset_mock()
    target_persona_id = data["session"]["personas"][0]["id"]
    int_payload = json.dumps({
        "session_id": session_id,
        "persona_id": target_persona_id,
        "question": "Anh có ý định gì sau lưng Ban Giám Đốc?",
    }).encode("utf-8")
    handler.path = "/api/v1/war-room/interrogate"
    handler.headers = {"Content-Length": str(len(int_payload))}
    handler.rfile = BytesIO(int_payload)
    handler.do_POST()
    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "interrogation" in data
    assert len(data["interrogation"]["answer"]) > 10


def test_network_graph_and_history(war_room_engine):
    """Test interactive graph computation and psychological trajectory tracking."""
    session = war_room_engine.initialize_session("Nghi vấn rò rỉ dữ liệu khách hàng VIP")
    assert "nodes" in session.network_graph
    assert "edges" in session.network_graph
    assert len(session.network_graph["nodes"]) == len(session.personas)

    for p in session.personas:
        assert len(p.loyalty_history) == 1
        assert len(p.stress_history) == 1

    # Advance 2 rounds
    war_room_engine.step_round(session.session_id)
    war_room_engine.step_round(session.session_id)

    for p in session.personas:
        assert len(p.loyalty_history) == 3
        assert len(p.stress_history) == 3

    assert len(session.network_graph["edges"]) >= 1


def test_interrogate_persona_direct(war_room_engine):
    """Test 1-on-1 direct interrogation of a persona."""
    session = war_room_engine.initialize_session("Cắt giảm 30% nhân sự")
    p0 = session.personas[0]
    res = war_room_engine.interrogate_persona(
        session_id=session.session_id,
        persona_id=p0.id,
        question="Nếu tôi tăng 20% lương cho anh, anh có chịu hợp tác dẹp yên khối vận hành không?",
    )
    assert res["persona_id"] == p0.id
    assert res["persona_name"] == p0.name
    assert "answer" in res
    assert "inner_motive" in res
    assert len(res["answer"]) > 15
    assert len(session.interrogation_history) == 1

