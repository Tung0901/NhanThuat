"""
Automated Test Suite for End-to-End BusinessOS & Nhân Thuật Pipeline.
Tests:
1. JevDecisionAdapter (Live vs Mock, Choice/Score/Noul schemas).
2. NhanThuatBehavioralService (Human input ingestion & behavioral event emission).
3. BusinessOSActionRouter (Threshold-based actions P > 0.85, alerts, and DISC formatting).
4. End-to-End integration across all stages.
"""

import pytest

from modules.business_os.router import BusinessOSActionRouter
from modules.decider.adapter import DecisionSchema, JevDecisionAdapter
from modules.nhan_thuat.service import (
    BehavioralEvaluationEvent,
    HumanInputRecord,
    NhanThuatBehavioralService,
)


def test_decider_mock_evaluation_schemas() -> None:
    """Validate that the decider adheres to the schema contract in mock mode."""
    decider = JevDecisionAdapter(mock_mode=True)

    # 1. Noul schema
    noul_res = decider.decide(
        text_state="Nhân viên mệt mỏi, kiệt sức và quá tải",
        schema=DecisionSchema(type="noul"),
    )
    assert noul_res.type == "noul"
    assert isinstance(noul_res.decision, bool)
    assert noul_res.decision is True
    assert 0.0 <= noul_res.confidence <= 1.0

    # 2. Score schema
    score_res = decider.decide(
        text_state="Áp lực công việc bình thường, hoàn thành tốt",
        schema=DecisionSchema(type="score", scale_min=1.0, scale_max=5.0),
    )
    assert score_res.type == "score"
    assert isinstance(score_res.decision, int)
    assert 1 <= score_res.decision <= 5
    assert 0.0 <= score_res.confidence <= 1.0

    # 3. Choice schema (DISC)
    choice_res = decider.decide(
        text_state="Cần chốt ngay kết quả KPI hôm nay để kịp deadline",
        schema=DecisionSchema(type="choice", options=["D", "I", "S", "C"]),
    )
    assert choice_res.type == "choice"
    assert choice_res.decision in ["D", "I", "S", "C"]
    assert choice_res.decision == "D"
    assert choice_res.confidence > 0.85


def test_decider_live_mode_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validate live mode sends expected HTTP request with Bearer authorization."""
    monkeypatch.setenv("TYPESAFE_API_KEY", "ts_live_key_test_54321")

    captured_requests = []

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "decision": "C",
                "confidence": 0.96,
                "type": "choice",
            }

    def fake_post(url: str, **kwargs):
        captured_requests.append({"url": url, "kwargs": kwargs})
        return FakeResponse()

    monkeypatch.setattr("modules.decider.adapter.requests.post", fake_post)

    decider = JevDecisionAdapter()
    assert decider.is_mock is False

    res = decider.decide(
        text_state="Cần đặc tả tiêu chí nghiệm thu và kiểm tra dữ liệu",
        schema=DecisionSchema(type="choice", options=["D", "I", "S", "C"]),
    )

    assert len(captured_requests) == 1
    call = captured_requests[0]
    assert call["kwargs"]["headers"]["Authorization"] == "Bearer ts_live_key_test_54321"
    assert res.decision == "C"
    assert res.confidence == 0.96


def test_nhan_thuat_service_emission() -> None:
    """Validate that NhanThuatBehavioralService queries the 3 core metrics and emits a structured event."""
    service = NhanThuatBehavioralService()
    record = HumanInputRecord(
        content="Báo cáo tiến độ: đã hoàn tất phân tích số liệu và rà soát đặc tả quy trình.",
        author_id="EMP-TEST-01",
        source_type="daily_report",
    )

    event = service.evaluate(record)

    assert isinstance(event, BehavioralEvaluationEvent)
    assert event.author_id == "EMP-TEST-01"
    assert isinstance(event.burnout_risk, bool)
    assert 1 <= event.stress_score <= 5
    assert event.behavior_style in ["D", "I", "S", "C"]
    assert event.behavior_style == "C"
    assert "burnout_risk" in event.raw_decisions
    assert "stress_score" in event.raw_decisions
    assert "behavior_style" in event.raw_decisions


def test_business_os_router_urgent_burnout_alert() -> None:
    """Validate that high stress (>=4) or burnout risk triggers manager alert and priority adjustment."""
    router = BusinessOSActionRouter(confidence_threshold=0.85)

    high_stress_event = BehavioralEvaluationEvent(
        event_id="EVT-TEST-STRESS",
        input_id="INP-TEST-01",
        author_id="EMP-STRESSED",
        burnout_risk=True,
        burnout_risk_confidence=0.95,
        stress_score=5,
        stress_score_confidence=0.92,
        behavior_style="S",
        behavior_style_confidence=0.80,
        timestamp=1000.0,
    )

    result = router.route(high_stress_event, task_context="Hoàn thành báo cáo tài chính quý 3")

    action_types = [a.action_type for a in result.actions]
    assert "URGENT_MANAGER_ALERT" in action_types
    assert "TASK_PRIORITY_ADJUSTMENT" in action_types
    assert len(result.alerts_triggered) >= 1
    assert "URGENT_BURNOUT_ALERT" in result.alerts_triggered[0]


def test_business_os_router_disc_formatting() -> None:
    """Validate that DISC styles D and C produce tailored task dispatch templates."""
    router = BusinessOSActionRouter(confidence_threshold=0.85)

    # Style D
    event_d = BehavioralEvaluationEvent(
        event_id="EVT-TEST-D",
        input_id="INP-TEST-02",
        author_id="EMP-DOMINANT",
        burnout_risk=False,
        burnout_risk_confidence=0.90,
        stress_score=1,
        stress_score_confidence=0.88,
        behavior_style="D",
        behavior_style_confidence=0.95,
        timestamp=1000.0,
    )
    res_d = router.route(event_d, task_context="Chốt hợp đồng bán hàng")
    actions_d = [a.action_type for a in res_d.actions]
    assert "TASK_DISPATCH_DIRECT_BULLETS" in actions_d
    assert "EXECUTIVE DIRECT DISPATCH" in res_d.dispatch_text

    # Style C
    event_c = BehavioralEvaluationEvent(
        event_id="EVT-TEST-C",
        input_id="INP-TEST-03",
        author_id="EMP-ANALYTICAL",
        burnout_risk=False,
        burnout_risk_confidence=0.90,
        stress_score=2,
        stress_score_confidence=0.88,
        behavior_style="C",
        behavior_style_confidence=0.92,
        timestamp=1000.0,
    )
    res_c = router.route(event_c, task_context="Tái cấu trúc cơ sở dữ liệu")
    actions_c = [a.action_type for a in res_c.actions]
    assert "TASK_DISPATCH_TECH_SPEC" in actions_c
    assert "TECHNICAL SPECIFICATION DISPATCH" in res_c.dispatch_text


def test_end_to_end_pipeline_flow() -> None:
    """Validate full end-to-end flow: Raw Message -> Decider -> NhanThuat -> BusinessOS."""
    decider = JevDecisionAdapter(mock_mode=True)
    nhan_thuat = NhanThuatBehavioralService(decider=decider)
    router = BusinessOSActionRouter()

    # Overworked employee input
    raw_message = "Em quá tải và kiệt sức rồi anh ơi, áp lực deadline dồn dập không kham nổi nữa."
    event = nhan_thuat.evaluate(raw_message, author_id="EMP-999")
    result = router.route(event, task_context="Viết tài liệu API")

    assert event.burnout_risk is True
    assert event.stress_score >= 4
    action_types = [a.action_type for a in result.actions]
    assert "URGENT_MANAGER_ALERT" in action_types
    assert "TASK_PRIORITY_ADJUSTMENT" in action_types
