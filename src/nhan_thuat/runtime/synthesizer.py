"""LLM synthesis with a deterministic fallback (capability NHANTHUAT-CAP-002).

Fallback-first design: if no OpenAI-compatible API key is configured the
synthesizer returns the deterministic retrieval flow (context, citations,
audit). With a key it calls the configured provider over ``requests`` and
includes an audit record (correlation_id, provider, prompt, latency, model).
"""

from __future__ import annotations

import os
import time
import uuid
from typing import Any, Iterable

import requests

from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.runtime.prompt_builder import PromptBuilder

OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.environ.get("NHAN_THUAT_LLM_MODEL", "gpt-4o-mini")


def _api_key() -> str:
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("NHAN_THUAT_OPENAI_API_KEY", "")


class KnowledgeSynthesizer:
    """Produces a synthesis for a query and its retrieved knowledge units."""

    def __init__(self, prompt_builder: PromptBuilder | None = None, timeout: int = 30) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.timeout = timeout

    @property
    def provider_configured(self) -> bool:
        return bool(_api_key())

    def synthesize(self, query: str, units: Iterable[KnowledgeUnit]) -> dict[str, Any]:
        """Return a synthesis result with mode, citations, and audit.

        The result dict always contains:
        - ``mode``: "llm" or "deterministic"
        - ``synthesis``: human-readable markdown
        - ``citations``: list of {"id", "title", "domain"}
        - ``audit``: {correlation_id, provider, model, latency_ms, prompt}
        - ``warning``: optional note when LLM was unavailable
        """
        units_list = list(units)
        citations = [
            {"id": unit.id, "title": unit.title, "domain": unit.primary_domain}
            for unit in units_list
        ]
        prompt = self._build_prompt(query, units_list)
        correlation_id = f"CORR-LLM-{uuid.uuid4().hex[:8].upper()}"

        if not self.provider_configured:
            return {
                "mode": "deterministic",
                "synthesis": self._deterministic_synthesis(query, units_list),
                "citations": citations,
                "audit": {
                    "correlation_id": correlation_id,
                    "provider": "deterministic",
                    "model": None,
                    "latency_ms": 0,
                    "prompt": prompt,
                },
                "warning": (
                    "LLM synthesis is not configured (no OPENAI_API_KEY). "
                    "Showing the deterministic knowledge retrieval flow."
                ),
            }

        started = time.monotonic()
        try:
            text = self._call_provider(prompt)
            latency_ms = int((time.monotonic() - started) * 1000)
            return {
                "mode": "llm",
                "synthesis": text,
                "citations": citations,
                "audit": {
                    "correlation_id": correlation_id,
                    "provider": "openai-compatible",
                    "model": OPENAI_MODEL,
                    "latency_ms": latency_ms,
                    "prompt": prompt,
                },
            }
        except Exception as exc:  # pragma: no cover - network boundary
            latency_ms = int((time.monotonic() - started) * 1000)
            return {
                "mode": "deterministic",
                "synthesis": self._deterministic_synthesis(query, units_list),
                "citations": citations,
                "audit": {
                    "correlation_id": correlation_id,
                    "provider": "openai-compatible",
                    "model": OPENAI_MODEL,
                    "latency_ms": latency_ms,
                    "prompt": prompt,
                    "error": str(exc),
                },
                "warning": f"LLM provider call failed ({exc}); fell back to deterministic flow.",
            }

    def _build_prompt(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        context = self.prompt_builder.build_context(units, format_type="markdown")
        return (
            "Bạn là Nhân Thuật, một hệ tri thức về hành vi con người và tổ chức.\n"
            "Trả lời bằng tiếng Việt, bám sát phần Tri thức bên dưới, trích dẫn ID "
            "tri thức (dạng NT-*) khi tham chiếu, và nêu rõ rủi ro/hạn chế nếu có.\n\n"
            f"CÂU HỎI:\n{query}\n\n"
            f"TRI THỨC:\n{context}"
        )

    def _deterministic_synthesis(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        units_list = list(units)
        if not units_list:
            return "Không có tri thức liên quan."
        names = ", ".join(f"**{u.title}** ({u.id})" for u in units_list[:3])
        return (
            f"Dựa trên {len(units_list)} tri thức cốt lõi được truy xuất, tình huống "
            f"được phân tích qua: {names}. "
            "Kết luận mang tính tham khảo từ tri thức đã kiểm định; xem trích dẫn "
            "chi tiết và phần đánh giá rủi ro để ra quyết định."
        )

    def _call_provider(self, prompt: str) -> str:
        response = requests.post(
            f"{OPENAI_BASE_URL.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {_api_key()}"},
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": "Bạn là một chuyên gia phân tích tri thức."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]