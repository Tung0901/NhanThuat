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


def get_provider_configs() -> list[dict[str, str]]:
    configs = []
    
    # 1. Deepseek / OpenAI
    openai_key = os.environ.get("DEEPSEEK_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com").strip()
        model = os.environ.get("NHAN_THUAT_LLM_MODEL", "deepseek-chat").strip()
        configs.append({
            "api_key": openai_key,
            "base_url": base_url,
            "model": model,
            "provider_name": "deepseek",
        })

    # 2. Gemini / Google
    google_key = os.environ.get("GOOGLE_API_KEY", "").strip() or os.environ.get("GEMINI_API_KEY", "").strip()
    if google_key:
        configs.append({
            "api_key": google_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model": "gemini-3.6-flash",
            "provider_name": "google-gemini",
        })
    
    return configs


class KnowledgeSynthesizer:
    """Produces a synthesis for a query and its retrieved knowledge units."""

    def __init__(self, prompt_builder: PromptBuilder | None = None, timeout: int = 60) -> None:
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.timeout = timeout

    @property
    def provider_configured(self) -> bool:
        return len(get_provider_configs()) > 0

    def synthesize(self, query: str, units: Iterable[KnowledgeUnit]) -> dict[str, Any]:
        """Return a synthesis result with mode, citations, and audit."""
        units_list = list(units)[:5]
        citations = [
            {"id": unit.id, "title": unit.title, "domain": unit.primary_domain}
            for unit in units_list
        ]
        prompt = self._build_prompt(query, units_list)
        correlation_id = f"CORR-LLM-{uuid.uuid4().hex[:8].upper()}"

        configs = get_provider_configs()
        if not configs:
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
                    "Chưa cấu hình LLM synthesis. "
                    "Đang hiển thị dòng truy xuất tri thức deterministic."
                ),
            }

        started = time.monotonic()
        errors = []

        for config in configs:
            try:
                text = self._call_provider(prompt, config)
                latency_ms = int((time.monotonic() - started) * 1000)
                return {
                    "mode": "llm",
                    "synthesis": text,
                    "citations": citations,
                    "audit": {
                        "correlation_id": correlation_id,
                        "provider": config["provider_name"],
                        "model": config["model"],
                        "latency_ms": latency_ms,
                        "prompt": prompt,
                    },
                }
            except Exception as exc:  # noqa: BLE001
                err_msg = str(exc)
                errors.append(f"{config['provider_name']}: {err_msg}")
                print(f"[ERROR] LLM Provider {config['provider_name']} call failed: {exc}")

        # If all providers fail, fall back to deterministic
        latency_ms = int((time.monotonic() - started) * 1000)
        warning_msg = (
            f"Lỗi khi gọi TẤT CẢ LLM providers ({' | '.join(errors)}); đã chuyển sang dòng truy xuất deterministic."
        )

        synthesis_text = self._deterministic_synthesis(query, units_list)
        # Removed appending the raw warning_msg to synthesis_text so it doesn't leak to the end-user UI
        
        return {
            "mode": "deterministic",
            "synthesis": synthesis_text,
            "citations": citations,
            "audit": {
                "correlation_id": correlation_id,
                "provider": "deterministic",
                "model": "fallback",
                "latency_ms": latency_ms,
                "prompt": prompt,
                "error": " | ".join(errors),
            },
            "warning": warning_msg,
        }

    def _build_prompt(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        context = self.prompt_builder.build_context(units, format_type="markdown")
        return (
            "Bạn là Cố Vấn Chiến Lược & Nhân Thuật Cấp Cao. Phong cách tư vấn của bạn dung hợp hoàn hảo giữa "
            "TRÍ TUỆ ĐÔNG PHƯƠNG (Binh pháp, thấu hiểu nhân tâm, lấy tĩnh chế động) và "
            "KHOA HỌC QUẢN TRỊ HIỆN ĐẠI (Tâm lý học hành vi, đàm phán FBI, ranh giới pháp lý & đòn bẩy dòng tiền).\n\n"
            "NGUYÊN TẮC BẤT BIẾN: Tuyệt đối không nói đạo lý suông hay mơ hồ. Mỗi phân tích phải đi kèm giải pháp hành động cụ thể.\n\n"
            f"TÌNH HUỐNG THỰC TẾ CỦA NGƯỜI DÙNG: {query}\n\n"
            "--- CƠ SỞ TRI THỨC ĐỐI CHIẾU ---\n"
            f"{context}\n"
            "---\n\n"
            "HÃY PHÂN TÍCH VÀ ĐƯA RA LỜI THAM MƯU BẰNG MARKDOWN THEO ĐÚNG 4 PHẦN MẠCH LẠC SAU:\n\n"
            "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM\n"
            "- [Đánh giá chính xác bản chất tâm lý, động cơ ẩn giấu và thế cục hiện tại của các bên. Chỉ ra quy luật nhân thuật đang chi phối].\n\n"
            "### ⚙️ 2. KỊCH BẢN HÀNH ĐỘNG THỰC CHIẾN (TỪNG BƯỚC CỤ THỂ)\n"
            "- **Bước 1 (Thủ Thế - Bảo toàn vị thế & Khóa rủi ro):** [Hành động cụ thể cần làm ngay].\n"
            "- **Bước 2 (Lập Thế - Đòn bẩy thương lượng & Lời thoại mẫu):** [Gợi ý nguyên văn câu thoại hoặc văn bản giao tiếp sắc bén, chuẩn tâm lý đàm phán hiện đại].\n"
            "- **Bước 3 (Định Cục - Chốt hạ thỏa thuận):** [Cách thức đóng thỏa thuận đảm bảo lợi ích lâu dài].\n\n"
            "### ⚠️ 3. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH\n"
            "- [Những phản ứng bốc đồng, bẫy cảm xúc hoặc sơ hở đàm phán mà người dùng tuyệt đối không được mắc phải].\n\n"
            "### 📌 4. CHỐT HẠ ĐỊNH CỤC\n"
            "- [Thông điệp đúc kết vị thế và nguyên tắc điều hướng cục diện bằng một câu nói hoặc đoạn văn ngắn đầy uy lực].\n\n"
            "### 📖 TRÍCH DẪN TRI THỨC\n"
            "- [Liệt kê các tri thức/quy luật đã vận dụng kèm mã ID, ví dụ: Binh Pháp Tôn Tử, Quy luật Giá trị (NT-LAW-3201)].\n"
        )

    def _deterministic_synthesis(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        units_list = list(units)
        if not units_list:
            return "Không có tri thức liên quan."
        names = ", ".join(f"**{u.title}** ({u.id})" for u in units_list[:3])
        return (
            f"### Khảo cứu {len(units_list)} tri thức tham khảo\n\n"
            f"Em đã rà soát nhanh qua các góc nhìn liên quan ({names}). "
            "Dưới đây là một vài gợi ý từ hệ thống để anh cân nhắc nhé."
        )

    def generate_text(self, prompt: str) -> str:
        """Call providers with failover and return just the text."""
        configs = get_provider_configs()
        if not configs:
            raise Exception("No providers configured")
        
        errors = []
        for config in configs:
            try:
                return self._call_provider(prompt, config)
            except Exception as e:
                errors.append(f"{config['provider_name']}: {e}")
                
        raise Exception(f"All providers failed: {' | '.join(errors)}")

    def _call_provider(self, prompt: str, config: dict[str, str]) -> str:
        response = requests.post(
            f"{config['base_url']}/chat/completions",
            headers={"Authorization": f"Bearer {config['api_key']}"},
            json={
                "model": config["model"],
                "messages": [
                    {"role": "system", "content": "Bạn là một chuyên gia phân tích tri thức."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.4,
            },
            timeout=self.timeout,
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise Exception(f"{e} - Response: {response.text}") from e
        payload = response.json()
        return payload["choices"][0]["message"]["content"]