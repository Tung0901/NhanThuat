"""LLM synthesis with a deterministic fallback (capability NHANTHUAT-CAP-002).

Fallback-first design: if no Google Gemini (AI Studio) API key is configured
the synthesizer returns the deterministic retrieval flow (context, citations,
audit). With a key it calls the Gemini OpenAI-compatible endpoint over
``requests`` and includes an audit record (correlation_id, provider, prompt,
latency, model).
"""

from __future__ import annotations

import os
import time
import uuid
from collections.abc import Iterable
from typing import Any

import requests

from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.runtime.prompt_builder import PromptBuilder

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEFAULT_MODEL = "gemini-3.6-flash"


def _api_key() -> str:
    return (
        os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or ""
    ).strip()


def _base_url() -> str:
    explicit = (
        os.environ.get("GEMINI_BASE_URL", "")
        or os.environ.get("OPENAI_BASE_URL", "")
    ).strip().rstrip("/")
    return explicit or DEFAULT_BASE_URL


def _model() -> str:
    explicit = (
        os.environ.get("GEMINI_MODEL", "")
        or os.environ.get("NHAN_THUAT_LLM_MODEL", "")
    ).strip()
    return explicit or DEFAULT_MODEL


def provider_name() -> str:
    """Human-readable provider label derived from the configured base URL."""
    base = _base_url()
    if "generativelanguage.googleapis.com" in base:
        return "google-gemini"
    return "openai-compatible"


OPENAI_BASE_URL = _base_url()
OPENAI_MODEL = _model()


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
                    "Chưa cấu hình LLM synthesis (thiếu GEMINI_API_KEY). "
                    "Đang hiển thị dòng truy xuất tri thức deterministic."
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
                    "provider": provider_name(),
                    "model": _model(),
                    "latency_ms": latency_ms,
                    "prompt": prompt,
                },
            }
        except Exception as exc:  # noqa: BLE001 - intentional: any provider failure must fall back to deterministic
            latency_ms = int((time.monotonic() - started) * 1000)
            return {
                "mode": "deterministic",
                "synthesis": self._deterministic_synthesis(query, units_list),
                "citations": citations,
                "audit": {
                    "correlation_id": correlation_id,
                    "provider": provider_name(),
                    "model": _model(),
                    "latency_ms": latency_ms,
                    "prompt": prompt,
                    "error": str(exc),
                },
                "warning": (
                    f"Lỗi khi gọi LLM provider ({exc}); đã chuyển sang dòng truy xuất deterministic. "
                    f"Đã thử: {_base_url()}/chat/completions | Mô hình: {_model()}."
                ),
            }

    def _build_prompt(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        context = self.prompt_builder.build_context(units, format_type="markdown")
        return (
            "Bạn là Nhân Thuật, một chuyên gia chiến lược bậc thầy về hành vi con người và quản trị tổ chức.\n"
            "Nhiệm vụ của bạn là phân tích sâu sắc, đa chiều và đưa ra CÁC GIẢI PHÁP HÀNH ĐỘNG cụ thể.\n\n"
            "Yêu cầu nội dung:\n"
            "- Không dùng ngôn ngữ chung chung, sáo rỗng hay tối nghĩa. Hãy viết rõ ràng, sắc bén và dễ hiểu.\n"
            "- Cung cấp ít nhất 3 bước giải pháp (actionable steps) mang tính thực tiễn cao.\n"
            "- Bám sát phần Tri thức bên dưới, trích dẫn ID tri thức (ví dụ: NT-PRINCIPLE-0001) khi tham chiếu.\n"
            "- Nhận diện rõ các rủi ro hoặc thiên kiến có thể xảy ra và cách phòng tránh.\n\n"
            f"CÂU HỎI:\n{query}\n\n"
            f"TRI THỨC BỐI CẢNH:\n{context}"
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
            f"{_base_url().rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {_api_key()}"},
            json={
                "model": _model(),
                "messages": [
                    {"role": "system", "content": "Bạn là một chuyên gia phân tích tri thức."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["choices"][0]["message"]["content"]