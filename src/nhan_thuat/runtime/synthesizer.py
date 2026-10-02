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
            "Bạn là Cố Vấn Chiến Lược & Quân Sư Thượng Thừa của Hệ thống Nhân Thuật. Phong cách tư vấn của bạn dung hợp trọn vẹn "
            "NGŨ ĐẠI HỆ HÌNH TRIẾT HỌC (Bản nguyên Đạo Gia - Khắc Kỷ, Nhân tính luận Nho - Tuân, Quyền lực Pháp Gia - Machiavellianism, "
            "Tâm thuật Quỷ Cốc Tử - Hùng biện, Binh pháp Tôn Tử - Lý thuyết trò chơi hiện đại).\n\n"
            "QUY TẮC TRÌNH BÀY & NGHỊ LUẬN (BẮT BUỘC):\n"
            "- Trình bày như một BÀI NGHỊ LUẬN CHIẾN LƯỢC SÂU SẮC, TRAU CHUỐT, phân tích tường tận, hồi quy quy nạp chặt chẽ, dẫn chứng cụ thể thuyết phục và lập luận sắc bén.\n"
            "- Khi dùng thuật ngữ cổ điển (Hình Danh Tham Đồng, Nhị Bỉnh, Bát Gian, Tâm Trai, Bách Hợp, Phi Kiềm, Nash Equilibrium...), "
            "phải giải thích bản chất thực tế trong ngoặc đơn.\n"
            "- Mỗi nhận định phải gắn chặt với tương quan quyền lực, tử huyệt lợi ích và kịch bản hành động cụ thể.\n\n"
            f"TÌNH HUỐNG THỰC TẾ CỦA NHÀ LÃNH ĐẠO: \"{query}\"\n\n"
            "--- CƠ SỞ TRI THỨC ĐỐI CHIẾU ---\n"
            f"{context}\n"
            "HÃY PHÂN TÍCH VÀ ĐƯA RA BẢN THAM MƯU CHIẾN LƯỢC BẰNG MARKDOWN THEO ĐÚNG 5 PHẦN CHUẨN MỰC SAU:\n\n"
            "### 🎯 TÓM TẮT ĐIỀU HÀNH\n"
            "- [3-4 gạch đầu dòng cô đọng nhất: Chuyện gì đang thực sự xảy ra dưới lớp vỏ bề mặt; Điều gì đang bị đe dọa (vị thế, uy tín, chi phí); Việc tối quan trọng cần làm ngay trong 24h].\n\n"
            "### 👁️ TỔNG QUAN TÌNH THẾ\n"
            "Trình bày như một BÀI NGHỊ LUẬN CHIẾN LƯỢC SÂU SẮC, TRAU CHUỐT (gồm tối thiểu 3 đoạn văn sâu sắc, dung hợp triết lý Đông Tây và thuật dụng nhân định thế):\n"
            "- **Đoạn 1 (Luận đề thế trận):** Không dừng lại ở hiện tượng bề mặt vụn vặt; hãy định vị thực chất cuộc diện này là gì trong tương quan lực lượng, cấu trúc quyền lực và dòng chảy kỳ vọng giữa các bên.\n"
            "- **Đoạn 2 (Biện giải chiều sâu & Ma sát tâm lý):** Bóc tách các dòng chảy ngầm: nỗi sợ hãi, động cơ lợi ích thực tế, xung đột nhận thức và bẫy thế cờ mà nếu người lãnh đạo ứng xử bằng cảm xúc nóng vội hoặc do dự thì cục diện sẽ biến tướng nguy hiểm ra sao.\n"
            "- **Đoạn 3 (Luận kết & Tâm thế định cục):** Đúc kết nguyên lý then chốt (kết hợp tư duy 'Tâm Trai', 'Lấy tĩnh chế động', 'Dichotomy of Control' với kỷ cương quản trị hiện đại), xác lập tâm thế của người nắm quyền chủ động để xoay chuyển cục diện.\n\n"
            "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM\n"
            "- **Phương pháp Hồi quy nhân quả:** Lần ngược từ phản ứng/lời nói bề mặt về áp lực vô hình và nỗi bất an tiềm thức của đối phương.\n"
            "- **Tam tầng lợi ích:**\n"
            "  * *Lợi ích tuyên bố (Declared):* Điều đối phương lớn tiếng đòi hỏi bề ngoài.\n"
            "  * *Lợi ích thực tế (Operational):* Mục tiêu thực dụng tối thiểu họ bắt buộc phải đạt được.\n"
            "  * *Lợi ích tâm lý & thể diện (Ego/Security):* Nỗi sợ bị xem thường hoặc mất quyền kiểm soát.\n"
            "- **Hệ quả nếu xử lý sai lầm:** Thế trận sẽ nghiêng về đâu và cái giá tổ chức phải trả.\n\n"
            "### ⚠️ 2. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH\n"
            "*Biện chứng phản đề và giải mã các bẫy nhận thức. Trình bày dưới dạng BẢNG (Markdown Table) gồm 3 cột:*\n"
            "| Tên Bẫy Nhận Thức | Biểu hiện dễ mắc phải (Lối mòn cảm xúc) | Hậu quả nhãn tiền trong thế trận |\n"
            "|---|---|---|\n"
            "| [Bẫy 1 - ví dụ: Ác cảm mất mát / Nôn nóng áp chế] | [Hành vi sai lầm] | [Tổn hại chiến lược] |\n"
            "| [Bẫy 2 - ví dụ: Neo kỳ vọng / Nhượng bộ cầu an] | [Hành vi sai lầm] | [Tổn hại chiến lược] |\n\n"
            "### ⚔️ 3. ĐÒN BẨY ĐỊNH CỤC & KỊCH BẢN LỜI THOẠI THỰC CHIẾN (VERBATIM SCRIPT)\n"
            "- **Đòn bẩy Tái đóng khung (Reframing) & Chiếc cầu vàng (Golden Bridge):** Cách thiết lập lối thoát danh dự có kiểm soát để đối phương tự nguyện bước sang thế hợp tác.\n"
            "- **Kịch bản Lời thoại mẫu từng câu chữ (Verbatim Script) 3 giai đoạn:**\n"
            "  * **Giai đoạn 1 (Tháo ngòi nổ & Thấu cảm chiến thuật):** *\"[Câu thoại mẫu chính xác dùng để làm nguội cơn giận hoặc thế đối đầu của đối phương]\"*\n"
            "  * **Giai đoạn 2 (Tái định vị ranh giới & Nắn dòng lợi ích):** *\"[Câu thoại mẫu chuyển dịch sự chú ý sang chi phí rủi ro chung và ranh giới không thể thương lượng]\"*\n"
            "  * **Giai đoạn 3 (Khóa thế & Chốt cam kết hành động):** *\"[Câu thoại mẫu chốt hạ điều kiện và xác lập thỏa thuận ràng buộc]\"*\n\n"
            "### 📌 CHỐT HẠ ĐỊNH CỤC\n"
            "> *[1-2 câu tuyên ngôn súc tích, mang tầm triết lý sắc bén để định hình tâm thế người lãnh đạo].*\n\n"
            "### 📖 TRÍCH DẪN TRI THỨC\n"
            "- [Liệt kê các tri thức/quy luật đã vận dụng kèm mã ID, ví dụ: Quy luật Giá trị (NT-LAW-3201), Binh pháp Tôn Tử (NT-MODEL-3202)].\n"
        )

    def _deterministic_synthesis(self, query: str, units: Iterable[KnowledgeUnit]) -> str:
        units_list = list(units)
        if not units_list:
            return "Không tìm thấy tri thức tương ứng trực tiếp trong hệ thống."

        top_units = units_list[:3]

        lines = [
            "### 🎯 TÓM TẮT ĐIỀU HÀNH",
            f"- Tình huống **\"{query}\"** được đối chiếu với {len(units_list)} tri thức và đại hệ hình triết học trong kho Nhân Thuật.",
        ]
        for u in top_units[:2]:
            summary_text = (u.summary or u.definition or "").strip()
            if summary_text:
                lines.append(f"- **{u.title} ({u.id})**: {summary_text}")
        lines.append(
            "- Việc cần làm ngay trong 24h: Giữ vững tâm thế bất biến, phong tỏa rò rỉ thông tin, "
            "kiểm tra lại cấu trúc quyền hạn và xác lập chiếc cầu vàng (lối thoát danh dự) trước khi ngồi vào bàn đàm phán."
        )

        # Xây dựng bài nghị luận chiến lược sâu sắc cho TỔNG QUAN TÌNH THẾ
        treatise_paras = [
            (
                f"Vấn đề **\"{query}\"** thoạt nhìn có vẻ là một xung đột hay biến cố vụ việc đơn lẻ, song khi đặt vào "
                "tọa độ quản trị và nhân tâm học, đây thực chất là sự đứt gãy hoặc xáo trộn trong tương quan giữa "
                "**Lợi ích cốt lõi**, **Cấu trúc quyền hạn** và **Dòng chảy kỳ vọng ngầm**. Mọi biểu hiện bề mặt như "
                "sự phản kháng, trì hoãn hay thái độ gay gắt chỉ là phần nổi của tảng băng chìm; gốc rễ nằm ở tâm lý thủ thế "
                "và sự phòng vệ tự nhiên của con người khi cảm nhận vùng an toàn hoặc quyền kiểm soát của họ bị đe dọa."
            )
        ]

        if top_units:
            evidence_points = []
            for u in top_units[:2]:
                text = (u.summary or u.definition or "").strip()
                if text:
                    evidence_points.append(f"quy luật **{u.title}** (`{u.id}`: *{text}*)")

            evidence_str = " cùng với ".join(evidence_points) if evidence_points else "các nguyên lý nền tảng của Nhân Thuật"
            treatise_paras.append(
                f"Soi chiếu dưới lăng kính triết học vận hành và quy luật tương quan lực lượng, tình thế này chịu sự tác động mang tính quyết định của {evidence_str}. "
                "Nếu nhà quản trị chỉ nhìn vào hiện tượng để phản ứng theo phản xạ tự nhiên — hoặc dùng uy quyền cứng nhắc để áp chế, "
                "hoặc nhượng bộ cảm tính để cầu an tạm thời — thì vô tình đều đẩy đối phương vào thế đối đầu triệt để hơn. "
                "Cái bẫy lớn nhất của người cầm quyền trong thời khắc này là biến một bài toán cấu trúc thành cuộc đấu tranh cá nhân, "
                "khiến tổ chức phải trả giá bằng sự xói mòn niềm tin, suy giảm uy quyền và chi phí điều hòa nội bộ tăng vọt."
            )
        else:
            treatise_paras.append(
                "Trong mọi thế trận giằng co, việc vội vã đưa ra phán quyết khi chưa thấu tỏ động cơ sâu kín của các bên "
                "luôn là mầm mống của thất bại chiến lược. Người lãnh đạo cần bóc tách rành mạch đâu là mâu thuẫn quyền lợi thật, "
                "đâu chỉ là sự tự ái nhận thức và phòng vệ tâm lý nhằm bảo vệ cái tôi đang bị tổn thương."
            )

        treatise_paras.append(
            "Do đó, định hướng giải pháp không phải là triệt hạ đối phương hay thỏa hiệp vô nguyên tắc, mà là nghệ thuật "
            "**'Lập Thế Trước Khi Xuất Ngôn, Dựng Khung Trước Khi Dụng Nhân'**. Bậc cao thủ về nhân thuật luôn giữ tâm thế "
            "**'Tâm Trai'** — tĩnh lặng như mặt nước hồ để nhìn xuyên lớp sương mù cảm xúc, xác lập ranh giới kỷ cương không thể thương lượng, "
            "đồng thời khéo léo chừa ra một lối thoát danh dự (Chiếc Cầu Vàng - Golden Bridge) để đối phương chủ động chuyển hóa từ thế đối kháng sang đồng thuận."
        )

        lines.extend([
            "",
            "### 👁️ TỔNG QUAN TÌNH THẾ",
            "\n\n".join(treatise_paras),
            "",
            "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM",
            "- **Phương pháp Hồi quy nguyên nhân:** Hành vi và lời nói của đối phương thực chất là cơ chế tự vệ trước nỗi sợ mất quyền kiểm soát hoặc áp lực phải chứng minh năng lực trước cấp trên.",
            "- **Tam tầng lợi ích chi phối cuộc diện:**",
            f"  * *Lợi ích tuyên bố (Declared):* Yêu cầu đanh thép liên quan đến vụ việc (như điều khoản, tiến độ, hoặc sự bất mãn bộc phát).",
            "  * *Lợi ích thực tế (Operational):* Sự bảo đảm rằng công việc của họ không bị đình trệ, rủi ro pháp lý/tài chính được khoanh vùng an toàn.",
            "  * *Lợi ích tâm lý & thể diện (Ego/Security):* Nhu cầu được tôn trọng vị thế, không bị cảm giác bị chèn ép hay tước đoạt tiếng nói.",
            "- **Hệ quả nếu xử lý sai lầm:** Nếu dùng uy lực đè bẹp, sự phản kháng sẽ chuyển thành ngầm phá hoại; nếu nhượng bộ vô nguyên tắc, vị thế đàm phán của tổ chức sẽ sụp đổ hoàn toàn.",
            "",
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
            "| Tên Bẫy Nhận Thức | Biểu hiện dễ mắc phải (Lối mòn cảm xúc) | Hậu quả nhãn tiền trong thế trận |",
            "|---|---|---|",
        ])

        collected_risks: list[str] = []
        for u in units_list:
            for risk in (u.risks or ()):
                text = str(risk).strip()
                if text:
                    collected_risks.append(text)

        if collected_risks:
            for idx, risk in enumerate(collected_risks[:3]):
                lines.append(f"| Bẫy {idx + 1} (Rủi ro cấu trúc) | {risk} | Tổn hại uy quyền, đứt gãy niềm tin và chi phí phục hồi tăng cao |")
        lines.append("| Bẫy cảm xúc vội vã (Emotional Reactivity) | Phản ứng bằng cơn thịnh nộ hoặc dùng quyền lực cứng để bức ép ngay lập tức | Mất vị thế đàm phán đạo đức, đẩy đối phương sang thế liều chết chống đối ngầm |")
        lines.append("| Bẫy nhượng bộ vô điều kiện (Appeasement Fallacy) | Nhân nhượng khi chưa xác lập được ranh giới và cam kết đối ứng | Tạo tiền lệ xấu, biến mình thành con mồi cho những đợt ép tiếp theo |")

        lines.extend([
            "",
            "### ⚔️ 3. ĐÒN BẨY ĐỊNH CỤC & KỊCH BẢN LỜI THOẠI THỰC CHIẾN (VERBATIM SCRIPT)",
            "- **Đòn bẩy Tái đóng khung (Reframing):** Chuyển dịch thế trận từ 'Cuộc đối đầu nhị nguyên Tôi - Anh' sang 'Hai bên cùng ngồi chung thuyền đối diện với rủi ro chung của dự án'.",
            "- **Kỹ nghệ Chiếc cầu vàng (Golden Bridge):** Mở ra một lối thoát danh dự cho đối phương để họ rút lui mà không bị mất mặt trước tập thể.",
            "",
            "**Kịch bản Lời thoại mẫu từng câu chữ (Verbatim Script) 3 giai đoạn:**",
            "1. **Pha 1: Tháo ngòi nổ & Thấu cảm chiến thuật (Tactical Empathy):**",
            f"   > *\"Tôi hoàn toàn hiểu vì sao anh lại bức xúc và kiên quyết như vậy trong vấn đề này. Nếu đứng ở vị trí gánh vác trách nhiệm của anh, có thể tôi cũng sẽ đặt ra những yêu cầu khắt khe tương tự. Chúng ta hãy cùng ngồi lại để nhìn thấu đáo toàn bộ bức tranh.\"*",
            "2. **Pha 2: Tái định vị ranh giới & Nắn dòng lợi ích (Reframing Boundaries):**",
            "   > *\"Tuy nhiên, nguyên tắc cốt lõi về chất lượng và kỷ cương vận hành là ranh giới bất biến mà cả hai bên đều không thể đánh đổi. Nếu phá vỡ ranh giới này, thiệt hại lớn nhất không chỉ là con số trước mắt mà là uy tín lâu dài của cả tôi và anh.\"*",
            "3. **Pha 3: Khóa thế & Chốt cam kết hành động (Equilibrium Closure):**",
            "   > *\"Để đảm bảo quyền lợi cao nhất cho anh mà không phá vỡ quy chuẩn chung, tôi đề xuất giải pháp trung dung có kiểm soát: Chúng ta giữ nguyên khung nguyên tắc, nhưng tôi sẽ bố trí cơ chế hỗ trợ nguồn lực bổ sung này cho anh. Anh thấy phương án này có giải tỏa được nút thắt lớn nhất của anh không?\"*",
            "",
            "### 📌 CHỐT HẠ ĐỊNH CỤC",
            "> *\"Người nắm quyền chủ động không thắng bằng sự áp đặt ồn ào, mà định đoạt cục diện bằng cấu trúc ranh giới bất biến và nghệ thuật mở lối thoát danh dự cho đối phương.\"*",
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