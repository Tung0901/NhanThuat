"""
Multi-Agent Advisory Council Engine for NhanThuat (Milestone Phase 4).
Simulates multi-perspective board deliberation across seven schools of thought.
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import ClassVar

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
    Orchestrates the seven-lens Philosophical Advisory Council.
    """

    COUNCIL_MEMBERS: ClassVar[list[CouncilMember]] = [
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
        CouncilMember(
            agent_id="ICHING",
            title="Đại diện Dịch Học",
            school_of_thought="Biến Dịch & Chuyển Trạng Thái",
            core_focus="Đọc chu kỳ như một giả thuyết định tính, xác định điểm chuyển pha và điều kiện bác bỏ.",
            icon="",
        ),
        CouncilMember(
            agent_id="TIMING",
            title="Đại diện Thời Thế",
            school_of_thought="Nhịp Độ & Cửa Sổ Can Thiệp",
            core_focus="Đánh giá mức độ chín của dữ liệu, khả năng hành động và thời điểm rà soát quyết định.",
            icon="",
        ),
    ]
    EXPECTED_AGENT_IDS: ClassVar[frozenset[str]] = frozenset(
        {"LEGALISM", "TAOISM", "CONFUCIAN", "XUNZI", "SUNZI", "ICHING", "TIMING"}
    )

    def __init__(
        self,
        knowledge_engine: KnowledgeEngine | None = None,
        hybrid_retriever: HybridRetriever | None = None,
    ) -> None:
        self.engine = knowledge_engine or KnowledgeEngine()
        self.retriever = hybrid_retriever or HybridRetriever(units=list(self.engine.units_by_id.values()))
        engine_dir = Path(__file__).resolve().parents[3] / "backend" / "app" / "engine" / "philosophies"
        self.iching_profile = self._load_lens_profile(engine_dir / "iching_engine.json")
        self.timing_profile = self._load_lens_profile(engine_dir / "timing_engine.json")

    @staticmethod
    def _load_lens_profile(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as profile_file:
            return json.load(profile_file)

    def deliberate(self, scenario_text: str, top_k_units: int = 5) -> CouncilDeliberationResult:
        """
        Execute full 3-stage Council Deliberation protocol:
        - Stage 1: 7 complete perspective briefs
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

        # 2. Try to generate dynamically via LLM
        pitches = []
        cross_debates = []
        decision_matrix = None
        
        try:
            from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
            syn = KnowledgeSynthesizer()
            prompt = (
                f"Bạn là Hội đồng 7 Cố Vấn Nhân Thuật (Pháp Gia, Đạo Gia, Nho Gia, Tuân Tử, Tôn Tử, Dịch Học, Thời Thế). "
                f"Hãy phân tích tình huống sau của Chủ tịch/CEO và trả về 100% JSON hợp lệ.\n\n"
                f"TÌNH HUỐNG: {scenario_text}\n\n"
                f"TRI THỨC THAM KHẢO:\n"
            )
            for c in citations:
                prompt += f"- [{c['id']}] {c['title']} ({c['domain']})\n"
                
            prompt += (
                "\nCẤU TRÚC JSON YÊU CẦU (Trả về đúng cấu trúc này, không bọc markdown):\n"
                "{\n"
                "  \"pitches\": [\n"
                "    {\n"
                "      \"agent_id\": \"LEGALISM | TAOISM | CONFUCIAN | XUNZI | SUNZI | ICHING | TIMING\",\n"
                "      \"title\": \"Tên đại diện và triết lý\",\n"
                "      \"situation_read\": \"Đọc tình thế cụ thể, tối thiểu 80 ký tự\",\n"
                "      \"stance\": \"Lập trường có điều kiện, tối thiểu 80 ký tự\",\n"
                "      \"assumptions\": [\"Giả định 1\", \"Giả định 2\"],\n"
                "      \"core_arguments\": [\"Lập luận 1\", \"Lập luận 2\", \"Lập luận 3\", \"Lập luận 4\"],\n"
                "      \"recommended_actions\": [\"Hành động 1\", \"Hành động 2\", \"Hành động 3\"],\n"
                "      \"evidence_needed\": [\"Bằng chứng cần kiểm 1\", \"Bằng chứng cần kiểm 2\"],\n"
                "      \"risk_warning\": \"Cảnh báo rủi ro cụ thể, tối thiểu 60 ký tự\",\n"
                "      \"confidence_note\": \"Mức tin cậy và điều kiện làm thay đổi kết luận, tối thiểu 40 ký tự\"\n"
                "    }\n"
                "  ], (pitches phải có đúng và đủ 7 agent_id, mỗi ID xuất hiện một lần)\n"
                "  \"cross_debates\": [\n"
                "    {\n"
                "      \"challenger_id\": \"ID người phản biện (ví dụ LEGALISM)\",\n"
                "      \"target_id\": \"ID người bị phản biện (ví dụ CONFUCIAN)\",\n"
                "      \"critique\": \"Lời phản biện\",\n"
                "      \"counter_recommendation\": \"Đề xuất hóa giải\"\n"
                "    }\n"
                "  ], (khoảng 2-3 debates)\n"
                "  \"decision_matrix\": {\n"
                "    \"highest_consensus\": \"Điểm đồng thuận cao nhất\",\n"
                "    \"core_conflicts\": [\"Mâu thuẫn 1\", \"Mâu thuẫn 2\"],\n"
                "    \"plan_a_primary\": {\"name\": \"Tên Plan A\", \"summary\": \"Tóm tắt\", \"action_steps\": [\"Bước 1\", \"Bước 2\"]},\n"
                "    \"plan_b_fallback\": {\"name\": \"Tên Plan B\", \"summary\": \"Tóm tắt\", \"action_steps\": [\"Bước 1\", \"Bước 2\"]},\n"
                "    \"plan_c_containment\": {\"name\": \"Tên Plan C\", \"summary\": \"Tóm tắt\", \"action_steps\": [\"Bước 1\", \"Bước 2\"]},\n"
                "    \"critical_caveats\": [\"Lưu ý 1\"],\n"
                "    \"execution_directives\": [\"Chỉ thị 1\"]\n"
                "  }\n"
                "}\n"
                "Dịch Học chỉ được dùng như khung giả thuyết định tính về biến dịch/chuyển trạng thái, không bói quẻ, "
                "không tiên tri và không khẳng định tất định. Thời Thế phải nêu tín hiệu, độ chín dữ liệu, cửa sổ hành động "
                "và điểm rà soát. Mọi lăng kính phải phân biệt dữ kiện, giả định và khuyến nghị."
            )
            
            data = syn.generate_json(prompt)
            
            # Map JSON to python models
            raw_pitches = data.get("pitches", [])
            self._validate_generated_pitches(raw_pitches)
            for p in raw_pitches:
                pitches.append(PerspectivePitch(
                    agent_id=p.get("agent_id", "UNKNOWN"),
                    title=p.get("title", "Unknown"),
                    stance=p.get("stance", ""),
                    core_arguments=p.get("core_arguments", []),
                    situation_read=p.get("situation_read", ""),
                    assumptions=p.get("assumptions", []),
                    recommended_actions=p.get("recommended_actions", []),
                    evidence_needed=p.get("evidence_needed", []),
                    confidence_note=p.get("confidence_note", ""),
                    cited_unit_ids=[c["id"] for c in citations],
                    citations=citations,
                    risk_warning=p.get("risk_warning", ""),
                ))
                
            raw_debates = data.get("cross_debates", [])
            for d in raw_debates:
                cross_debates.append(CrossDebatePoint(
                    challenger_id=d.get("challenger_id", ""),
                    target_id=d.get("target_id", ""),
                    critique=d.get("critique", ""),
                    counter_recommendation=d.get("counter_recommendation", "")
                ))
                
            dm = data.get("decision_matrix", {})
            decision_matrix = DecisionMatrix(
                highest_consensus=dm.get("highest_consensus", ""),
                core_conflicts=dm.get("core_conflicts", []),
                plan_a_primary=dm.get("plan_a_primary", {}),
                plan_b_fallback=dm.get("plan_b_fallback", {}),
                plan_c_containment=dm.get("plan_c_containment", {}),
                critical_caveats=dm.get("critical_caveats", []),
                execution_directives=dm.get("execution_directives", [])
            )
        except Exception as e:  # noqa: BLE001 - LLM output parsing must fall back to deterministic
            print(f"[CouncilEngine] Failed to generate dynamically: {e}")
            # Fallback to deterministic mock
            pitches = self._generate_pitches(scenario_text, citations)
            cross_debates = self._generate_cross_debates(scenario_text, pitches)
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

    @classmethod
    def _validate_generated_pitches(cls, pitches: list[dict]) -> None:
        """Reject shallow or partial LLM output before it reaches the UI."""
        if len(pitches) != len(cls.EXPECTED_AGENT_IDS):
            raise ValueError("Council output must contain exactly seven pitches")
        if {str(p.get("agent_id", "")) for p in pitches} != cls.EXPECTED_AGENT_IDS:
            raise ValueError("Council output is missing one or more required lenses")

        requirements = (
            ("situation_read", 80),
            ("stance", 80),
            ("risk_warning", 60),
            ("confidence_note", 40),
        )
        list_requirements = (
            ("assumptions", 2),
            ("core_arguments", 4),
            ("recommended_actions", 3),
            ("evidence_needed", 2),
        )
        for pitch in pitches:
            for field_name, minimum in requirements:
                if len(str(pitch.get(field_name, "")).strip()) < minimum:
                    raise ValueError(f"Incomplete {field_name} for {pitch.get('agent_id')}")
            for field_name, minimum in list_requirements:
                value = pitch.get(field_name, [])
                if (
                    not isinstance(value, list)
                    or len(value) < minimum
                    or any(len(str(item).strip()) < 20 for item in value)
                ):
                    raise ValueError(f"Incomplete {field_name} for {pitch.get('agent_id')}")

    def _generate_pitches(self, scenario: str, citations: list[dict[str, str]]) -> list[PerspectivePitch]:
        """Generate seven complete, deterministic philosophical briefs."""
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

        shared_assumptions = [
            "Tình huống đầu vào phản ánh vấn đề thực tế nhưng chưa thay thế hồ sơ, hợp đồng và lời khai đã được đối soát.",
            "Người ra quyết định có thẩm quyền triển khai một bước thử có giới hạn và dừng lại khi xuất hiện bằng chứng trái chiều.",
        ]
        shared_evidence = [
            "Hồ sơ sự kiện có mốc thời gian, người chịu trách nhiệm và bằng chứng gốc được đối chiếu độc lập.",
            "Dữ liệu về chi phí, năng lực thay thế, tác động con người và ràng buộc pháp lý của từng phương án.",
        ]
        action_sets = {
            "LEGALISM": [
                "Lập biên bản sự kiện và đối chiếu nghĩa vụ bằng văn bản trước khi áp dụng chế tài.",
                "Ấn định mốc khắc phục, chủ thể chịu trách nhiệm và hệ quả nếu không hoàn thành.",
                "Cho pháp chế hoặc kiểm soát nội bộ rà soát tính tương xứng của biện pháp.",
            ],
            "TAOISM": [
                "Tạm giảm xung lực đối đầu để thu thêm dữ kiện và quan sát phản ứng thực tế.",
                "Mở một lối điều chỉnh ít tổn thất để các bên có thể sửa sai mà không mất thể diện.",
                "Đặt giới hạn đỏ và thời điểm kết thúc giai đoạn mềm dẻo để tránh trì hoãn vô hạn.",
            ],
            "CONFUCIAN": [
                "Tổ chức đối thoại trực tiếp, tách lợi ích chính đáng khỏi hành vi vi phạm cần sửa.",
                "Công bố chuẩn mực áp dụng đồng đều và trách nhiệm nêu gương của người lãnh đạo.",
                "Ghi nhận cam kết phục hồi niềm tin bằng hành vi và mốc kiểm chứng cụ thể.",
            ],
            "XUNZI": [
                "Xác lập lại vai trò, quyền hạn, tiêu chuẩn đầu ra và quy trình bàn giao.",
                "Thử nghiệm quy trình sửa đổi trên phạm vi nhỏ trước khi nhân rộng toàn hệ thống.",
                "Đánh giá lại bằng chỉ số hành vi và kết quả thay vì chỉ dựa vào lời hứa.",
            ],
            "SUNZI": [
                "Lập bản đồ mục tiêu, nguồn lực, giới hạn chịu đựng và lợi ích của từng bên.",
                "Chuẩn bị phương án thay thế có thể thực thi trước khi phát tín hiệu cứng rắn.",
                "Chọn điểm can thiệp tạo lợi thế nhưng vẫn giữ đường lui và khả năng đảo ngược.",
            ],
        }
        for pitch in pitches:
            pitch.situation_read = (
                f"Với tình huống '{scenario}', lăng kính {pitch.title} nhìn thấy một khoảng cách giữa hiện trạng, "
                "chuẩn mực cần đạt và năng lực thực thi. Kết luận chỉ nên hình thành sau khi đối chiếu dữ kiện, "
                "động cơ các bên và mức độ đảo ngược của quyết định."
            )
            pitch.assumptions = list(shared_assumptions)
            pitch.core_arguments.append(
                "Khuyến nghị phải được triển khai theo bước có mốc kiểm chứng, vì phản ứng thực tế có thể làm thay đổi chẩn đoán ban đầu."
            )
            pitch.recommended_actions = action_sets[pitch.agent_id]
            pitch.evidence_needed = list(shared_evidence)
            pitch.confidence_note = (
                "Độ tin cậy trung bình; sẽ tăng khi hồ sơ sự kiện và năng lực phương án thay thế được xác minh, "
                "và phải giảm nếu xuất hiện dữ kiện mâu thuẫn."
            )
            if len(pitch.stance) < 80:
                pitch.stance += " Lập trường này chỉ có hiệu lực khi dữ kiện nền và thẩm quyền thực thi đã được xác minh."
            if len(pitch.risk_warning) < 60:
                pitch.risk_warning += " Cần đặt mốc dừng và cơ chế rà soát độc lập trước khi mở rộng biện pháp."

        pitches.extend([
            self._build_iching_pitch(scenario, citations),
            self._build_timing_pitch(scenario, citations),
        ])
        return pitches

    def _build_iching_pitch(
        self, scenario: str, citations: list[dict[str, str]]
    ) -> PerspectivePitch:
        text = scenario.casefold()
        states = self.iching_profile["six_dragon_states"]
        if any(token in text for token in ("khởi đầu", "mới", "chưa vững")):
            state = states["hao_1_tiem_long"]
        elif any(token in text for token in ("đỉnh", "độc đoán", "quá cao", "cực thịnh")):
            state = states["hao_6_khang_long"]
        elif any(token in text for token in ("ngã rẽ", "chuyển", "khủng hoảng", "bế tắc", "thay đổi")):
            state = states["hao_4_uyen_duoc"]
        else:
            state = states["hao_3_can_can"]
        source = self.iching_profile["metadata"]["source_document"]
        return PerspectivePitch(
            agent_id="ICHING",
            title=f"Dịch Học: {state['name']}",
            situation_read=(
                f"Tình huống '{scenario}' được đọc như một giả thuyết chuyển trạng thái gần với {state['name']}. "
                f"{state['meaning']} Đây là phép đối chiếu định tính để tìm điểm chuyển pha, không phải quẻ bói hay dự báo tất định."
            ),
            stance=(
                "Không chốt quyết định chỉ từ hình ảnh Dịch học. Hãy dùng mô hình chuyển trạng thái để xác định điều kiện "
                "giữ nguyên, thử nghiệm hoặc đổi hướng, rồi kiểm chứng từng điều kiện bằng dữ liệu thực tế."
            ),
            assumptions=[
                "Các dấu hiệu trong mô tả phản ánh một chuyển pha có thật chứ không chỉ là dao động ngắn hạn.",
                "Tổ chức còn đủ dư địa để thực hiện thử nghiệm nhỏ và đảo ngược trước khi cam kết toàn bộ nguồn lực.",
            ],
            core_arguments=[
                f"Trạng thái tham chiếu là {state['name']}, được chọn từ tín hiệu ngôn ngữ của tình huống chứ không qua nghi thức bói toán.",
                f"Chỉ dẫn định tính của trạng thái: {state['action_directive']}",
                "Quy luật vật cực tất phản nhắc người ra quyết định kiểm tra dấu hiệu đảo chiều khi áp lực hoặc tăng trưởng đã tiến gần cực điểm.",
                "Nguyên tắc cương nhu tương tế yêu cầu đồng thời giữ ranh giới rõ và tạo không gian điều chỉnh có kiểm soát.",
            ],
            recommended_actions=[
                "Ghi rõ trạng thái hiện tại, trạng thái mong muốn và ba tín hiệu chứng minh quá trình chuyển pha đã bắt đầu.",
                "Thực hiện một thử nghiệm quy mô nhỏ, có thời hạn và tiêu chí dừng trước khi mở rộng quyết định.",
                "Đặt lịch rà soát để bác bỏ hoặc cập nhật giả thuyết khi tín hiệu thực tế không phù hợp.",
            ],
            evidence_needed=[
                "Chuỗi sự kiện theo thời gian cho thấy xu hướng bền vững thay vì một biến động đơn lẻ.",
                "Chỉ số định lượng hoặc hành vi có thể xác nhận trạng thái cũ đang suy yếu và trạng thái mới đang hình thành.",
            ],
            confidence_note=(
                "Độ tin cậy thận trọng vì đây là khung diễn giải định tính. Kết luận phải hạ mức tin cậy hoặc bị bác bỏ "
                "nếu dữ liệu chuỗi thời gian không cho thấy chuyển pha."
            ),
            cited_unit_ids=[c["id"] for c in citations],
            citations=citations + [{"id": "LENS-ICHING", "title": source, "domain": "qualitative_framework"}],
            risk_warning=(
                "Rủi ro lớn nhất là gán biểu tượng cho dữ kiện rồi xem nó như tiên tri. Không dùng lăng kính này thay thế pháp lý, "
                "tài chính, điều tra thực địa hoặc trách nhiệm của người ra quyết định."
            ),
        )

    def _build_timing_pitch(
        self, scenario: str, citations: list[dict[str, str]]
    ) -> PerspectivePitch:
        text = scenario.casefold()
        phases = self.timing_profile["three_temporal_phases"]
        if any(token in text for token in ("chưa rõ", "thiếu dữ liệu", "mới", "kích động")):
            phase = phases["phase_1_so_thoi"]
        elif any(token in text for token in ("quá muộn", "cắt lỗ", "suy thoái", "không còn khả thi")):
            phase = phases["phase_3_mat_thoi"]
        else:
            phase = phases["phase_2_duong_thoi"]
        source = self.timing_profile["metadata"]["source_document"]
        return PerspectivePitch(
            agent_id="TIMING",
            title=f"Thời Thế: {phase['phase_name']}",
            situation_read=(
                f"Từ tình huống '{scenario}', lăng kính Thời Thế tạm xếp quyết định vào {phase['phase_name']}. "
                f"Tín hiệu tham chiếu: {phase['indicators']} Phân loại này là giả thuyết vận hành và phải được rà lại khi dữ liệu đổi."
            ),
            stance=(
                "Không hỏi đơn giản nên làm hay không, mà xác định việc nào cần làm ngay, việc nào chờ thêm bằng chứng và "
                "mốc nào khiến cửa sổ hành động đóng lại. Nhịp độ phải đi cùng khả năng thực thi."
            ),
            assumptions=[
                "Các mốc thời gian và tín hiệu về mức độ sẵn sàng trong đầu vào tương đối chính xác.",
                "Tổ chức có người chịu trách nhiệm theo dõi cửa sổ hành động và quyền điều chỉnh khi điều kiện thay đổi.",
            ],
            core_arguments=[
                f"Pha tham chiếu hiện tại là {phase['phase_name']}; đây là phân loại theo độ chín dữ liệu và năng lực hành động.",
                f"Giao thức đề xuất của pha: {phase['tactical_protocol']}",
                "Một quyết định đúng về nội dung vẫn có thể thất bại nếu đưa ra khi liên minh nội bộ, bằng chứng hoặc phương án thay thế chưa sẵn sàng.",
                "Cửa sổ hành động phải có tín hiệu mở, thời hạn đóng và điểm rà soát, thay vì dựa vào cảm giác cấp bách của cá nhân.",
            ],
            recommended_actions=[
                "Lập bảng tín hiệu xanh, vàng, đỏ cho dữ liệu, đồng thuận nội bộ và năng lực phương án thay thế.",
                "Chỉ định thời hạn cửa sổ hành động cùng người có quyền kích hoạt, hoãn hoặc hủy quyết định.",
                "Rà soát lại sau mỗi mốc quan trọng và chuyển pha nếu bằng chứng nền không còn đúng.",
            ],
            evidence_needed=[
                "Mức độ hoàn chỉnh của bằng chứng, sự thống nhất của nhóm thực thi và năng lực phương án dự phòng.",
                "Chi phí của việc hành động ngay so với trì hoãn, bao gồm rủi ro mất cơ hội và chi phí khó đảo ngược.",
            ],
            confidence_note=(
                "Độ tin cậy trung bình và phụ thuộc mạnh vào độ mới của dữ liệu. Mọi thay đổi về bằng chứng, nguồn lực hoặc "
                "hạn chót đều có thể làm thay đổi phân loại pha."
            ),
            cited_unit_ids=[c["id"] for c in citations],
            citations=citations + [{"id": "LENS-TIMING", "title": source, "domain": "qualitative_framework"}],
            risk_warning=(
                "Rủi ro là hợp thức hóa trì hoãn bằng chữ 'chưa đúng thời' hoặc hành động vội bằng chữ 'thời cơ'. "
                "Mọi nhận định thời điểm phải gắn với tín hiệu quan sát được và người chịu trách nhiệm."
            ),
        )

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
            CrossDebatePoint(
                challenger_id="ICHING",
                target_id="LEGALISM",
                critique="Pháp Gia có thể khóa tổ chức vào trạng thái cũ nếu áp dụng chế tài trước khi kiểm tra liệu tình huống đã bước sang một pha mới hay chưa.",
                counter_recommendation="Đặt một thử nghiệm chuyển trạng thái có tiêu chí bác bỏ, sau đó mới quyết định giữ, tăng hoặc rút biện pháp chế tài.",
            ),
            CrossDebatePoint(
                challenger_id="TIMING",
                target_id="SUNZI",
                critique="Có phương án thay thế chưa đủ để hành động; nếu dữ liệu, liên minh nội bộ và năng lực triển khai chưa chín thì đòn bẩy có thể phản tác dụng.",
                counter_recommendation="Định nghĩa tín hiệu mở cửa sổ hành động, hạn chót và điểm rà soát trước khi phát tín hiệu chiến lược ra bên ngoài.",
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
                "Hội đồng Cố vấn thống nhất rằng quyết định phải dựa trên dữ kiện đã đối soát, có ranh giới bằng văn bản, "
                "phương án thay thế khả thi và mốc rà soát. Dịch Học và Thời Thế bổ sung việc kiểm tra chuyển pha cùng độ chín "
                "của cửa sổ hành động; hai lăng kính này không thay thế bằng chứng thực địa."
            ),
            core_conflicts=[
                "Cân đối giữa tốc độ xử lý dứt điểm (Pháp Gia) và việc duy trì quan hệ đối tác dài hạn (Nho Gia / Đạo Gia).",
                "Mức độ công khai chế tài phạt: Áp dụng ngay lập tức hay gia hạn có điều kiện 24h."
            ],
            plan_a_primary={
                "name": "Phương án A (Hành động có điều kiện)",
                "summary": "Xác minh sự kiện, chốt ranh giới và triển khai bước can thiệp có thể kiểm chứng trong cửa sổ hành động đã định.",
                "action_steps": [
                    "1. Lập hồ sơ hiện trạng, giả định nền và bằng chứng còn thiếu.",
                    "2. Xác định biện pháp tương xứng, người chịu trách nhiệm và thời hạn khắc phục.",
                    "3. Chạy bước thử có giới hạn rồi đánh giá lại tại mốc đã công bố."
                ]
            },
            plan_b_fallback={
                "name": "Phương án B (Điều chỉnh và học nhanh)",
                "summary": "Khi dữ liệu chưa đủ chín, thu hẹp phạm vi, bổ sung bằng chứng và duy trì khả năng đảo ngược quyết định.",
                "action_steps": [
                    "1. Tách phần chắc chắn khỏi phần còn tranh cãi và xử lý riêng từng nhóm.",
                    "2. Bổ sung dữ liệu tại nguồn và kiểm tra năng lực thực thi của các bên.",
                    "3. Cập nhật quyết định khi tín hiệu chuyển pha hoặc độ chín thay đổi."
                ]
            },
            plan_c_containment={
                "name": "Phương án C (Khoanh vùng tổn thất)",
                "summary": "Nếu giả định nền bị bác bỏ hoặc rủi ro vượt ngưỡng, dừng mở rộng và chuyển sang bảo toàn nguồn lực.",
                "action_steps": [
                    "1. Kích hoạt tiêu chí dừng và ghi nhận nguyên nhân bằng văn bản.",
                    "2. Cô lập phần tổn thất, bảo toàn dữ liệu, dòng tiền và hoạt động thiết yếu.",
                    "3. Chuyển sang phương án thay thế đã được thẩm định và thông báo mốc đánh giá mới."
                ]
            },
            critical_caveats=[
                "Không phát tín hiệu cứng rắn nếu phương án thay thế chưa được kiểm chứng về pháp lý, nguồn lực và thời gian.",
                "Dịch Học là khung giả thuyết định tính; không dùng biểu tượng hoặc 64 quẻ để tiên tri hay thay thế dữ kiện.",
                "Mọi trao đổi quyết định phải được xác nhận bằng văn bản và gắn với người có thẩm quyền."
            ],
            execution_directives=[
                "Chỉ thị 1: Chỉ định chủ hồ sơ và hoàn tất bảng dữ kiện, giả định, bằng chứng thiếu.",
                "Chỉ thị 2: Xác định cửa sổ hành động, tiêu chí dừng và lịch rà soát trước khi triển khai.",
                "Chỉ thị 3: Báo cáo lại kết quả bước thử, dữ kiện phản chứng và đề xuất cập nhật quyết định."
            ]
        )
