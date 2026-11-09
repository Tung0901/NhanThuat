"""Tests for Unconstrained AI Synthesis and Streaming SSE capability.
Spec: SPEC-UNCONSTRAINED-AI-SYNTHESIS
Plan: PLAN-UNCONSTRAINED-AI-SYNTHESIS
"""

from unittest.mock import MagicMock, patch

from nhan_thuat.engine.sparring_engine import SparringEngine
from nhan_thuat.runtime.synthesizer import (
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_REQUEST_TIMEOUT,
    KnowledgeSynthesizer,
)
from nhan_thuat.storage.db import DatabaseManager


def test_synthesizer_defaults_and_env_config(monkeypatch):
    """Verify default max tokens and timeout adhere to unconstrained settings."""
    assert DEFAULT_MAX_OUTPUT_TOKENS >= 4096
    assert DEFAULT_REQUEST_TIMEOUT >= 120

    syn = KnowledgeSynthesizer()
    assert syn.timeout >= 120

    monkeypatch.setenv("AI_MAX_OUTPUT_TOKENS", "16384")
    monkeypatch.setenv("AI_REQUEST_TIMEOUT", "180")
    custom_syn = KnowledgeSynthesizer()
    assert custom_syn.timeout == 180


def test_call_provider_passes_max_tokens():
    """Verify _call_provider sends max_tokens in payload to upstream API."""
    syn = KnowledgeSynthesizer()
    config = {
        "base_url": "https://api.example.com",
        "api_key": "test-key-123456789",
        "model": "test-model",
        "provider_name": "test-provider",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Phân tích chiến lược chuyên sâu toàn diện."}}]
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        result = syn._call_provider("prompt text", config, max_tokens=12000)
        assert result == "Phân tích chiến lược chuyên sâu toàn diện."
        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["max_tokens"] == 12000
        assert call_kwargs["timeout"] >= 120


def test_synthesizer_generate_stream_chunks():
    """Verify generate_stream correctly decodes and yields SSE chunks."""
    syn = KnowledgeSynthesizer()
    config = {
        "base_url": "https://api.example.com",
        "api_key": "test-key-123456789",
        "model": "test-model",
        "provider_name": "test-provider",
    }

    lines = [
        b'data: {"choices": [{"delta": {"content": "L\xe1\xba\xadp lu\xe1\xba\xadn"}}]}',
        b'data: {"choices": [{"delta": {"content": " s\xe1\xba\xafc b\xc3\xa9n."}}]}',
        b"data: [DONE]",
    ]
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.iter_lines.return_value = lines

    with patch("nhan_thuat.runtime.synthesizer.get_provider_configs", return_value=[config]), \
         patch("requests.post", return_value=mock_resp):
        chunks = list(syn.generate_stream("Đàm phán thế trận"))
        assert "".join(chunks) == "Lập luận sắc bén."


def test_build_prompt_has_no_artificial_length_clamps():
    """Verify prompt does not instruct AI to be overly brief or limit sentences."""
    syn = KnowledgeSynthesizer()
    mock_unit = MagicMock()
    mock_unit.id = "NT-LAW-0001"
    mock_unit.title = "Quy luật Khách quan"
    mock_unit.primary_domain = "human-nature"
    mock_unit.definition = "Quy luật vận hành khách quan"
    mock_unit.summary = "Định vị quy luật khách quan"
    mock_unit.type = "law"

    prompt = syn._build_prompt("Xử lý khủng hoảng truyền thông", [mock_unit])

    assert "Tối đa 4 câu" not in prompt
    assert "KHÔNG GIỚI HẠN ĐỘ DÀI" in prompt
    assert "BÀI NGHỊ LUẬN CHIẾN LƯỢC TOÀN DIỆN" in prompt


def test_sparring_engine_prompt_uncapped(tmp_path):
    """Verify SparringEngine prompt is free from brevity clamps."""
    db = DatabaseManager(db_path=str(tmp_path / "test_sparring.db"))
    engine = SparringEngine(db_manager=db)

    # Inspect _generate_sparring_response prompt via KnowledgeSynthesizer mock
    captured_prompt = []

    def mock_gen_text(prompt, max_tokens=None):
        captured_prompt.append(prompt)
        return "### ⚔️ 1. PHẢN BIỆN\nĐối đáp.\n### 💡 2. GỢI Ý\nĐòn bẩy."

    with patch("nhan_thuat.runtime.synthesizer.KnowledgeSynthesizer.generate_text", side_effect=mock_gen_text):
        engine._generate_sparring_response(
            user_text="Chúng tôi muốn giảm giá 10%",
            lens="LEGALISM",
            units=[],
            related_map={},
        )

    assert len(captured_prompt) == 1
    p = captured_prompt[0]
    assert "Tối đa 4 câu" not in p
    assert "[1 câu]" not in p
    assert "Không giới hạn số câu" in p


def test_sparring_process_turn_stream(tmp_path):
    """Verify SparringEngine process_turn_stream yields meta, content, and done events."""
    db = DatabaseManager(db_path=str(tmp_path / "test_sparring_stream.db"))
    engine = SparringEngine(db_manager=db)
    session = engine.start_session("Phiên đàm phán dòng", philosophy_lens="LEGALISM")

    stream_chunks = ["Lập luận ", "của bạn ", "chưa có chế tài."]

    with patch("nhan_thuat.runtime.synthesizer.KnowledgeSynthesizer.provider_configured", True), \
         patch("nhan_thuat.runtime.synthesizer.KnowledgeSynthesizer.generate_stream", return_value=iter(stream_chunks)):
        events = list(engine.process_turn_stream(
            session_id=session.id,
            user_message="Chúng tôi muốn giãn nợ 30 ngày.",
            override_lens="LEGALISM",
        ))

    event_types = [e["type"] for e in events]
    assert "meta" in event_types
    assert "content" in event_types
    assert "done" in event_types

    # Verify messages saved to database
    messages = db.list_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Lập luận của bạn chưa có chế tài."
