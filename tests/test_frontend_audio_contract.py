"""Static contract tests for the offline Executive Audio controller."""

from pathlib import Path


def test_council_audio_covers_seven_lenses_and_complete_decision() -> None:
    source = Path("frontend/js/executive_audio.js").read_text(encoding="utf-8")

    assert "Hội đồng tham mưu bảy lăng kính Nhân Thuật" in source
    assert "situation_read" in source
    assert "recommended_actions" in source
    assert "evidence_needed" in source
    assert "cross_debates" in source
    assert "plan_c_containment" in source
    assert "critical_caveats" in source
    assert "execution_directives" in source
    assert "Hội Đồng 7 Lăng Kính" in source
    assert "Hội Đồng 5" not in source


def test_audio_player_uses_restrained_controls_and_voice_selector() -> None:
    source = Path("frontend/js/executive_audio.js").read_text(encoding="utf-8")

    assert "exec-audio-voice-select" in source
    assert "selectVoice" in source
    assert "🎙️" not in source
    assert "⏮️" not in source
    assert "⏭️" not in source
