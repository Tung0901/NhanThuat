"""
Executive Sparring Engine for NhanThuat (Milestone Phase 3).
Orchestrates multi-turn adversarial roleplay, counter-argument generation,
and strategic coaching using 9 Philosophy Lenses and Hybrid RAG retrieval.
"""

from __future__ import annotations

import uuid
from typing import Any, Callable

from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.rag.hybrid_retriever import HybridRetriever
from nhan_thuat.storage.db import DatabaseManager
from nhan_thuat.storage.models import SparringMessage, SparringSession


def default_route_philosophy(text: str) -> str:
    """Built-in zero-dependency philosophy router for NhanThuat engine."""
    t = text.lower()
    if any(k in t for k in ["hợp đồng", "vi phạm", "tiến độ", "chậm", "phạt", "chế tài", "kỷ luật", "vật tư", "quy trình", "nghĩa vụ"]):
        return "LEGALISM"
    if any(k in t for k in ["giá", "đắt", "báo giá", "chi phí", "từ chối", "khách hàng", "chiết khấu", "thuyết phục", "lập luận"]):
        return "RHETORIC"
    if any(k in t for k in ["thế trận", "đối thủ", "đòn bẩy", "bất đối xứng", "chiến lược", "tấn công", "phòng thủ", "rút lui", "binh pháp"]):
        return "SUNZI"
    if any(k in t for k in ["bực", "tức giận", "áp lực", "bình tâm", "cảm xúc", "nghịch cảnh", "kiểm soát", "khắc kỷ"]):
        return "STOICISM"
    if any(k in t for k in ["nhân sự", "đào tạo", "khuyên học", "uốn nắn", "tiêu chuẩn", "định phần", "lễ", "tổ đội"]):
        return "XUNZI"
    return "LEGALISM"


class SparringEngine:
    """
    Stateful Executive Sparring Co-Pilot Engine.
    Simulates adversarial counterpart, challenges executive blindspots, and cites knowledge foundations.
    """

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        knowledge_engine: KnowledgeEngine | None = None,
        hybrid_retriever: HybridRetriever | None = None,
        philosophy_router: Any | None = None,
    ) -> None:
        self.db = db_manager or DatabaseManager()
        self.engine = knowledge_engine or KnowledgeEngine()
        self.retriever = hybrid_retriever or HybridRetriever(units=list(self.engine.units_by_id.values()))
        self.router = philosophy_router

    def start_session(
        self,
        title: str,
        philosophy_lens: str = "auto",
        initial_context: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SparringSession:
        """Initialize a new sparring session."""
        session = self.db.create_session(
            title=title,
            philosophy_lens=philosophy_lens,
            metadata=metadata or {},
        )
        if initial_context:
            self.db.add_message(
                session_id=session.id,
                role="system",
                content=f"Bối cảnh khởi tạo phiên đấu trí: {initial_context}",
                metadata={"type": "context_seed"},
            )
        return session

    def process_turn(
        self,
        session_id: str,
        user_message: str,
        override_lens: str | None = None,
    ) -> dict[str, Any]:
        """
        Process a single sparring turn:
        1. Save user message.
        2. Identify philosophy lens & retrieve counter-knowledge via Hybrid RAG.
        3. Formulate adversarial counter-argument + strategic coaching advice.
        4. Save assistant response and return full turn payload.
        """
        session = self.db.get_session(session_id)
        if not session:
            # Auto-create session if not exists
            session = self.start_session(title=user_message[:50], philosophy_lens=override_lens or "auto")
            session_id = session.id

        # 1. Save User Message
        user_msg = self.db.add_message(
            session_id=session_id,
            role="user",
            content=user_message,
        )

        # 2. Determine Philosophy Lens
        active_lens = override_lens or session.philosophy_lens
        if active_lens == "auto":
            if self.router is not None and hasattr(self.router, "route"):
                route_res = self.router.route({
                    "scenario_type": "general",
                    "intent": user_message,
                    "keywords": user_message.split(),
                })
                active_lens = route_res.get("primary_philosophy", "LEGALISM").upper()
            else:
                active_lens = default_route_philosophy(user_message)

        # 3. Hybrid RAG Retrieval for relevant counter-knowledge
        retrieval_res = self.retriever.retrieve(
            query=user_message,
            top_k=3,
            expand_relations=True,
        )
        matched_units = retrieval_res.primary_units
        matched_unit_ids = [getattr(u, "id", getattr(u, "unit_id", "")) for u in matched_units]

        # 4. Generate Adversarial Sparring Response
        response_text, citations = self._generate_sparring_response(
            user_text=user_message,
            lens=active_lens,
            units=matched_units,
            related_map=retrieval_res.related_units_map,
        )

        # 5. Save Assistant Message
        assistant_msg = self.db.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            matched_unit_ids=matched_unit_ids,
            metadata={
                "philosophy_lens": active_lens,
                "latency_ms": retrieval_res.total_latency_ms,
            },
        )

        return {
            "status": "success",
            "session_id": session_id,
            "user_message_id": user_msg.id,
            "assistant_message_id": assistant_msg.id,
            "philosophy_lens": active_lens,
            "response": response_text,
            "matched_unit_ids": matched_unit_ids,
            "citations": citations,
            "latency_ms": retrieval_res.total_latency_ms,
        }

    def _generate_sparring_response(
        self,
        user_text: str,
        lens: str,
        units: list[Any],
        related_map: dict[str, Any],
    ) -> tuple[str, list[dict[str, str]]]:
        """Synthesize sharp 2-part sparring dialogue with citations."""
        citations = []
        for u in units:
            uid = getattr(u, "id", getattr(u, "unit_id", ""))
            raw = u.raw if hasattr(u, "raw") and u.raw else getattr(u, "raw_data", {})
            title = str(getattr(u, "title", raw.get("title", uid)))
            domain = str(getattr(u, "primary_domain", getattr(u, "domain", raw.get("primary_domain", ""))))
            citations.append({"id": uid, "title": title, "domain": domain})

        primary_unit_str = f"[{citations[0]['id']} - {citations[0]['title']}]" if citations else "NT-LAW-0001"

        # Specialized Lens Personas
        if lens == "LEGALISM":
            adversarial_text = (
                f"Lập luận của bạn đang quá cả nể và dựa dẫm vào lời hứa cảm tính! "
                f"Trong quản trị và hợp đồng, lời nói không có biên bản tương đương với hư vô. "
                f"Nếu bạn nhượng bộ lúc này mà không siết chặt chế tài, đối tác sẽ tiếp tục kéo giãn giới hạn vi phạm. "
                f"Bạn đang để doanh nghiệp gánh chịu 100% rủi ro tiến độ và tài chính."
            )
            strategy_text = (
                f"- **Sơ hở cốt lõi:** Thiếu mốc thời hạn ràng buộc (Hard Deadline) và thiếu chế tài phạt lũy tiến.\n"
                f"- **Căn cứ tri thức đối trọng:** Cần kích hoạt ngay {primary_unit_str} và nguyên tắc 'Hình Danh Tham Đồng'.\n"
                f"- **Lời thoại lật ngược thế cờ:** *'Chúng tôi ghi nhận khó khăn của Quý vị, nhưng mọi phát sinh bắt buộc phải căn cứ theo Điều khoản Hợp đồng. Yêu cầu hoàn tất xử lý trước 12h00 trưa mai, quá thời hạn này Ban Quản lý sẽ tự động áp dụng chế tài phạt 0.5%/ngày và giữ thanh toán đợt 2.'*"
            )
        elif lens == "RHETORIC":
            adversarial_text = (
                f"Bạn đang mắc bẫy 'Khung Chi Phí' do đối phương giăng ra! "
                f"Khi đối phương chê giá đắt hoặc đòi chiết khấu, việc bạn vội vã phân trần hoặc hạ giá chỉ chứng minh giải pháp của bạn bị thổi phồng giá trị lúc đầu. "
                f"Bạn đang ở thế phòng thủ bị động và để đối phương nắm toàn quyền dẫn dắt cuộc thương thảo."
            )
            strategy_text = (
                f"- **Sơ hở cốt lõi:** Đối đáp trên tiêu chí 'Số tiền bỏ ra hôm nay' thay vì chuyển dịch sang 'Tổng chi phí vận hành 3 năm (TCO)'.\n"
                f"- **Căn cứ tri thức đối trọng:** Áp dụng {primary_unit_str} và kỹ thuật 'Rút củi đáy nồi (Reframing)'.\n"
                f"- **Lời thoại lật ngược thế cờ:** *'Tiêu chí tiết kiệm ngân sách của Anh/Chị hoàn toàn chính xác. Nhưng nếu chọn giải pháp rẻ hơn 15% để rồi chịu rủi ro sập hệ thống và bảo trì sau 6 tháng với chi phí gấp 3 lần, Anh/Chị có sẵn sàng đánh đổi không? Bên em không bán giá rẻ nhất, bên em bảo đảm dòng tiền an toàn nhất.'*"
            )
        elif lens == "SUNZI":
            adversarial_text = (
                f"Bạn đang tấn công trực diện vào điểm mạnh của đối thủ khi thực lực chưa chuẩn bị đủ! "
                f"Binh pháp dạy: 'Bất chiến tự nhiên thành', người giỏi dụng binh thì lập thế bất bại trước khi đòi đánh thắng. "
                f"Cách tiếp cận hiện tại của bạn là hành động hấp tấp, dễ biến xung đột cục bộ thành tổn thất toàn diện cho cả hai bên."
            )
            strategy_text = (
                f"- **Sơ hở cốt lõi:** Lập thế trận chưa kín kẽ, để lộ điểm yếu về thời gian và áp lực dòng tiền.\n"
                f"- **Căn cứ tri thức đối trọng:** Vận dụng {primary_unit_str} - Chiến lược Đòn bẩy Bất đối xứng.\n"
                f"- **Lời thoại lật ngược thế cờ:** *'Thay vì đối đầu trực diện, hãy chủ động lùi một bước để củng cố đồng minh và nguồn lực dự phòng (Plan B), buộc đối phương phải thương lượng khi họ mất dần lợi thế thời gian.'*"
            )
        elif lens == "STOICISM":
            adversarial_text = (
                f"Bạn đang bị cảm xúc bực bội và phản xạ tự ái chi phối quyết định! "
                f"Hành vi vô lý của đối tác hay sự cố bất ngờ là ngoại cảnh nằm ngoài 'Vòng tròn kiểm soát' của bạn. "
                f"Nếu bạn để cơn giận dẫn dắt lời nói, bạn đã tự giao chìa khóa tâm trí của mình vào tay đối phương."
            )
            strategy_text = (
                f"- **Sơ hở cốt lõi:** Đồng hóa cái tôi với sự cố khách quan.\n"
                f"- **Căn cứ tri thức đối trọng:** Áp dụng {primary_unit_str} và nguyên tắc 'Phân định Vòng tròn Kiểm soát'.\n"
                f"- **Lời thoại lật ngược thế cờ:** *'Hít một hơi thở sâu, tách rời cảm xúc cá nhân khỏi lợi ích cốt lõi của tổ chức. Tập trung 100% vào việc kiểm soát những gì mình làm được: Chuẩn bị phương án B và bảo vệ quyền lợi hợp pháp.'*"
            )
        else:  # Xunzi / Confucian / General
            adversarial_text = (
                f"Phương án của bạn giải quyết được phần ngọn nhưng chưa chạm vào gốc rễ của mâu thuẫn! "
                f"Vi phạm quy trình hay mâu thuẫn nhân sự xuất phát từ thói quen thiếu rèn nắn tiêu chuẩn và ranh giới vai trò lỏng lẻo. "
                f"Nếu chỉ dùng mệnh lệnh hành chính mà không chuẩn hóa lại quy chuẩn ('Dùng Lễ Định Phần'), sự cố tương tự sẽ lặp lại."
            )
            strategy_text = (
                f"- **Sơ hở cốt lõi:** Thiếu quy chuẩn hóa vai trò và lộ trình đào tạo nâng chuẩn.\n"
                f"- **Căn cứ tri thức đối trọng:** Áp dụng {primary_unit_str} (Tuân Tử - Khuyên Học & Định Phần).\n"
                f"- **Lời thoại lật ngược thế cờ:** *'Xác lập lại chuẩn mực vận hành rõ ràng, tổ chức sát hạch tiêu chuẩn bắt buộc và chỉ trao quyền cho nhân sự vượt qua bài kiểm tra năng lực.'*"
            )

        full_response = (
            f"### ⚔️ 1. ĐỐI ĐÁP PHẢN BIỆN TRỰC DIỆN ({lens} LENS)\n\n"
            f"{adversarial_text}\n\n"
            f"### 💡 2. GỢI Ý ĐÒN BẨY HÓA GIẢI & CHIẾN LƯỢC\n\n"
            f"{strategy_text}\n"
        )

        return full_response, citations
