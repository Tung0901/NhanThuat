"""
Unit tests for Continuous Behavioral Profiler & Flight Risk Radar.
Validates operationalization of NT-MODEL-0008 and NT-MODEL-0011.
"""

import time

from modules.nhan_thuat.continuous_profiler import ContinuousBehavioralProfiler
from modules.nhan_thuat.service import BehavioralEvaluationEvent


def create_mock_event(
    author_id: str,
    stress: int,
    burnout: bool,
    style: str,
    offset_seconds: int = 0,
) -> BehavioralEvaluationEvent:
    return BehavioralEvaluationEvent(
        event_id=f"EVT-TEST-{author_id}-{offset_seconds}",
        input_id=f"INP-TEST-{author_id}-{offset_seconds}",
        author_id=author_id,
        burnout_risk=burnout,
        burnout_risk_confidence=0.95,
        stress_score=stress,
        stress_score_confidence=0.92,
        behavior_style=style,
        behavior_style_confidence=0.90,
        timestamp=time.time() + offset_seconds,
    )


def test_continuous_profiler_single_event():
    profiler = ContinuousBehavioralProfiler()
    ev = create_mock_event(author_id="EMP-MINH", stress=2, burnout=False, style="D")

    profile = profiler.ingest_event(ev)
    assert profile.author_id == "EMP-MINH"
    assert profile.sample_count == 1
    assert profile.baseline_disc == "D"
    assert profile.average_stress == 2.0
    assert profile.flight_risk_level == "LOW"
    assert "Độc đoán áp đặt" in profile.under_load_forecast.default_tendency
    assert profile.context_strength.situation_strength == "STRONG"


def test_continuous_profiler_stress_trajectory_and_critical_flight_risk():
    profiler = ContinuousBehavioralProfiler()
    author = "EMP-BURNOUT"

    # Simulate rising stress over 4 interactions
    events = [
        create_mock_event(author, stress=2, burnout=False, style="S", offset_seconds=0),
        create_mock_event(author, stress=3, burnout=False, style="S", offset_seconds=10),
        create_mock_event(author, stress=5, burnout=True, style="S", offset_seconds=20),
        create_mock_event(author, stress=5, burnout=True, style="S", offset_seconds=30),
    ]

    for ev in events:
        profile = profiler.ingest_event(ev)

    assert profile.sample_count == 4
    assert profile.average_stress >= 3.5
    assert profile.stress_trajectory == [2, 3, 5, 5]
    assert profile.burnout_velocity > 0.0
    assert profile.flight_risk_level == "CRITICAL"
    assert profile.flight_risk_score >= 0.70
    assert len(profile.recommended_interventions) >= 2
    assert "Workload Throttle" in profile.recommended_interventions[0]


def test_continuous_profiler_context_strength_weak_situation():
    profiler = ContinuousBehavioralProfiler()
    ev = create_mock_event("EMP-CREATIVE", stress=1, burnout=False, style="I")

    # Ingest in an ambiguous, unconstrained environment
    profile = profiler.ingest_event(ev, context_clarity=0.2, context_constraints=0.3)
    assert profile.context_strength.situation_strength == "WEAK"
    assert profile.context_strength.dominant_determinant == "PERSONALITY_TRAITS"
    assert "Mất tập trung" in profile.under_load_forecast.default_tendency


def test_continuous_profiler_team_radar():
    profiler = ContinuousBehavioralProfiler()

    # 1 safe employee
    profiler.ingest_event(create_mock_event("EMP-SAFE", stress=1, burnout=False, style="C"))

    # 1 critical employee
    for s in [4, 5, 5]:
        profiler.ingest_event(create_mock_event("EMP-DANGER", stress=s, burnout=True, style="D"))

    radar = profiler.get_team_radar()
    assert radar["status"] == "success"
    assert radar["total_monitored"] == 2
    assert radar["critical_flight_risk_count"] == 1
    assert len(radar["profiles"]) == 2


def test_behavioral_http_endpoints():
    """Test HTTP API endpoints for behavioral stream analysis and radar."""
    import json
    from io import BytesIO
    from unittest.mock import MagicMock

    from backend.app.main import BusinessOSGatewayHandler

    handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
    handler._send_json_response = MagicMock()

    # 1. POST /api/v1/behavioral/analyze-stream
    payload = json.dumps({
        "content": "Tôi đang kiệt sức hoàn toàn vì dự án này, áp lực liên tục quá mức chịu đựng.",
        "author_id": "EMP-STREAM-TEST",
        "context_clarity": 0.9,
        "context_constraints": 0.8,
    }).encode("utf-8")

    handler.path = "/api/v1/behavioral/analyze-stream"
    handler.headers = {"Content-Length": str(len(payload))}
    handler.rfile = BytesIO(payload)
    handler.do_POST()

    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert "event" in data
    assert "profile" in data
    assert data["profile"]["author_id"] == "EMP-STREAM-TEST"

    # 2. GET /api/v1/behavioral/profile?author_id=EMP-STREAM-TEST
    handler._send_json_response.reset_mock()
    handler.path = "/api/v1/behavioral/profile?author_id=EMP-STREAM-TEST"
    handler.headers = {}
    handler.do_GET()

    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["profile"]["author_id"] == "EMP-STREAM-TEST"

    # 3. GET /api/v1/behavioral/radar
    handler._send_json_response.reset_mock()
    handler.path = "/api/v1/behavioral/radar"
    handler.headers = {}
    handler.do_GET()

    handler._send_json_response.assert_called_once()
    code, data = handler._send_json_response.call_args[0]
    assert code == 200
    assert data["status"] == "success"
    assert data["total_monitored"] >= 1

