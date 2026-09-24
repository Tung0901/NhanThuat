"""
Unit tests for War Room 2.0 Engine Extensions:
- calculate_faction_alliances
- deliberate_socratic_debate
"""

import pytest

from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.runtime.war_room import WarRoomEngine


@pytest.fixture
def war_room_engine():
    ke = KnowledgeEngine()
    return WarRoomEngine(knowledge_engine=ke)


def test_war_room_2_faction_alliances(war_room_engine):
    session = war_room_engine.initialize_session("Tranh chấp nguồn vốn và ngân sách các khối")
    assert session.personas

    alliances = war_room_engine.calculate_faction_alliances(session)
    assert alliances["status"] == "success"
    assert alliances["session_id"] == session.session_id
    assert alliances["total_factions"] >= 1
    assert 0.0 <= alliances["friction_index"] <= 1.0
    assert alliances["dominant_faction"] != "None"

    # Check faction analysis structure
    for data in alliances["faction_analysis"].values():
        assert data["member_count"] > 0
        assert data["power_share_pct"] >= 0.0
        assert 0.0 <= data["average_loyalty"] <= 100.0
        assert 0.0 <= data["average_stress"] <= 100.0
        assert 0 <= data["cohesion_score"] <= 100
        assert 0.0 <= data["betrayal_risk_pct"] <= 100.0


def test_war_room_2_socratic_debate(war_room_engine):
    session = war_room_engine.initialize_session("Cắt giảm nhân sự cấp cao")
    dilemma = "Xử lý phó tổng giám đốc vi phạm kỷ luật nhưng có quan hệ với cổ đông lớn"

    debate = war_room_engine.deliberate_socratic_debate(
        session=session,
        dilemma=dilemma,
        philosophies=["legalism", "confucian", "taoism", "sunzi"],
    )

    assert debate["status"] == "success"
    assert debate["dilemma"] == dilemma
    assert len(debate["participating_schools"]) == 4
    assert len(debate["rounds"]) == 4

    for r in debate["rounds"]:
        assert r["school"]
        assert r["thesis"]
        assert r["critique"]
        assert r["recommended_action"]

    assert "executive_synthesis" in debate
    assert "Cương Nhu Tương Tế" in debate["executive_synthesis"]
    assert "Binh Pháp Tôn Tử" in debate["executive_synthesis"]
