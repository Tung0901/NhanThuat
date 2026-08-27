"""
Multi-Agent Advisory Council Engine for NhanThuat (Milestone Phase 4).
Simulates multi-perspective board deliberation across 5 classical schools of thought:
Legalism, Taoism, Confucianism, Xunzi Realism, and Sunzi Strategy.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

from nhan_thuat.council.models import (
    CouncilDeliberationResult,
    CouncilMember,
    CrossDebatePoint,
    DecisionMatrix,
    PerspectivePitch,
)
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.rag.hybrid_retriever import HybridRetriever


class CouncilEngine:
    """
    Orchestrates the 5-Agent Philosophical Advisory Council for high-stakes executive decisions.
    """

    COUNCIL_MEMBERS = [
        CouncilMember(
            agent_id="LEGALISM",
            title="Đại diện Pháp Gia (Hàn Phi Tử)",
            school_of_thought="Pháp Trị Thực Chứng",
            core_focus="Thiết chế quy chuẩn, thưởng phạt minh bạch, kiểm soát tuân thủ và chế tài hợp đồng.",
            icon="⚖️",
        ),
        CouncilMember(
            agent_id="TAOISM",
            title="Đại diện Đạo Gia (Lão Trang)",
            school_of_thought="Đạo Pháp Tự Nhiên",
            core_focus="Bảo toàn nguyên khí, tránh đối đầu trực diện, dĩ nhu khắc cương, ứng biến linh hoạt.",
            icon="☯️",
        ),
        CouncilMember(
            agent_id="CONFUCIAN",
            title="Đại diện Nho Gia (Khổng Tử)",
            school_of_thought="Đức Trị & Nhân Nghĩa",
            core_focus="Giữ chữ Tín, phát triển văn hóa đội ngũ, lãnh đạo nêu gương, dung hòa quan hệ lâu dài.",
            icon="📜",
        ),
        CouncilMember(
            agent_id="XUNZI",
            title="Đại diện Tuân Tử (Lễ Trị Thực Nghiệp)",
            school_of_thought="Lễ Định Phần & Khuyên Học",
            core_focus="Quy chuẩn hóa vai trò, sát hạch tiêu chuẩn, rèn nắn thói quen, kiềm chế tính tư lợi.",
            icon="🏛️",
        ),
        CouncilMember(
            agent_id="SUNZI",
            title="Đại diện Tôn Tử (Binh Pháp)",
            school_of_thought="Chiến Lược Mưu Lược",
            core_focus="Tạo thế và thời, tối ưu nguồn lực, đòn bẩy bất đối xứng, biết người biết ta.",
            icon="⚔️",
        ),
    ]

    def __init__(
        self,
        knowledge_engine: KnowledgeEngine | None = None,
        hybrid_retriever: HybridRetriever | None = None,
    ) -> None:
        self.engine = knowledge_engine or KnowledgeEngine()
        self.retriever = hybrid_retriever or HybridRetriever(units=list(self.engine.units_by_id.values()))

    def deliberate(self, scenario_text: str, top_k_units: int = 5) -> CouncilDeliberationResult:
        """
        Execute full 3-stage Council Deliberation protocol:
        - Stage 1: 5 Agent Perspective Pitches
        - Stage 2: Cross-School Adversarial Examination
        - Stage 3: Council Synthesis & Decision Matrix
        """
        t_start = time.perf_counter()
        session_id = f"COUNCIL-SESS-{uuid.uuid4().hex[:8].upper()}"

        # 1. Retrieve relevant knowledge units via Hybrid RAG
        rag_res = self.retriever.retrieve(query=scenario_text, top_k=top_k_units, expand_relations=True)
        primary_units = rag_res.primary_units

        # Extract unit citations
        citations = []
        for u in primary_units:
            uid = getattr(u, "id", getattr(u, "unit_id", ""))
            raw = u.raw if hasattr(u, "raw") and u.raw else getattr(u, "raw_data", {})
            title = str(getattr(u, "title", raw.get("title", uid)))
            domain = str(getattr(u, "primary_domain", getattr(u, "domain", raw.get("primary_domain", ""))))
            citations.append({"id": uid, "title": title, "domain": domain})

        # 2. Stage 1: Generate 5 Agent Perspective Pitches
        pitches = self._generate_pitches(scenario_text, citations)

        # 3. Stage 2: Cross-School Debates
        cross_debates = self._generate_cross_debates(scenario_text, pitches)

        # 4. Stage 3: Synthesize Decision Matrix
        decision_matrix = self._synthesize_decision_matrix(scenario_text, pitches, cross_debates, citations)

        total_latency = (time.perf_counter() - t_start) * 1000

        return CouncilDeliberationResult(
            session_id=session_id,
            scenario_text=scenario_text,
            pitches=pitches,
            cross_debates=cross_debates,
            decision_matrix=decision_matrix,
            total_latency_ms=total_latency,
        )

    def _generate_pitches(self, scenario: str, citations: list[dict[str, str]]) -> list[PerspectivePitch]:
        """Generate Stage 1 pitches from 5 distinct philosophical viewpoints."""
        c0 = citations[0]["id"] if citations else "NT-LAW-0001"
        c1 = citations[1]["id"] if len(citations) > 1 else "NT-PRINCIPLE-0061"
        c2 = citations[2]["id"] if len(citations) > 2 else "NT-LAW-0054"

        pitches = [
            PerspectivePitch(
                agent_id="LEGALISM",
                title="Pháp Gia: Siết Chặt Kỷ Luật & Thực Thi Chế Tài",
                stance="Tuyệt đối không nhượng bộ bằng cảm tính. Khởi động biên bản và áp dụng chế tài theo hợp đồng.",
                core_arguments=[
                    "Mọi thỏa hiệp không bằng văn bản đều tạo tiền lệ xấu khiến đối tác hoặc nhân sự tiếp tục vi phạm.",
                    "Kích hoạt cơ chế Nhị Bỉnh (Thưởng rõ ràng - Phạt nghiêm minh) để kiểm soát tổn thất vận hành.",
                    f"Căn cứ đơn vị tri thức: {c0} - Động lực & Chế tài chi phối hành vi."
                ],
                cited_unit_ids=[c0],
                citations=citations[:1],
                risk_warning="Cảnh báo: Nếu quá cứng nhắc mà thiếu phương án B, có thể đẩy đối tác vào bước đường cùng dẫn đến đứt gãy hoàn toàn.",
            ),
            PerspectivePitch(
                agent_id="TAOISM",
                title="Đạo Gia: Dĩ Nhu Khắc Cương & Bảo Toàn Nguyên Khí",
                stance="Tránh đối đầu trực diện làm tiêu hao năng lượng. Tìm kiếm điểm cân bằng động và để đối phương tự lộ sơ hở.",
                core_arguments=[
                    "Khi cơn bão đang mạnh, cây cứng dễ gãy hơn cành mềm uốn lượn.",
                    "Chủ động hoãn xung lực đối đầu 24h để quan sát phản ứng thực tế của hiện trường.",
                    f"Căn cứ đơn vị tri thức: {c1} - Thích ứng động và nguyên lý bảo tồn sinh lực."
                ],
                cited_unit_ids=[c1],
                citations=citations[1:2] if len(citations) > 1 else citations[:1],
                risk_warning="Cảnh báo: Nhẫn nhịn kéo dài mà không có giới hạn đỏ sẽ bị hiểu nhầm là sự bất lực và nhu nhược.",
            ),
            PerspectivePitch(
                agent_id="CONFUCIAN",
                title="Nho Gia: Giữ Chữ Tín & Xây Dựng Văn Hóa Bền Vững",
                stance="Xem xét yếu tố con người, bảo toàn uy tín doanh nghiệp và mở kênh đối thoại thiện chí.",
                core_arguments=[
                    "Thương hiệu và niềm tin dài hạn quý hơn các khoản phạt tài chính ngắn hạn.",
                    "Lãnh đạo cần trực tiếp lắng nghe để thấu suốt căn nguyên khó khăn của các bên.",
                    f"Căn cứ tri thức: {c0} - Uy tín và tính bền vững của liên minh."
                ],
                cited_unit_ids=[c0],
                citations=citations[:1],
                risk_warning="Cảnh báo: Cả nể quá mức sẽ biến tổ chức thành nạn nhân bị lợi dụng lòng tốt.",
            ),
            PerspectivePitch(
                agent_id="XUNZI",
                title="Tuân Tử: Tái Định Chuẩn & Lễ Định Phần",
                stance="Phân định rõ ràng trách nhiệm của từng vị trí; dùng tiêu chuẩn và sát hạch thực tế để giải quyết.",
                core_arguments=[
                    "Bản tính con người hướng về tư lợi; chỉ có quy chuẩn và định mức rõ ràng mới ngăn chặn xung đột.",
                    "Chuẩn hóa quy trình bàn giao và nghiệm thu theo biểu mẫu kiểm toán bắt buộc.",
                    f"Căn cứ tri thức: {c1} - Tái cấu trúc cơ chế khoán và vai trò trước khi yêu cầu thay đổi thái độ."
                ],
                cited_unit_ids=[c1],
                citations=citations[1:2] if len(citations) > 1 else citations[:1],
                risk_warning="Cảnh báo: Tiêu chuẩn quá rườm rà sẽ gây nghẽn cổ chai tiến độ nếu bộ máy chưa sẵn sàng.",
            ),
            PerspectivePitch(
                agent_id="SUNZI",
                title="Tôn Tử: Lập Thế Bất Bại & Đòn Bẩy Bất Đối Xứng",
                stance="Không đánh trận không chắc thắng. Chuẩn bị xong Plan B hoàn hảo trước khi đưa ra tối hậu thư.",
                core_arguments=[
                    "Biết người biết ta: Đánh giá chính xác thế kẹt và giới hạn chịu đựng của đối phương.",
                    "Dùng yếu tố thời gian và sự sẵn sàng của nhà cung cấp thay thế làm đòn bẩy buộc đối phương hợp tác.",
                    f"Căn cứ tri thức: {c2} - Lập thế bất đối xứng và định khung giá trị."
                ],
                cited_unit_ids=[c2],
                citations=citations[2:3] if len(citations) > 2 else citations[:1],
                risk_warning="Cảnh báo: Nếu đối phương phát hiện Plan B của ta là đòn gió, ta sẽ mất hoàn toàn ưu thế thương thảo.",
            ),
        ]
        return pitches

    def _generate_cross_debates(self, scenario: str, pitches: list[PerspectivePitch]) -> list[CrossDebatePoint]:
        """Generate Stage 2 adversarial cross-examinations between schools."""
        return [
            CrossDebatePoint(
                challenger_id="LEGALISM",
                target_id="CONFUCIAN",
                critique="Nho Gia quá ngây thơ khi dựa vào lời hứa đạo đức giữa thương trường khốc liệt. Không có chế tài phạt thì chữ 'Tín' chỉ là khẩu hiệu rỗng.",
                counter_recommendation="Bắt buộc quy chuẩn mọi cam kết thành phụ lục hợp đồng có giá trị bồi thường tài chính.",
            ),
            CrossDebatePoint(
                challenger_id="TAOISM",
                target_id="LEGALISM",
                critique="Pháp Gia quá cứng nhắc, chỉ chăm chăm dùng luật phạt sẽ làm đứt gãy mối quan hệ cung ứng và đẩy nhà thầu vào thế bất cần.",
                counter_recommendation="Tạo một bước đệm thương lượng 12h để đối phương có lối thoát danh dự mà vẫn hoàn thành nhiệm vụ.",
            ),
            CrossDebatePoint(
                challenger_id="SUNZI",
                target_id="XUNZI",
                critique="Tuân Tử tập trung quá nhiều vào tiêu chuẩn nội bộ tĩnh mà quên mất yếu tố thời cơ và đòn bẩy cạnh tranh trên thị trường.",
                counter_recommendation="Song song với việc siết tiêu chuẩn, phải kích hoạt đàm phán với đơn vị dự phòng bên ngoài để tạo áp lực thế trận.",
            ),
        ]

    def _synthesize_decision_matrix(
        self,
        scenario: str,
        pitches: list[PerspectivePitch],
        debates: list[CrossDebatePoint],
        citations: list[dict[str, str]],
    ) -> DecisionMatrix:
        """Stage 3: Produce executive Decision Matrix with Plans A/B/C."""
        return DecisionMatrix(
            highest_consensus=(
                "Hội đồng Cố vấn thống nhất 100%: Ban Lãnh đạo không được nhượng bộ miệng vô căn cứ. "
                "Cần kết hợp lập trường Pháp Gia (Ràng buộc chế tài bằng văn bản) với Binh Pháp Tôn Tử (Kích hoạt sẵn Plan B) "
                "để nắm quyền chủ động tuyệt đối."
            ),
            core_conflicts=[
                "Cân đối giữa tốc độ xử lý dứt điểm (Pháp Gia) và việc duy trì quan hệ đối tác dài hạn (Nho Gia / Đạo Gia).",
                "Mức độ công khai chế tài phạt: Áp dụng ngay lập tức hay gia hạn có điều kiện 24h."
            ],
            plan_a_primary={
                "name": "Phương án A (Chủ đạo - Kết hợp Pháp Gia & Tôn Tử)",
                "summary": "Gửi công văn ấn định thời hạn tối hậu 24h kèm chế tài cụ thể, đồng thời khởi động đàm phán với đối tác dự phòng.",
                "action_steps": [
                    "1. Lập biên bản hiện trạng và đối chiếu điều khoản vi phạm trong hợp đồng.",
                    "2. Gửi thông báo tối hậu thư hạn định khắc phục trước 12h00 trưa mai.",
                    "3. Đặt cọc giữ chỗ với đơn vị cung ứng dự phòng Plan B để sẵn sàng thay thế nếu đối tác không giao bù."
                ]
            },
            plan_b_fallback={
                "name": "Phương án B (Linh hoạt - Kết hợp Đạo Gia & Tuân Tử)",
                "summary": "Nếu đối tác gặp sự cố khách quan bất khả kháng, tái cấu trúc biểu đồ tiến độ và chia nhỏ khối lượng giao hàng.",
                "action_steps": [
                    "1. Chia khối lượng giao hàng thành 3 đợt nhỏ trong 48h để giảm áp lực dòng tiền cho đối tác.",
                    "2. Tăng cường nhân sự giám sát chất lượng tại nguồn cung ứng của đối tác.",
                    "3. Giữ lại 15% giá trị thanh toán đợt cuối đến khi hoàn tất kiểm toán hiện trường."
                ]
            },
            plan_c_containment={
                "name": "Phương án C (Khoanh vùng rủi ro - Pháp Trị Triệt Để)",
                "summary": "Đình chỉ hợp đồng nếu đối tác tiếp tục kéo dài vi phạm, khởi kiện thu hồi thiệt hại và bàn giao toàn bộ cho Plan B.",
                "action_steps": [
                    "1. Niêm phong hiện trường và khóa tài khoản thanh toán.",
                    "2. Chuyển hồ sơ cho bộ phận Pháp chế thực thi bồi thường thiệt hại 100%.",
                    "3. Bàn giao mặt bằng cho nhà thầu mới thi công bù tiến độ."
                ]
            },
            critical_caveats=[
                "Tuyệt đối không đưa ra lời đe dọa nếu doanh nghiệp chưa thực sự ký hợp đồng nguyên tắc với đơn vị Plan B.",
                "Mọi trao đổi qua điện thoại hoặc tin nhắn phải được xác nhận lại bằng Email / Văn bản có chữ ký đại diện thẩm quyền."
            ],
            execution_directives=[
                "Chỉ thị 1: Giám đốc Điều hành chỉ đạo ban hành Biên bản Vi phạm trước 17h00 hôm nay.",
                "Chỉ thị 2: Phòng Mua hàng/Cung ứng hoàn tất đánh giá năng lực của đơn vị dự phòng trong vòng 6 giờ.",
                "Chỉ thị 3: Kế toán trưởng tạm giữ đợt thanh toán tiếp theo đến khi có ý kiến của Ban Giám đốc."
            ]
        )
