"""Runtime authorization and seven-lens depth contract."""

from backend.app.engine.philosophies.iching_service import iching_service
from backend.app.engine.philosophies.router import PhilosophyRouter, PhilosophyType
from nhan_thuat.council.council_engine import CouncilEngine


def test_provisional_lenses_have_product_owner_runtime_authorization() -> None:
    router = PhilosophyRouter()
    for lens in (PhilosophyType.ICHING, PhilosophyType.TIMING):
        metadata = router.engines[lens]["metadata"]
        assert metadata["governance_status"] == "ready_for_review"
        assert 0.0 < metadata["confidence_modifier"] < 1.0
        authorization = metadata["runtime_authorization"]
        assert authorization["status"] == "enabled"
        assert authorization["authorized_by"] == "Product Owner"
        assert authorization["scope"] == "council_and_router"
        assert router._is_routable(lens) is True


def test_router_executes_iching_and_timing_as_qualitative_lenses() -> None:
    router = PhilosophyRouter()
    iching = router.route({
        "scenario_type": "transformation",
        "intent": "bế tắc, cần kiểm tra chuyển pha theo Dịch học",
        "keywords": ["kinh dịch", "biến dịch"],
    })
    timing = router.route({
        "scenario_type": "timing",
        "intent": "đánh giá cửa sổ hành động và độ chín dữ liệu",
        "keywords": ["thời thế", "đúng thời điểm"],
    })
    assert iching["status"] == "success"
    assert iching["primary_philosophy"] == "iching"
    assert 0.0 < iching["lens_confidence_scores"]["iching"] < 1.0
    assert timing["status"] == "success"
    assert timing["primary_philosophy"] == "timing"
    assert 0.0 < timing["lens_confidence_scores"]["timing"] < 1.0


def test_council_returns_all_seven_complete_perspectives(monkeypatch) -> None:
    # Force the deterministic path so the depth contract is stable in CI.
    from nhan_thuat.runtime import synthesizer

    def fail_generation(*_args, **_kwargs):
        raise RuntimeError("offline test")

    monkeypatch.setattr(synthesizer.KnowledgeSynthesizer, "generate_json", fail_generation)
    result = CouncilEngine().deliberate(
        "Doanh nghiệp đang ở ngã rẽ chuyển đổi nhưng dữ liệu thị trường còn mâu thuẫn."
    )
    assert {pitch.agent_id for pitch in result.pitches} == {
        "LEGALISM", "TAOISM", "CONFUCIAN", "XUNZI", "SUNZI", "ICHING", "TIMING"
    }
    for pitch in result.pitches:
        assert len(pitch.situation_read) >= 80
        assert len(pitch.stance) >= 80
        assert len(pitch.assumptions) >= 2
        assert len(pitch.core_arguments) >= 4
        assert len(pitch.recommended_actions) >= 3
        assert len(pitch.evidence_needed) >= 2
        assert all(len(item.strip()) >= 20 for item in pitch.assumptions)
        assert all(len(item.strip()) >= 20 for item in pitch.core_arguments)
        assert all(len(item.strip()) >= 20 for item in pitch.recommended_actions)
        assert all(len(item.strip()) >= 20 for item in pitch.evidence_needed)
        assert len(pitch.risk_warning) >= 60
        assert len(pitch.confidence_note) >= 40


def test_unreviewed_oracle_remains_outside_council_runtime() -> None:
    result = iching_service.cast_oracle("Có nên đầu tư ngay không?", seed=42)
    assert result["error_code"] == "ORACLE_UNAVAILABLE"
    assert "primary_hexagram" not in result
