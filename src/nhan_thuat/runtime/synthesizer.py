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
    
    gemini_keys = []
    
    primary = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if primary:
        gemini_keys.append(primary)
        
    for i in range(1, 6):
        key = (os.environ.get(f"GEMINI_API_KEY_{i}") or 
               os.environ.get(f"GOOGLE_API_KEY_{i}") or 
               os.environ.get(f"GEMINI_API_KEY{i}") or 
               os.environ.get(f"GOOGLE_API_KEY{i}") or "").strip()
        if key and key not in gemini_keys:
            gemini_keys.append(key)
            
    base_url = os.environ.get("GEMINI_BASE_URL", "").strip().rstrip("/") or DEFAULT_BASE_URL
    model = os.environ.get("GEMINI_MODEL", "").strip() or DEFAULT_MODEL
    
    # Auto-fix deprecated models
    if "2.5-flash" in model.lower() or "gemini-pro" in model.lower():
        model = "gemini-3.6-flash"
    
    for i, key in enumerate(gemini_keys):
        configs.append({
            "api_key": key,
            "base_url": base_url,
            "model": model,
            "provider_name": f"google-gemini-{i+1}" if len(gemini_keys) > 1 else "google-gemini",
        })
        
    groq_key = os.environ.get("GROQ_API_KEY", "").strip()
    if groq_key:
        groq_model = os.environ.get("GROQ_MODEL", "").strip() or "llama3-8b-8192"
        if "3.1-8b-instant" in groq_model.lower():
            groq_model = "llama3-8b-8192"
            
        configs.append({
            "api_key": groq_key,
            "base_url": "https://api.groq.com/openai/v1",
            "model": groq_model,
            "provider_name": "groq",
        })
        
    deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if deepseek_key:
        configs.append({
            "api_key": deepseek_key,
            "base_url": "https://api.deepseek.com/v1",
            "model": os.environ.get("DEEPSEEK_MODEL", "").strip() or "deepseek-chat",
            "provider_name": "deepseek",
        })

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if openai_key:
        openai_model = os.environ.get("OPENAI_MODEL", "").strip() or os.environ.get("NHAN_THUAT_LLM_MODEL", "").strip() or DEFAULT_MODEL
        if "2.5-flash" in openai_model.lower():
            openai_model = "gemini-3.6-flash"
            
        configs.append({
            "api_key": openai_key,
            "base_url": os.environ.get("OPENAI_BASE_URL", "").strip().rstrip("/") or DEFAULT_BASE_URL,
            "model": openai_model,
            "provider_name": "openai-compatible",
        })
        
    return configs


class KnowledgeSynthesizer:
    """Produces a synthesis for a query and its retrieved knowledge units."""

    def __init__(self, prompt_builder: PromptBuilder | None = None, timeout: int = 15) -> None:
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
            "Bạn là một Cố Vấn Chiến Lược & Nhân Sinh Cấp Cao, hiện thân cho trí tuệ Binh pháp, Nhân thuật và phong cách sống thâm trầm, từng trải.\n"
            "Nhiệm vụ của bạn là phân tích vô cùng SÂU SẮC, CHI TIẾT, ĐA CHIỀU và đưa ra CÁC GIẢI PHÁP HÀNH ĐỘNG cụ thể. KHÔNG ĐƯỢC viết vắn tắt hay qua loa.\n\n"
            f"TÌNH HUỐNG HIỆN TẠI CỦA NGƯỜI DÙNG: {query}\n\n"
            "--- CƠ SỞ TRI THỨC (KNOWLEDGE BASE) ---\n"
            "Dựa vào các tri thức sau đây để đưa ra lời khuyên:\n"
            f"{context}\n"
            "---\n\n"
            "CHỈ ĐẠO CỐT LÕI VỀ TƯ DUY & VĂN PHONG Á ĐÔNG:\n"
            "1. Tuyệt đối không ấn định mốc thời gian cứng nhắc. Hãy chia chiến lược theo Trình tự Binh thế (Thủ thế -> Lập thế -> Định cục).\n"
            "2. Văn phong Á Đông sâu sắc: Dùng trí tuệ nhân thuật, lấy tĩnh chế động. Ngôn từ đầm, mộc mạc, thấu hiểu nhân quả và tâm lý. Diễn đạt mượt mà, lưu loát, liền mạch.\n"
            "3. Thực chiến & Ranh giới: Phân tích đúng bản chất thực tế, ranh giới chịu đựng rõ ràng và kịch bản ứng phó sắc bén. Hãy viết dài và cặn kẽ để người dùng thực sự hiểu nguyên lý.\n"
            "4. TRÍCH DẪN TRI THỨC: BẮT BUỘC phải viết TÊN TIẾNG VIỆT ĐẦY ĐỦ của tri thức, sau đó đóng ngoặc mã ID (ví dụ: Quy luật Giá trị (NT-LAW-3201)).\n\n"
            "TRẢ LỜI BẰNG MARKDOWN THEO ĐÚNG CÁC PHẦN SAU (Mỗi phần phải viết thật chi tiết, có phân tích ngọn ngành):\n\n"
            "### 🔍 CHẨN ĐOÁN HÀNH VI\n"
            "- [Đánh giá sức ép cảm xúc, động cơ ngầm và bản chất cốt lõi của hành vi một cách sâu sắc và chi tiết].\n\n"
            "### 🚫 MẪU HÀNH VI CẦN TRÁNH\n"
            "- [Phân tích cặn kẽ các phản ứng sai lầm, rủi ro tâm lý thường gặp mà thân chủ dễ vướng phải].\n\n"
            "### ⚙️ CÁC BƯỚC HÀNH ĐỘNG CỤ THỂ\n"
            "- [Liệt kê các bước hành động thực chiến theo trình tự ưu tiên. Mỗi bước phải giải thích rõ tại sao làm vậy và làm như thế nào].\n\n"
            "### ⚠️ NHẬN DIỆN RỦI RO VÀ CÁCH PHÒNG TRÁNH\n"
            "- [Những rủi ro tiềm ẩn khi áp dụng giải pháp và kịch bản phòng bị chi tiết].\n\n"
            "### 📌 TỔNG KẾT VÀ KẾT LUẬN\n"
            "- [Thông điệp chốt hạ, khẳng định vị thế và nguyên tắc điều hướng cục diện bằng một câu nói hoặc đoạn văn súc tích, uy lực].\n\n"
            "### 📖 TRÍCH DẪN\n"
            "- [BẮT BUỘC liệt kê cụ thể các tri thức/quy luật đã sử dụng kèm ID].\n"
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