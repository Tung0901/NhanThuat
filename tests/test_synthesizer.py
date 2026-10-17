"""Tests for EPIC 5 LLM synthesis (fallback-first) and resolver scores."""

import os

import pytest

from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.runtime.resolver import KnowledgeResolver
from nhan_thuat.runtime.synthesizer import (
    DEFAULT_MODEL,
    KnowledgeSynthesizer,
    get_provider_configs,
    get_provider_summary,
)

_KEY_ENV = (
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_MODEL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENAI_MODEL",
    "NHAN_THUAT_LLM_MODEL",
    "NHAN_THUAT_LLM_PROVIDER",
)


@pytest.fixture(autouse=True)
def isolated_provider_environment(monkeypatch) -> None:
    """Provider tests must not depend on developer or deployment secrets."""
    for key in _KEY_ENV:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(scope="module")
def units() -> list[KnowledgeUnit]:
    engine = KnowledgeEngine()
    return [
        KnowledgeUnit.from_mapping(iu.raw_data, source_path=None)
        for iu in engine.units_by_id.values()
    ]


@pytest.fixture(scope="module")
def resolver(units: list[KnowledgeUnit]) -> KnowledgeResolver:
    return KnowledgeResolver(units)


def _clear_keys() -> dict[str, str | None]:
    return {k: os.environ.pop(k, None) for k in _KEY_ENV}


def _restore_keys(saved: dict[str, str | None]) -> None:
    for k, v in saved.items():
        if v is not None:
            os.environ[k] = v


def test_resolver_scored_returns_pairs(resolver: KnowledgeResolver) -> None:
    pairs = resolver.resolve_scored("khách hàng trì hoãn quyết định mua", limit=5)
    assert pairs
    assert all(isinstance(score, int) and isinstance(unit, KnowledgeUnit) for score, unit in pairs)
    scores = [score for score, _ in pairs]
    assert scores == sorted(scores, reverse=True)


def test_resolver_scored_consistent_with_resolve(resolver: KnowledgeResolver) -> None:
    query = "khủng hoảng truyền thông"
    resolve_ids = [u.id for u in resolver.resolve(query, limit=3)]
    scored_ids = [u.id for _, u in resolver.resolve_scored(query, limit=3)]
    assert resolve_ids == scored_ids


def test_synthesizer_deterministic_fallback_without_key(units: list[KnowledgeUnit]) -> None:
    saved = _clear_keys()
    try:
        synthesizer = KnowledgeSynthesizer()
        assert not synthesizer.provider_configured
        result = synthesizer.synthesize("Tại sao khách hàng trì hoãn quyết định mua?", units[:3])
        assert result["mode"] == "deterministic"
        assert result["synthesis"]
        assert result["citations"]
        assert all({"id", "title", "domain"} <= set(c) for c in result["citations"])
        assert result["audit"]["correlation_id"].startswith("CORR-LLM-")
        assert result["audit"]["provider"] == "deterministic"
        assert "warning" in result
    finally:
        _restore_keys(saved)


def test_deterministic_synthesis_is_readable(units: list[KnowledgeUnit]) -> None:
    """Regression: tuple-typed mechanism/risks must not leak Python repr into output."""
    saved = _clear_keys()
    try:
        synthesizer = KnowledgeSynthesizer()
        result = synthesizer.synthesize("Nhân sự chủ chốt bất mãn và chống đối ngầm", units[:3])
        text = result["synthesis"]
        assert "TÓM TẮT ĐIỀU HÀNH" in text
        assert "('" not in text
        assert "tuple(" not in text
        assert "  ►" not in text
    finally:
        _restore_keys(saved)


def test_synthesizer_llm_with_gemini_key(units: list[KnowledgeUnit], monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy-test-key")
    synthesizer = KnowledgeSynthesizer()

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "Phân tích theo Luật X (NT-LAW-2101)."}}]}

    def fake_post(*args, **kwargs) -> FakeResponse:
        assert "generativelanguage.googleapis.com" in args[0]
        assert kwargs["json"]["model"] == DEFAULT_MODEL
        return FakeResponse()

    monkeypatch.setattr("nhan_thuat.runtime.synthesizer.requests.post", fake_post)

    result = synthesizer.synthesize("Tại sao khách hàng trì hoãn quyết định mua?", units[:2])

    assert result["mode"] == "llm"
    assert "Phân tích theo Luật X" in result["synthesis"]
    assert result["audit"]["provider"] == "google-gemini"
    assert result["audit"]["model"] == DEFAULT_MODEL
    assert result["audit"]["latency_ms"] >= 0


def test_synthesizer_falls_back_on_provider_error(units: list[KnowledgeUnit], monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy-test-key")

    def fail_post(*args, **kwargs):
        raise RuntimeError("connection refused")

    synthesizer = KnowledgeSynthesizer()
    monkeypatch.setattr("nhan_thuat.runtime.synthesizer.requests.post", fail_post)

    result = synthesizer.synthesize("test query", units[:2])

    assert result["mode"] == "deterministic"
    assert "deterministic" in result.get("warning", "")


def test_synthesizer_honors_explicit_model_override(units: list[KnowledgeUnit], monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSy-test-key")
    monkeypatch.setenv("NHAN_THUAT_LLM_MODEL", "gemini-3.6-flash")
    synthesizer = KnowledgeSynthesizer()

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "Phân tích."}}]}

    def fake_post(*args, **kwargs) -> FakeResponse:
        assert kwargs["json"]["model"] == "gemini-3.6-flash"
        return FakeResponse()

    monkeypatch.setattr("nhan_thuat.runtime.synthesizer.requests.post", fake_post)

    result = synthesizer.synthesize("test query", units[:2])

    assert result["mode"] == "llm"
    assert result["audit"]["model"] == "gemini-3.6-flash"


def test_deepseek_is_preferred_and_models_are_provider_specific(monkeypatch) -> None:
    saved = _clear_keys()
    try:
        monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-test-key-value")
        monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
        monkeypatch.setenv("GOOGLE_API_KEY", "google-test-key-value")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")

        configs = get_provider_configs()

        assert [config["provider_name"] for config in configs] == [
            "deepseek", "google-gemini"
        ]
        assert configs[0]["model"] == "deepseek-chat"
        assert configs[1]["model"] == "gemini-test-model"
    finally:
        _restore_keys(saved)


def test_provider_preference_and_public_summary_never_expose_keys(monkeypatch) -> None:
    saved = _clear_keys()
    try:
        monkeypatch.setenv("DEEPSEEK_API_KEY", "ds-private-secret")
        monkeypatch.setenv("GOOGLE_API_KEY", "google-private-secret")
        monkeypatch.setenv("NHAN_THUAT_LLM_PROVIDER", "gemini")

        configs = get_provider_configs()
        summary = get_provider_summary()

        assert [config["provider_name"] for config in configs] == [
            "google-gemini", "deepseek"
        ]
        assert summary["preferred_provider"] == "gemini"
        assert summary["configured_providers"] == ["google-gemini", "deepseek"]
        assert "api_key" not in str(summary).lower()
        assert "private-secret" not in str(summary)
    finally:
        _restore_keys(saved)
