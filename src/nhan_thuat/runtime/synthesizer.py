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


class ProviderError(RuntimeError):
    """Raised when all configured LLM providers fail or none is configured."""


def _is_valid_api_key(key: str) -> bool:
    if not key:
        return False
    key_clean = key.strip().lower()
    if key_clean.startswith("your_") or "your_api_key" in key_clean or "your_google_api_key" in key_clean or key_clean == "none":
        return False
    return len(key_clean) > 8


def get_provider_configs() -> list[dict[str, str]]:
    configs = []
    
    # 1. Deepseek / OpenAI
    openai_key = os.environ.get("DEEPSEEK_API_KEY", "").strip() or os.environ.get("OPENAI_API_KEY", "").strip()
    if _is_valid_api_key(openai_key):
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
    if _is_valid_api_key(google_key):
        model = os.environ.get("NHAN_THUAT_LLM_MODEL", "").strip() or os.environ.get("GEMINI_MODEL", "").strip() or DEFAULT_MODEL
        configs.append({
            "api_key": google_key,
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "model": model,
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
            "Bạn là Cố Vấn Chiến Lược & Nhân Thuật Cấp Cao. Phong cách tư vấn của bạn dung hợp giữa "
            "TRÍ TUỆ ĐÔNG PHƯƠNG (Binh pháp, thấu hiểu nhân tâm) và "
            "KHOA HỌC QUẢN TRỊ HIỆN ĐẠI (Tâm lý học hành vi, đàm phán, ranh giới pháp lý).\n\n"
            "QUY TẮC TRÌNH BÀY (bắt buộc):\n"
            "- Viết tiếng Việt rõ ràng, câu ngắn, dễ hiểu cho một nhà quản lý bận rộn. KHÔNG dùng văn phong đại ngôn, không nói đạo lý suông.\n"
            "- Khi dùng thuật ngữ cổ (ví dụ: Hình Danh Tương Phù, Nhị Bỉnh, Bát Gian, Tâm Trai...), "
            "phải giải thích ngay trong ngoặc bằng tiếng Việt đời thường.\n"
            "- Mỗi nhận định phải đi kèm việc cần làm cụ thể.\n\n"
            f"TÌNH HUỐNG THỰC TẾ CỦA NGƯỜI DÙNG: {query}\n\n"
            "--- CƠ SỞ TRI THỨC ĐỐI CHIẾU ---\n"
            f"{context}\n"
            "HÃY PHÂN TÍCH VÀ ĐƯA RA LỜI THAM MƯU BẰNG MARKDOWN THEO ĐÚNG 5 PHẦN SAU:\n\n"
            "### 🎯 TÓM TẮT ĐIỀU HÀNH\n"
            "- [3-4 gạch đầu dòng ngắn nhất có thể, ngôn ngữ bình dân: chuyện gì đang thực sự xảy ra; "
            "điều gì đang bị đe dọa; việc quan trọng nhất cần làm ngay. Người đọc chỉ đọc phần này cũng phải hiểu và biết phải làm gì].\n\n"
            "### 👁️ TỔNG QUAN TÌNH THẾ\n"
            "- [1 đoạn văn 3-4 câu tóm tắt mức độ nghiêm trọng và bản chất cốt lõi của sự việc].\n\n"
            "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM\n"
            "- **Hiện tượng bề mặt:** [Vấn đề nhìn thấy bằng mắt thường, hành vi đang diễn ra].\n"
            "- **Động cơ ngầm ẩn:** [Lợi ích cốt lõi, nỗi sợ hãi hoặc định kiến thực sự đang chi phối đối phương].\n"
            "- **Hệ quả nếu không xử lý:** [Thế cờ sẽ nghiêng về đâu, tổ chức sẽ trả giá thế nào].\n\n"
            "### ⚠️ 2. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH\n"
            "*Trình bày dưới dạng BẢNG (Markdown Table) gồm 3 cột:*\n"
            "| Tên Bẫy | Biểu hiện dễ mắc phải | Hậu quả nhãn tiền |\n"
            "|---|---|---|\n"
            "| [Tên bẫy 1] | [Hành vi bốc đồng, cảm xúc] | [Hậu quả] |\n"
            "| [Tên bẫy 2] | [Sai lầm trong đánh giá] | [Hậu quả] |\n\n"
            "### 📌 3. CHỐT HẠ ĐỊNH CỤC\n"
            "- [Tối đa 1-2 câu tuyên ngôn súc tích để định hướng hành động].\n\n"
            "### 📖 TRÍCH DẪN TRI THỨC\n"
            "- [Liệt kê ngắn gọn các tri thức/quy luật đã vận dụng kèm mã ID, ví dụ: Quy luật Giá trị (NT-LAW-3201)].\n"
        )

    def _deterministic_synthesis(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        units_list = list(units)
        if not units_list:
            return "Không tìm thấy tri thức tương ứng trực tiếp trong hệ thống."

        top_units = units_list[:3]

        lines = [
            "### 🎯 TÓM TẮT ĐIỀU HÀNH",
            f"- Tình huống **\"{query}\"** được đối chiếu với {len(units_list)} tri thức liên quan trong kho Nhân Thuật.",
        ]
        for u in top_units[:2]:
            summary_text = (u.summary or u.definition or "").strip()
            if summary_text:
                lines.append(f"- **{u.title} ({u.id})**: {summary_text}")
        lines.append(
            "- Việc cần làm ngay: xác định rõ lợi ích thật của từng bên, kiểm tra lại cấu trúc "
            "quyền hạn và chọn một hành động cụ thể có thể kiểm chứng được."
        )
        lines.extend([
            "",
            "### 👁️ TỔNG QUAN TÌNH THẾ",
            (
                f"Vấn đề **\"{query}\"** cần được nhìn như một chuỗi quan hệ giữa lợi ích, quyền hạn và "
                "thông tin — không chỉ là sự việc bề mặt. Các tri thức dưới đây cho biết quy luật nào "
                "đang vận hành phía sau tình huống."
            ),
            "",
            "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM",
        ])

        for u in top_units:
            lines.append(f"**{u.title}** — `{u.id}` (miền `{u.primary_domain}`):")
            if u.summary:
                lines.append(f"- *Bản chất:* {u.summary}")
            if u.definition and u.definition != u.summary:
                lines.append(f"- *Cơ chế:* {u.definition}")
            mechanism_items = [str(item) for item in (u.mechanism or ()) if str(item).strip()]
            if mechanism_items:
                lines.append(f"- *Cách vận hành:* {' → '.join(mechanism_items[:3])}")
            lines.append("")

        lines.extend([
            "### ⚠️ 2. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH",
            "| Tên Bẫy | Biểu hiện dễ mắc phải | Hậu quả nhãn tiền |",
            "|---|---|---|",
        ])

        collected_risks: list[str] = []
        for u in units_list:
            for risk in (u.risks or ()):
                text = str(risk).strip()
                if text:
                    collected_risks.append(text)

        if collected_risks:
            for idx, risk in enumerate(collected_risks[:4]):
                lines.append(f"| Rủi ro {idx + 1} | {risk} | Tổn hại uy tín, dòng tiền hoặc quan hệ |")
        else:
            lines.append("| Bẫy cảm xúc vội vã | Phản ứng bằng cảm tính hoặc dùng quyền lực cứng để bức ép | Mất vị thế đàm phán, tạo chống đối ngầm |")
            lines.append("| Nhượng bộ vô điều kiện | Nhân nhượng khi chưa xử lý được gốc vấn đề | Tạo tiền lệ xấu, phá vỡ kỷ cương |")

        lines.extend([
            "",
            "### 📌 3. CHỐT HẠ ĐỊNH CỤC",
            "> *\"Người nắm quyền chủ động không thắng bằng áp đặt ồn ào, mà định đoạt cục diện bằng cấu trúc và điểm đòn bẩy.\"*",
            "",
            "### 📖 TRÍCH DẪN TRI THỨC",
        ])
        for u in units_list[:4]:
            unit_type = str(getattr(u, "type", "unit")).upper()
            lines.append(f"- `{u.id}`: **{u.title}** ({unit_type}) — Miền: {u.primary_domain}")

        return "\n".join(lines)

    def generate_text(self, prompt: str) -> str:
        """Call providers with failover and return just the text."""
        configs = get_provider_configs()
        if not configs:
            raise ProviderError("No providers configured")

        errors = []
        for config in configs:
            try:
                return self._call_provider(prompt, config)
            except Exception as e:  # noqa: BLE001 - failover across any provider failure
                errors.append(f"{config['provider_name']}: {e}")

        raise ProviderError(f"All providers failed: {' | '.join(errors)}")

    def generate_json(self, prompt: str) -> dict[str, Any]:
        """Call providers and force JSON return, parsing it safely."""
        configs = get_provider_configs()
        if not configs:
            raise ProviderError("No providers configured")

        errors = []
        for config in configs:
            try:
                json_prompt = prompt + "\n\nCRITICAL: You MUST return ONLY valid JSON. Do not wrap it in markdown block quotes like ```json ... ```. Just return the raw JSON object."
                text = self._call_provider(json_prompt, config)

                # Cleanup common markdown code block wrapping if LLM ignores instruction
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                elif text.startswith("```"):
                    text = text[3:]
                text = text.removesuffix("```")
                text = text.strip()

                import json
                return json.loads(text)
            except Exception as e:  # noqa: BLE001 - failover across any provider failure
                errors.append(f"{config['provider_name']}: {e}")

        raise ProviderError(f"All providers failed JSON generation: {' | '.join(errors)}")

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
            raise ProviderError(f"{e} - Response: {response.text}") from e
        payload = response.json()
        return payload["choices"][0]["message"]["content"]