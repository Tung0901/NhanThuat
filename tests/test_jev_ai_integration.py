"""
Targeted Test Suite for TypeSafe AI Jev System One Integration.
Validates:
1. Typed JevClient & contract compliance (choice, score, noul, calibrated_probabilities).
2. Calibrated mock client when TYPESAFE_API_KEY is absent.
3. Typed live HTTP client calling POST https://api.typesafe.ai/v1/systemone with Bearer auth.
4. Error handling and boundary isolation.
5. BusinessOS pipeline integration (BusinessOSRuntimeOrchestrator).
"""

import pytest

from backend.app.engine.jev_client import (
    DEFAULT_JEV_ENDPOINT,
    JevAPIError,
    JevClient,
    JevDecisionResponse,
)
from backend.app.engine.runtime import BusinessOSRuntimeOrchestrator, RuntimeRequestPayload


def test_jev_client_mock_mode_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """When TYPESAFE_API_KEY is absent or placeholder, client operates in mock mode."""
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)

    client = JevClient()
    assert client.is_mock is True

    res = client.decide("Contract dispute with vendor delaying delivery")

    assert isinstance(res, JevDecisionResponse)
    assert res.is_mock is True
    assert res.choice in ["EXECUTE", "CALIBRATE", "DE_ESCALATE", "ESCALATE"]
    assert 0.0 <= res.score <= 1.0
    assert 0.70 <= res.noul <= 0.98
    assert isinstance(res.calibrated_probabilities, dict)

    # Probabilities must be calibrated and sum to 1.0
    prob_sum = sum(res.calibrated_probabilities.values())
    assert pytest.approx(prob_sum, 0.001) == 1.0

    # Top choice must match highest probability
    max_opt = max(res.calibrated_probabilities.items(), key=lambda x: x[1])[0]
    assert res.choice == max_opt
    assert res.score == res.calibrated_probabilities[max_opt]


def test_jev_client_mock_with_custom_options() -> None:
    """Mock client must calibrate probabilities across user-supplied custom options."""
    client = JevClient(mock_mode=True)
    custom_options = ["APPROVE_IMMEDIATE", "REJECT_WITH_PENALTY", "REQUEST_AUDIT"]

    res = client.decide(
        prompt="Review invoice discrepancy of $50,000",
        options=custom_options,
    )

    assert res.choice in custom_options
    assert set(res.calibrated_probabilities.keys()) == set(custom_options)
    assert pytest.approx(sum(res.calibrated_probabilities.values()), 0.001) == 1.0


def test_jev_client_placeholder_key_triggers_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Placeholder keys like 'your_typesafe_api_key_here' must safely default to mock."""
    monkeypatch.setenv("TYPESAFE_API_KEY", "your_typesafe_api_key_here")
    client = JevClient()
    assert client.is_mock is True


def test_jev_client_live_http_request_contract(monkeypatch: pytest.MonkeyPatch) -> None:
    """When valid API key is present, client sends POST to TypeSafe endpoint with Bearer auth."""
    test_key = "ts_live_test_api_key_12345"
    monkeypatch.setenv("TYPESAFE_API_KEY", test_key)

    captured_calls: list[dict] = []

    class FakeResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "choice": "DE_ESCALATE",
                "score": 0.88,
                "noul": 0.94,
                "calibrated_probabilities": {
                    "EXECUTE": 0.05,
                    "CALIBRATE": 0.05,
                    "DE_ESCALATE": 0.88,
                    "ESCALATE": 0.02,
                },
            }

    def fake_post(url: str, **kwargs):
        captured_calls.append({"url": url, "kwargs": kwargs})
        return FakeResponse()

    monkeypatch.setattr("nhan_thuat.runtime.jev_client.requests.post", fake_post)

    client = JevClient()
    assert client.is_mock is False
    assert client.endpoint == DEFAULT_JEV_ENDPOINT

    res = client.call_system_one(
        prompt="Key talent threatens to resign due to compensation dispute",
        options=["EXECUTE", "CALIBRATE", "DE_ESCALATE", "ESCALATE"],
    )

    assert len(captured_calls) == 1
    call = captured_calls[0]
    assert call["url"] == "https://api.typesafe.ai/v1/systemone"
    assert call["kwargs"]["headers"]["Authorization"] == f"Bearer {test_key}"
    assert call["kwargs"]["headers"]["Content-Type"] == "application/json"

    assert res.choice == "DE_ESCALATE"
    assert res.score == 0.88
    assert res.noul == 0.94
    assert res.is_mock is False
    assert res.calibrated_probabilities["DE_ESCALATE"] == 0.88


def test_jev_client_http_error_raises_jev_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Live HTTP client must raise typed JevAPIError on failure."""
    monkeypatch.setenv("TYPESAFE_API_KEY", "ts_live_valid_key_99999")

    def fail_post(*args, **kwargs):
        import requests
        raise requests.ConnectionError("Connection refused by typesafe.ai")

    monkeypatch.setattr("nhan_thuat.runtime.jev_client.requests.post", fail_post)

    client = JevClient()
    with pytest.raises(JevAPIError, match="Failed to communicate with TypeSafe Jev API"):
        client.decide("Test scenario under connection failure")


def test_businessos_runtime_orchestrator_jev_integration() -> None:
    """BusinessOSRuntimeOrchestrator must incorporate Jev System One decisions into pipeline execution."""
    orchestrator = BusinessOSRuntimeOrchestrator()

    # Direct System One evaluation
    s1_res = orchestrator.evaluate_system_one("Vendor refusing to honor delivery warranty")
    assert isinstance(s1_res, JevDecisionResponse)
    assert s1_res.choice in ["EXECUTE", "CALIBRATE", "DE_ESCALATE", "ESCALATE"]
    assert s1_res.noul > 0.0

    # Pipeline execution with System One included in structured output
    req = RuntimeRequestPayload(
        session_id="SESS-JEV-001",
        correlation_id="CORR-JEV-001",
        intent_action="conflict_resolution",
        scenario_type="vendor_dispute",
        context_stack={"keywords": ["breach of contract", "delivery failure"]},
        requested_knowledge_ids=["NT-LAW-0001"],
    )

    response = orchestrator.execute(req)
    assert response.status_code == "SUCCESS"
    assert "system_one_decision" in response.structured_output

    s1_output = response.structured_output["system_one_decision"]
    assert "choice" in s1_output
    assert "score" in s1_output
    assert "noul" in s1_output
    assert "calibrated_probabilities" in s1_output
    assert s1_output["choice"] in s1_output["calibrated_probabilities"]
