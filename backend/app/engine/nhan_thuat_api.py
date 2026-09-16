"""
NhanThuat Knowledge Engine & BusinessOS Cognitive API Handler.
Provides detailed actionable execution scripts, step-by-step dialogues, draft communications, financial & operational directives, and custom RAG docs matching.
"""

import json
import uuid
from pathlib import Path
from typing import Any

from backend.app.engine.runtime import BusinessOSRuntimeOrchestrator
from nhan_thuat.knowledge_engine import IndexedUnit, KnowledgeEngine

_orchestrator: BusinessOSRuntimeOrchestrator = None
_dialogue_few_shots: dict[str, Any] = None


def get_orchestrator() -> BusinessOSRuntimeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BusinessOSRuntimeOrchestrator()
    return _orchestrator


def get_dialogue_few_shots() -> dict[str, Any]:
    global _dialogue_few_shots
    if _dialogue_few_shots is None:
        template_file = Path(__file__).resolve().parent.parent.parent / "docs" / "templates" / "dialogue_few_shots.json"
        if template_file.exists():
            try:
                _dialogue_few_shots = json.loads(template_file.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 - fall back to empty few-shot examples
                _dialogue_few_shots = {}
        else:
            _dialogue_few_shots = {}
    return _dialogue_few_shots


_hybrid_retriever = None


def get_hybrid_retriever(engine: KnowledgeEngine) -> Any:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        from nhan_thuat.rag.hybrid_retriever import HybridRetriever
        units_list = list(engine.units_by_id.values())
        _hybrid_retriever = HybridRetriever(units=units_list)
    return _hybrid_retriever


def find_relevant_units(scenario_text: str, engine: KnowledgeEngine, top_k: int = 3) -> list[IndexedUnit]:
    retriever = get_hybrid_retriever(engine)
    res = retriever.retrieve(scenario_text, top_k=top_k, expand_relations=True)
    if res.primary_units:
        return res.primary_units[:top_k]
    return list(engine.units_by_id.values())[:top_k]


def check_context_ambiguity(scenario_text: str) -> tuple[bool, str]:
    text_lower = scenario_text.lower().strip()
    words = text_lower.split()

    location_keywords = ["nhà bè", "công trình", "dự án", "hiện trường", "công trường", "chi nhánh", "phòng ban"]
    action_conflict_keywords = [
        "báo cáo láo", "dối trá", "vi phạm", "đình công", "chậm", "chê", "đắt",
        "từ chối", "tranh chấp", "xung đột", "đòi", "thanh tra", "hỏng", "nghỉ việc", "bất đồng",
        "vật tư", "nhà cung cấp", "hợp đồng", "tiến độ", "nợ", "thanh toán"
    ]

    has_location = any(loc in text_lower for loc in location_keywords)
    has_conflict = any(conf in text_lower for conf in action_conflict_keywords)

    if (has_location and not has_conflict) or len(words) <= 4:
        warning = (
            f"⚠️ CẢNH BẢO THIẾU BỐI CẢNH (AMBIGUOUS CONTEXT WARNING):\n"
            f"   ► Hệ thống nhận diện đây là thông tin địa lý / dự án đơn thuần: '{scenario_text}'.\n"
            f"   ► Lời khuyên cho Chủ tịch: Vui lòng bổ sung sự cố hoặc mâu thuẫn vận hành cụ thể tại bối cảnh này\n"
            f"     (Ví dụ: 'Công trình ở Nhà Bè bị chậm tiến độ do nhà cung cấp giao vật tư trễ'\n"
            f"      hoặc 'Công trình ở Nhà Bè xảy ra xung đột tổ đội đòi tăng lương đột xuất')\n"
            f"     để hệ thống xuất kịch bản chính xác 100%."
        )
        return True, warning

    return False, ""


def generate_actionable_script_details(primary: str, scenario_text: str, matched_units: list = None) -> dict[str, Any]:
    """Generates Senior Executive Co-Pilot Strategic Analysis, 3-step verbatim dialogue, draft communications, and financial/operational directives."""
    # 1. Try to generate dynamically via LLM
    try:
        from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
        syn = KnowledgeSynthesizer()
        prompt = (
            f"Bạn là Cố vấn Chiến lược cấp cao chuyên về QUẢN TRỊ CON NGƯỜI và THUẬT NHÂN TÂM. Hãy lập Kịch bản Hành động (Actionable Script) cho tình huống sau.\n"
            f"LƯU Ý QUAN TRỌNG: KHÔNG tập trung vào các con số kinh doanh thuần túy (giá cả, chi phí, quy trình máy móc). HÃY tập trung bóc tách các khía cạnh tâm lý hành vi, ma sát nhận thức, động cơ cá nhân, và sự phù hợp vai trò (person-role fit).\n"
            f"Lăng kính triết học chủ đạo: {primary}\n"
            f"Tình huống thực tế: {scenario_text}\n"
            f"Trích dẫn tri thức tham khảo: {[getattr(u, 'title', str(u)) for u in (matched_units or [])]}\n\n"
            "TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU (Không bọc bằng markdown ```json):\n"
            "{\n"
            "  \"position_analysis\": \"Phân tích vị thế theo cấu trúc nghị luận chiến lược sâu sắc: "
            "(1) Thực chất cuộc diện & sự đứt gãy ngầm ẩn; (2) Động cơ, nỗi sợ và xung đột lợi ích cốt lõi giữa các bên; "
            "(3) Nguy cơ trượt dốc nếu xử lý theo cảm tính hoặc thụ động; (4) Điểm đòn bẩy cấu trúc để nắm quyền chủ động chuyển hóa tình thế. "
            "Viết đĩnh đạc, câu từ trau chuốt, thuật ngữ cổ phải giải thích ngay trong ngoặc.\",\n"
            "  \"step_1_anchor\": {\"title\": \"Tên bước 1\", \"verbatim\": \"Câu nói mẫu\"},\n"
            "  \"step_2_deadline_consequence\": {\"title\": \"Tên bước 2\", \"verbatim\": \"Câu nói mẫu\"},\n"
            "  \"step_3_way_out_plan_b\": {\"title\": \"Tên bước 3\", \"verbatim\": \"Câu nói mẫu\"},\n"
            "  \"draft_official_communication\": \"Văn bản mẫu/Công văn mẫu\",\n"
            "  \"financial_and_operational_directives\": [\"Chỉ thị 1\", \"Chỉ thị 2\"],\n"
            "  \"action_principles\": [\"Nguyên tắc 1\", \"Nguyên tắc 2\"]\n"
            "}"
        )
        return syn.generate_json(prompt)
    except Exception as e:
        print(f"[NhanThuatAPI] LLM script generation failed, using fallback: {e}")

    few_shots = get_dialogue_few_shots().get("templates", {})
    text_lower = scenario_text.lower()

    # 1. Human Resources / Person-Role Fit / Hiring & Promotion Scenario
    hr_keywords = ["nhân sự", "tuyển dụng", "bố trí", "vai trò", "tính cách", "nhân tài", "phỏng vấn", "đánh giá", "bổ nhiệm", "sa thải", "giữ chân", "hiệu suất", "năng lực"]
    if any(w in text_lower for w in hr_keywords):
        return {
            "position_analysis": (
                "Bản chất bài toán nhân sự này nằm ở sự sai lệch giữa thiên hướng tính cách tiềm ẩn mặc định của cá nhân "
                "và yêu cầu hành vi của vai trò (Chiếu theo Mô hình NT-MODEL-0007 & Nguyên tắc Chuẩn hóa Đánh giá NT-PRINCIPLE-0067). "
                "Nếu dùng quyền lực ép buộc hoặc chỉ phán xét bằng cảm tính, nhân sự sẽ tiêu hao năng lượng tự điều chỉnh, dẫn đến ma sát nhận thức, "
                "giảm sút hiệu năng hoặc chống đối ngầm. Nhà quản trị cần tách bạch giữa Năng lực cốt lõi và Gánh nặng thích ứng tình huống."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Chuẩn hóa Tiêu chuẩn & Thấu suốt Thiên hướng Cá nhân (NT-MODEL-0007)",
                "verbatim": (
                    f'"Chào [Tên Nhân sự/Ứng viên], tổ chức đánh giá rất cao thế mạnh và những đóng góp thực chất của bạn. '
                    f'Tuy nhiên, khi đối chiếu trực tiếp với yêu cầu của vai trò trong giai đoạn này, chúng ta cần một sự chuẩn hóa rõ ràng '
                    f'về mặt hành vi, trách nhiệm và tiêu chuẩn bàn giao kết quả (Hình Danh Tham Đồng). Chúng ta hãy cùng ngồi lại để định vị chính xác kỳ vọng hai bên."'
                )
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Đo lường Ma sát Thích ứng & Thiết lập Cơ chế Kiểm định (30-60 Ngày)",
                "verbatim": (
                    f'"Trong 30 ngày tới, tôi sẽ thiết lập 3 chỉ số hành vi then chốt cho vị trí này. '
                    f'Nếu bạn cảm thấy áp lực tự điều chỉnh quá lớn hoặc vai trò không phát huy được giá trị tốt nhất của bạn, '
                    f'tổ chức sẽ thẳng thắn thảo luận để tái cấu trúc phạm vi nhiệm vụ hoặc chuyển dịch sang vai trò phù hợp hơn, thay vì để sự ma sát kéo dài ảnh hưởng tới toàn đội ngũ."'
                )
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường Hỗ trợ Môi trường & Kế hoạch Dự phòng Bố trí (Plan B)",
                "verbatim": (
                    f'"Tổ chức sẵn sàng cung cấp các điểm tựa hỗ trợ: phân bổ người phối hợp bù trừ điểm khuyết và trao quyền chủ động trong vùng thế mạnh. '
                    f'Nhưng nếu sau thời gian thử thách, sự lệch pha vai trò vẫn gây tổn hại tới tiến độ chung, tôi sẽ chủ động kích hoạt phương án tái bố trí '
                    f'hoặc tạo điều kiện để bạn chuyển giao trong êm đẹp trên tinh thần tôn trọng tối đa."'
                )
            },
            "draft_official_communication": (
                f"THÔNG BÁO VỀ VIỆC THỐNG NHẤT TIÊU CHUẨN VAI TRÒ & LỘ TRÌNH ĐÁNH GIÁ\n"
                f"------------------------------------------------------------------\n"
                f"Kính gửi: [Họ và Tên Nhân Sự / Ứng Viên]\n\n"
                f"Căn cứ Định hướng Tái cơ cấu & Chuẩn hóa Năng lực Doanh nghiệp.\n"
                f"Ban Điều Hành xin gửi bản Thỏa thuận Tiêu chuẩn Vai trò (Role Expectation Framework):\n"
                f"1. Xác định 3 kết quả then chốt (Key Deliverables) và hành vi chuẩn mực được kỳ vọng.\n"
                f"2. Áp dụng cơ chế đánh giá định kỳ 15 ngày để đo lường mức độ tương thích thực tế.\n"
                f"3. Doanh nghiệp cam kết hỗ trợ tối đa về nguồn lực và môi trường để nhân sự bứt phá.\n\n"
                f"Trân trọng,\n[Ban Lãnh Đạo / Ban Nhân Sự]"
            ),
            "financial_and_operational_directives": [
                "👥 THIẾT KẾ LẠI VAI TRÒ (JOB REDESIGN): Bổ sung nhân sự hỗ trợ hành chính/vận hành để giải phóng thời gian cho nhân sự tập trung vào vùng thế mạnh chuyên môn.",
                "📊 CHUẨN HÓA ĐÁNH GIÁ (RUBRIC METRICS): Chuyển đổi từ đánh giá thái độ định tính sang đánh giá bằng rubric định lượng theo kết quả thực chứng (Hình Danh Tham Đồng).",
                "🛡️ CHỐT CHẶN DỰ PHÒNG (SUCCESSION PLAN): Chuẩn bị sẵn 01 ứng viên dự phòng bên ngoài hoặc nhân sự phó để sẵn sàng thế chỗ trong 14 ngày nếu có biến động."
            ],
            "action_principles": [
                "Không coi thiên hướng mặc định là giới hạn tuyệt đối của năng lực.",
                "Đo lường chi phí thích ứng để tránh đốt cháy năng lượng nhận thức nhân sự.",
                "Lấy Lễ định Phần (Tuân Tử): Rõ ràng về ranh giới quyền hạn và kỳ vọng kết quả."
            ]
        }

    # 2. Internal Conflict, Factions, Arrogance, Politics Scenario
    conflict_keywords = ["kiêu ngạo", "chia rẽ", "bè phái", "mâu thuẫn", "tranh chấp", "đố kỵ", "thao túng", "bằng mặt", "nói xấu", "chống đối", "bất mãn"]
    if any(w in text_lower for w in conflict_keywords):
        return {
            "position_analysis": (
                "Tình huống mâu thuẫn/chia rẽ này đang tạo ra sự rạn nứt cấu trúc quyền lực và đe dọa trực tiếp sự ổn định của tổ chức. "
                "Cá nhân hoặc nhóm đối lập đang dùng vị thế chuyên môn hoặc ảnh hưởng ngầm để yêu sách. "
                "Áp dụng lăng kính Pháp Gia kết hợp Nho Gia ('Hòa nhi bất đồng' & 'Khử Bát Gian'): Tách rời giữa tài năng cá nhân và kỷ cương hệ thống. "
                "Tuyệt đối không nhượng bộ trước hành vi thị uy quyền lực ngầm, nhưng cũng không xử lý thô bạo để tránh kích hoạt phản kháng tập thể."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Tách Biệt Tài Năng Khỏi Kỷ Cương (Hình Danh Tương Phù)",
                "verbatim": (
                    f'"[Tên Cá nhân/Đại diện], tổ chức luôn ghi nhận đầy đủ năng lực và thành tích cá nhân của bạn. '
                    f'Tuy nhiên, kỷ luật tổ chức và sự đoàn kết nội bộ là lằn ranh đỏ không thể thương lượng. '
                    f'Mọi đóng góp dù lớn đến đâu đều phải nằm trong khuôn khổ văn hóa chung. Không ai được phép đứng trên lợi ích tập thể."'
                )
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Thu Hẹp Phạm Vi Ảnh Hưởng & Thiết Lập Thế Cân Bằng (Counter-balance)",
                "verbatim": (
                    f'"Tôi yêu cầu mọi bất đồng phải được đưa ra thảo luận công khai, minh bạch trong cuộc họp giao ban sáng mai. '
                    f'Sau ngày hôm nay, bất kỳ hành vi lôi kéo bè phái hoặc gây chia rẽ nào bị phát hiện sẽ bị xem là cố tình phá hoại tổ chức, '
                    f'và tôi sẽ kích hoạt điều khoản đình chỉ chức vụ ngay lập tức mà không cần thêm cảnh cáo."'
                )
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường Hội Nhập 'Hòa Nhi Bất Đồng' & Chuẩn Bị Thay Thế (Plan B)",
                "verbatim": (
                    f'"Nếu bạn thực sự muốn cùng doanh nghiệp đi xa, hãy tập trung 100% năng lượng vào mục tiêu chung và hỗ trợ đồng đội. '
                    f'Cánh cửa ghi nhận và đãi ngộ xứng đáng luôn rộng mở. Nhưng nếu bạn tiếp tục giữ thái độ bất hợp tác, '
                    f'tôi đã chuẩn bị sẵn phương án phân quyền và chuyển giao công việc cho đội ngũ kế cận trong 24 giờ."'
                )
            },
            "draft_official_communication": (
                f"CHỈ ĐẠO CỦA CHỦ TỊCH / TỔNG GIÁM ĐỐC VỀ KỶ CƯƠNG & ĐOÀN KẾT NỘI BỘ\n"
                f"-------------------------------------------------------------------\n"
                f"Kính gửi: Toàn thể Cán bộ Quản lý và Đội ngũ Nhân sự\n\n"
                f"Để bảo đảm sức mạnh vận hành thống nhất trong giai đoạn chiến lược mới, Ban Điều Hành chỉ đạo:\n"
                f"1. Kiên quyết duy trì nguyên tắc 'Hòa nhi bất đồng' - Tự do tranh biện giải pháp, nhưng tuyệt đối thống nhất hành động.\n"
                f"2. Nghiêm cấm mọi hành vi chia rẽ, bài xích cá nhân hoặc bè phái cục bộ làm suy yếu sức mạnh tổ chức.\n"
                f"3. Cán bộ quản lý vi phạm kỷ luật văn hóa sẽ bị đình chỉ nhiệm vụ để thanh tra độc lập.\n\n"
                f"[Chủ Tịch Hội Đồng Quản Trị / Ban Điều Hành]"
            ),
            "financial_and_operational_directives": [
                "⚖️ PHÂN QUYỀN ĐỐI TRỌNG (COUNTER-BALANCE): Chia tách quyền hạn ký duyệt tài chính và nhân sự của bộ phận có nguy cơ bè phái để tránh thao túng cục bộ.",
                "🔍 KIỂM TOÁN VẬN HÀNH ĐỘC LẬP: Cử trợ lý điều hành hoặc thanh tra nội bộ tham gia các cuộc họp bộ phận để giám sát tính minh bạch thông tin.",
                "🛡️ BẢO VỆ NHÂN SỰ TRUNG LẬP: Trực tiếp đối thoại và bảo vệ các cá nhân có năng lực nhưng đang bị nhóm quyền lực ngầm cô lập."
            ],
            "action_principles": [
                "Khử Bát Gian (Hàn Phi Tử): Không để nhân sự lũng đoạn thông tin hoặc liên minh bè phái.",
                "Hòa nhi bất đồng (Nho Gia): Cho phép khác biệt về quan điểm, nhưng kỷ cương hành động là bất khả xâm phạm.",
                "Lập thế kiềm tỏa trước khi ra tay: Luôn có phương án nhân sự thay thế trước khi xử lý người tài có tì vết."
            ]
        }

    # 3. Debt collection & Payment Delay Scenario
    if any(w in text_lower for w in ["nợ", "đòi nợ", "quá hạn", "chậm thanh toán", "tiền hàng"]):
        return {
            "position_analysis": "Vụ việc đòi nợ / quá hạn thanh toán này đang làm tổn hại trực tiếp dòng tiền vận hành của doanh nghiệp. Nếu nhượng bộ bằng cảm tính, đối tác sẽ tiếp tục chiếm dụng vốn. Áp dụng lăng kính Pháp Gia ('Hình Danh Tương Phù') kết hợp Chế tài Nhị Bỉnh: Khóa công nợ, tính lãi phạt chậm trả và gửi công văn hạn định 48h trước khi chuyển sang cơ quan tư pháp/luật sư.",
            "step_1_anchor": {
                "title": "Bước 1: Khẳng định Căn cứ Công nợ & Hợp đồng (Hình Danh Tương Phù)",
                "verbatim": '"Kính gửi Anh/Chị [Tên Đại diện], theo Hợp đồng số [Số HĐ] và Biên bản chốt công nợ ngày [DD/MM/YYYY], khoản thanh toán đợt [X] trị giá [Số tiền] VNĐ đã quá hạn [Y] ngày. Phía chúng tôi luôn thiện chí hỗ trợ, nhưng việc chậm trả kéo dài đã vi phạm trực tiếp nghĩa vụ hợp đồng hai bên đã ký."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Ấn định Mốc Thanh toán & Kích hoạt Chế tài Phạt Chậm Trả",
                "verbatim": '"Yêu cầu Quý công ty hoàn tất giải ngân 100% khoản nợ quá hạn trước 17h00 ngày [DD/MM/YYYY]. Sau mốc thời hạn này, hệ thống kế toán sẽ tự động khóa toàn bộ đơn hàng mới, tính lãi phạt chậm trả 0.05%/ngày theo hợp đồng và tạm dừng hỗ trợ kỹ thuật hiện trường."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Lộ trình Trả góp & Kích hoạt Hồ sơ Pháp lý (Plan B)",
                "verbatim": '"Trường hợp Quý công ty gặp khó khăn dòng tiền ngắn hạn, chúng tôi chấp nhận phương án thanh toán 50% trước 17h00 ngày mai và chia nhỏ phần còn lại trong 14 ngày kèm cam kết bằng văn bản. Nếu không có cam kết trước 17h00, chúng tôi buộc phải chuyển toàn bộ hồ sơ cho Ban Pháp chế & Đơn vị Luật sư để thu hồi nợ theo quy định pháp luật."'
            },
            "draft_official_communication": (
                "CÔNG VĂN ĐÔN ĐỐC THANH TOÁN CÔNG NỢ QUÁ HẠN & THÔNG BÁO CHẾ TÀI\n"
                "---------------------------------------------------------------\n"
                "Kính gửi: Ban Giám Đốc [Tên Công Ty Đối Tác]\n\n"
                "Căn cứ Hợp đồng số [Số HĐ/2026] và Biên bản đối soát công nợ kỳ [Month/2026].\n"
                "Ban Điều Hành BusinessOS chính thức thông báo:\n"
                "1. Ghi nhận khoản nợ quá hạn đợt [X] trị giá [Số tiền] VNĐ, đã quá hạn [Y] ngày.\n"
                "2. Yêu cầu Quý công ty hoàn tất thanh toán trước 17h00 ngày [DD/MM/YYYY].\n"
                "3. Quá thời hạn trên, chúng tôi sẽ kích hoạt chế tài phạt chậm trả 0.05%/ngày, ngưng toàn bộ dịch vụ/giao hàng và chuyển hồ sơ thu hồi nợ cho Luật sư.\n\n"
                "Rất mong sự hợp tác khẩn trương của Quý công ty.\n"
                "[Ban Điều Hành BusinessOS]"
            ),
            "financial_and_operational_directives": [
                "💰 TẠM TẮT ĐƠN HÀNG MỚI: Khóa toàn bộ tài khoản đặt hàng và xuất kho đối với khách hàng đang nợ quá hạn.",
                "⚖️ CHẾ TÀI LÃI CHẬM TRẢ: Áp dụng lãi phạt 0.05%/ngày (18%/năm) đối với số tiền nợ quá hạn quá 7 ngày.",
                "🚀 KÍCH HOẠT HỒ SƠ PHÁP LÝ: Chuẩn bị sẵn hồ sơ thu hồi nợ qua Đơn vị Tư vấn Luật sư nếu đối tác không phản hồi sau 48h."
            ],
            "action_principles": [
                "Xác lập căn cứ công nợ minh bạch theo Hợp đồng.",
                "Không để đối tác chiếm dụng vốn vô thời hạn.",
                "Ấn định thời hạn 48h và lộ trình xử lý từng bước."
            ]
        }

    # 4. Labor Strike / Collective Worker Dispute Scenario
    if "đình công" in text_lower and "strike_labor" in few_shots:
        tmpl = few_shots["strike_labor"]
        return {
            "position_analysis": tmpl["position_analysis"],
            "step_1_anchor": {
                "title": "Bước 1: Thiết lập Vị thế & Quy chế Khoán (Hình Danh Tương Phù)",
                "verbatim": tmpl["direct_dialogue"]["step_1_anchor"]
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Ấn định Thời hạn & Chế tài Chấm dứt Hợp đồng Khoán",
                "verbatim": tmpl["direct_dialogue"]["step_2_deadline_consequence"]
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường lui & Thưởng Tiến độ khi Tuân thủ",
                "verbatim": tmpl["direct_dialogue"]["step_3_way_out_plan_b"]
            },
            "draft_official_communication": tmpl["ready_to_send_text"],
            "financial_and_operational_directives": [
                "💰 TẠM TẮT GIẢI NGÂN: Tạm dừng toàn bộ đợt giải ngân lương tuần này cho tổ đội vi phạm cho đến khi hoạt động thi công phục hồi 100%.",
                "⚖️ CHẾ TÀI HỢP ĐỒNG KHOÁN: Áp dụng Điều 2 Hợp đồng khoán - Chốt khối lượng hiện trạng và phạt 10% giá trị hợp đồng nếu cố tình vi phạm.",
                "🚀 THƯỞNG TIẾN ĐỘ TUÂN THỦ: Dành quỹ thưởng 5% cho các cá nhân công nhân tuân thủ và hoàn thành vượt định mức công việc tuần."
            ],
            "action_principles": [
                "Không thỏa hiệp với vi phạm kỷ luật ngưng việc tự phát.",
                "Đối chiếu hợp đồng khoán hiện trạng và ấn định thời hạn trở lại làm việc.",
                "Duy trì kênh đối thoại và thưởng tiến độ khi nhân sự tuân thủ."
            ]
        }

    # 5. Price Objection / Commercial Negotiation Scenario
    if any(w in text_lower for w in ["chê đắt", "giá cao", "báo giá", "chiết khấu", "giảm giá", "đắt"]):
        tmpl = few_shots.get("price_objection", {})
        return {
            "position_analysis": (
                "Khách hàng đang dùng chiến thuật 'chê giá cao' để thử thách tâm lý và ép chiết khấu. "
                "Nếu vội vàng giảm giá, ta tự thừa nhận biên lợi nhuận bị thổi phồng và làm xói mòn vị thế giải pháp. "
                "Áp dụng Thuật Hùng Biện (Aristotle) kết hợp Thấu cảm Chiến thuật FBI (Chris Voss): "
                "Bẻ gãy khung so sánh chi phí ban đầu, chuyển đổi tâm trí đối tác sang Tổng chi phí sở hữu (TCO) và Dòng tiền tiết kiệm 3 năm."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Thấu Cảm & Bẻ Khung Chi Phí (Tactical Empathy & Reframing)",
                "verbatim": (
                    '"Tôi hoàn toàn thấu hiểu mối bận tâm của Anh/Chị về ngân sách đầu tư ban đầu. '
                    'Tuy nhiên, nếu chỉ so sánh con số báo giá bề mặt, ta đang so sánh một hệ thống giải pháp vận hành bền vững 3 năm '
                    'với những phương án vá víu ngắn hạn mang đầy rủi ro ẩn. Giá trị thực sự của thương vụ này nằm ở sự an tâm dòng tiền dài hạn."'
                )
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Bóc Tách Rủi Ro & Đưa Ra Phản Đề (Consequence Probe)",
                "verbatim": (
                    '"Nếu chọn đối tác rẻ hơn 15%, Anh/Chị có thể tiết kiệm một khoản ngân sách tức thời. '
                    'Nhưng liệu Anh/Chị có sẵn sàng đánh đổi sự gián đoạn vận hành và chi phí khắc phục sự cố sau 6 tháng '
                    'cao gấp 3 lần khoản chênh lệch đó không?"'
                )
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Gia Tăng Giá Trị Kèm Điều Kiện Ràng Buộc (Closing Commitment)",
                "verbatim": (
                    '"Thay vì giảm trừ tiền mặt làm ảnh hưởng chất lượng triển khai, tôi xin tặng thêm Gói Bảo Trì & Cố Vấn Chuyên Sâu 12 tháng trị giá [X triệu]. '
                    'Đổi lại, tôi cần Anh/Chị phê duyệt hợp đồng trong tuần này để đội ngũ kỹ thuật kịp khóa lịch trình triển khai tối ưu nhất."'
                )
            },
            "draft_official_communication": (
                "THƯ THAM MƯU TỐI ƯU HIỆU QUẢ ĐẦU TƯ GỬI ĐỐI TÁC / KHÁCH HÀNG\n"
                "----------------------------------------------------------\n"
                "Kính gửi: Ban Lãnh Đạo [Tên Doanh Nghiệp Đối Tác]\n\n"
                "Chúng tôi đã xem xét thấu đáo các đề xuất ngân sách của Quý công ty.\n"
                "Triết lý của chúng tôi là không cạnh tranh bằng mức giá rẻ nhất, mà cam kết hiệu quả dòng tiền và độ tin cậy tối cao.\n"
                "Xin trân trọng gửi kèm Bản Phân Tích Tổng Chi Phí Sở Hữu (TCO 3 Năm) để minh chứng khoản tối ưu vận hành thực tế.\n\n"
                "Trân trọng,\n[Giám Đốc Chiến Lược / Kinh Doanh]"
            ),
            "financial_and_operational_directives": [
                "💰 GIỮ VỮNG ĐƠN GIÁ NIÊM YẾT: Không tự ý chiết khấu tiền mặt quá 3% ngân sách.",
                "📊 TỐI ƯU LỘ TRÌNH THANH TOÁN: Linh hoạt chia nhỏ thành 4 kỳ thanh toán để giải tỏa áp lực vốn ngắn hạn cho khách hàng.",
                "🎁 BÙ ĐẮP BẰNG DỊCH VỤ GIA TĂNG: Tặng kèm gói đào tạo chuyển giao công nghệ thay vì giảm trừ doanh thu."
            ],
            "action_principles": [
                "Rút củi đáy nồi: Đổi khung đối thoại từ Chi phí sang Dòng tiền và Rủi ro.",
                "Không nhượng bộ một chiều: Bất kỳ sự linh hoạt nào cũng phải đi kèm cam kết chốt hạn của đối tác.",
                "Tôn vinh giá trị giải pháp: Vị thế chuyên gia được xác lập bằng sự tự tin vào chuẩn mực kết quả."
            ]
        }

    # 6. Specific Material / Construction Delay Scenario
    if any(w in text_lower for w in ["vật tư", "giao hàng", "chậm giao", "nhà cung cấp"]) and any(w in text_lower for w in ["công trình", "thi công", "hiện trường"]):
        return {
            "position_analysis": "Nhà cung cấp đang vi phạm tiến độ giao nhận vật tư hiện trường. Nếu xử lý nể nang bằng tình cảm, công trình sẽ bị ngưng trệ dây chuyền và chịu thiệt hại nặng. Cần lập tức siết kỷ cương hợp đồng ('Hình Danh Tham Đồng') để buộc đối tác tập trung xe hàng giao bù trong 24h.",
            "step_1_anchor": {
                "title": "Bước 1: Thiết lập Vị thế & Căn cứ Hợp đồng (Hình Danh Tham Đồng)",
                "verbatim": '"Anh [Tên Đại diện NCC], theo Hợp đồng và Biên bản giao nhận đã ký, vật tư phải có mặt tại hiện trường muộn nhất hôm qua. Việc giao trễ đã làm đình trệ toàn bộ máy móc và nhân công. Chúng tôi làm việc chuẩn mực trên căn cứ hợp đồng, không chấp nhận các lý do khách quan ngoài văn bản."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Ấn định Mốc Thời Hạn & Kích Hoạt Chế Tài Phạt (Nhị Bỉnh)",
                "verbatim": '"Yêu cầu bên anh điều động xe hàng giao đủ 100% khối lượng trước 12h00 trưa mai. Quá thời hạn này, Ban Quản lý sẽ lập biên bản vi phạm đơn phương, tính phạt 0.5%/ngày và treo toàn bộ đợt giải ngân tiếp theo để bảo toàn thiệt hại."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường Lui & Kích Hoạt Nhà Cung Cấp Dự Phòng (Plan B)",
                "verbatim": '"Nếu bên anh nỗ lực giao đủ trước 17h00 chiều mai, chúng tôi sẽ xem xét miễn phạt đợt này. Nhưng nếu trưa mai hàng không tới, chúng tôi buộc phải cho đơn vị dự phòng nhập hàng thay thế và cấn trừ toàn bộ chi phí chênh lệch vào thanh toán bên anh."'
            },
            "draft_official_communication": (
                "CÔNG VĂN ĐÔN ĐỐC TIẾN ĐỘ GIAO HÀNG & THÔNG BÁO CHẾ TÀI HỢP ĐỒNG\n"
                "---------------------------------------------------------------\n"
                "Kính gửi: Ban Giám Đốc [Tên Đơn Vị Cung Cấp]\n\n"
                "Ban Quản Lý Dự Án chính thức thông báo:\n"
                "1. Ghi nhận vi phạm chậm tiến độ cung ứng làm ảnh hưởng trực tiếp tới kế hoạch thi công.\n"
                "2. Yêu cầu Quý công ty hoàn tất giao bù 100% khối lượng trước 12h00 ngày [DD/MM/YYYY].\n"
                "3. Quá thời hạn trên, chúng tôi sẽ kích hoạt chế tài phạt vi phạm theo Hợp đồng.\n\n"
                "Ban Quản Lý Dự Án"
            ),
            "financial_and_operational_directives": [
                "💰 TẠM GIỮ GIẢI NGÂN: Giữ lại 15% giá trị thanh toán đợt tiếp theo để bảo đảm tiến độ.",
                "⚖️ ÁP DỤNG PHẠT CHẬM TIẾN ĐỘ: Phạt 0.5%/ngày theo đúng điều khoản hợp đồng.",
                "🚀 KÍCH HOẠT NHÀ CUNG CẤP B: Nhập bù khối lượng thiếu từ nguồn dự phòng nếu quá 24h."
            ],
            "action_principles": [
                "Lấy Hợp đồng và hiện trạng làm căn cứ bất biến (Hình Danh Tham Đồng).",
                "Thưởng phạt minh bạch (Nhị Bỉnh), không để tình cảm làm mờ lý trí quản trị.",
                "Luôn duy trì giải pháp dự phòng Plan B tại mọi thời điểm."
            ]
        }

    # 7. Adaptive Fallback based on Primary Philosophy Lens
    if primary == "LEGALISM":
        return {
            "position_analysis": (
                f"Phân tích bối cảnh: \"{scenario_text[:80]}...\". Lăng kính Pháp Gia (Hàn Phi Tử) chỉ ra rằng: "
                "Khi xảy ra sự cố vận hành, nguồn gốc cốt lõi là ranh giới quyền hạn và trách nhiệm chưa tương thích (Hình Danh bất tương phù). "
                "Cần lập tức lập lại trật tự bằng quy chế minh bạch, áp dụng Nhị Bỉnh (Thưởng - Phạt phân minh) để loại trừ rủi ro thao túng."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Khẳng định Quy chế & Ranh giới Trách nhiệm (Hình Danh Tham Đồng)",
                "verbatim": f'"Chúng ta giải quyết tình huống này dựa trên căn cứ quy chuẩn và kết quả thực tế, không dựa trên cảm tính hay lời biện bạch cá nhân."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Ấn định Thời hạn Khắc phục & Chế tài Ràng buộc",
                "verbatim": f'"Yêu cầu các bên liên quan hoàn thành phương án khắc phục trước thời hạn ấn định. Mọi vi phạm cam kết sẽ chịu chế tài quy chế rõ ràng."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Cơ chế Phục hồi & Chuẩn bị Kế hoạch Dự phòng (Plan B)",
                "verbatim": f'"Những nỗ lực khắc phục kịp thời sẽ được ghi nhận và bảo lưu quyền lợi. Ngược lại, kế hoạch dự phòng độc lập sẽ kích hoạt ngay để đảm bảo an toàn hệ thống."'
            },
            "draft_official_communication": (
                f"THÔNG BÁO CHỈ ĐẠO XỬ LÝ VÀ CHUẨN HÓA QUY TRÌNH\n"
                f"----------------------------------------------\n"
                f"Kính gửi: Các Đơn Vị và Cá Nhân Liên Quan\n\n"
                f"Nội dung: Chỉ đạo giải quyết dứt điểm sự việc theo đúng quy chuẩn kỷ luật và mục tiêu điều hành.\n"
                f"Thời hạn báo cáo hoàn tất: Trước 17h00 ngày quy định.\n\n"
                f"Ban Điều Hành"
            ),
            "financial_and_operational_directives": [
                "⚖️ SIẾT CHẶT KỶ CƯƠNG: Tạm khóa các quyền duyệt đặc cách cho đến khi khắc phục xong sự cố.",
                "📋 LẬP BIÊN BẢN HIỆN TRẠNG: Xác lập chứng cứ khách quan trước khi đưa ra phán quyết.",
                "🛡️ BẢO VỆ DÒNG TIỀN: Rà soát các cam kết tài chính liên quan để triệt tiêu nguy cơ thất thoát."
            ],
            "action_principles": [
                "Hình Danh Tham Đồng: Danh nghĩa thế nào thì trách nhiệm và thẩm quyền tương ứng như thế.",
                "Nhị Bỉnh: Nắm chắc hai cán cân thưởng và phạt trong tay người điều hành.",
                "Tuyệt đối không dung dưỡng những vi phạm lặp lại làm xói mòn uy lực hệ thống."
            ]
        }
    elif primary == "CONFUCIAN":
        return {
            "position_analysis": (
                f"Phân tích bối cảnh: \"{scenario_text[:80]}...\". Lăng kính Nho Gia đề cao Đức Trị & Nhân Chính: "
                "Thu phục lòng người bằng sự chính trực (Tu thân lập đức) và duy trì sự hòa thuận sâu sắc (Hòa nhi bất đồng). "
                "Cần phân định rõ ràng giữa người Quân tử (hướng về đại cuộc) và kẻ Tiểu nhân (trục lợi cá nhân) để có đối sách thích hợp."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Lấy Đại Cuộc Làm Trọng & Lắng Nghe Thấu Đáo",
                "verbatim": f'"Mục tiêu cao nhất của chúng ta là sự hưng thịnh và bền vững của tập thể. Mọi cá nhân đều xứng đáng được lắng nghe trên tinh thần chân thành."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Chuẩn Hóa Lễ Nghĩa & Khơi Gợi Trách Nhiệm Tự Giác",
                "verbatim": f'"Tôi tin tưởng vào danh dự và lương tri nghề nghiệp của các bạn. Hãy hành động xứng đáng với vị thế và sự tin cậy mà tổ chức trao gửi."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường Cho Sự Hoàn Lương & Đãi Ngộ Người Có Đức",
                "verbatim": f'"Tổ chức luôn trân trọng những người biết vì đại cuộc. Những cống hiến âm thầm sẽ được đền đáp xứng đáng bằng cả sự nghiệp lâu dài."'
            },
            "draft_official_communication": (
                f"THƯ NGỎ CỦA NGƯỜI ĐỨNG ĐẦU VỀ TINH THẦN ĐỒNG LÒNG VÌ ĐẠI CUỘC\n"
                f"----------------------------------------------------------\n"
                f"Gửi toàn thể Đội ngũ Cộng sự,\n\n"
                f"Sức mạnh của chúng ta nằm ở sự đồng tâm hiệp lực và niềm tin lẫn nhau.\n"
                f"Mỗi thử thách là dịp để chúng ta tôi luyện bản lĩnh và khẳng định văn hóa cốt lõi.\n\n"
                f"Người Đứng Đầu Tổ Chức"
            ),
            "financial_and_operational_directives": [
                "👑 CHĂM LO PHÚC LỢI CỐT LÕI: Đảm bảo quyền lợi xứng đáng cho những nhân sự cống hiến bền bỉ.",
                "🤝 ĐỐI THOẠI CHÂN THÀNH: Tổ chức phiên gặp gỡ giải tỏa tâm tư cho các nhân sự chủ chốt.",
                "🌟 VINH DANH GƯƠNG SÁNG: Khen thưởng công khai các tấm gương vượt khó vì tập thể."
            ],
            "action_principles": [
                "Hòa nhi bất đồng: Hòa hợp nhưng giữ vững chính kiến và phẩm cách.",
                "Kỷ sở bất dục, vật thi ư nhân: Điều gì mình không muốn, đừng áp đặt cho người khác.",
                "Lãnh đạo bằng sự nêu gương trước khi đòi hỏi sự phục tùng."
            ]
        }
    elif primary == "TAOISM":
        return {
            "position_analysis": (
                f"Phân tích bối cảnh: \"{scenario_text[:80]}...\". Lăng kính Đạo Gia (Trang Tử & Lão Tử) dạy: "
                "Lấy tĩnh chế động, thuận theo tự nhiên (Vô Vi), không hấp tấp dùng sức đối đầu trực diện khi sóng gió đang cuộn trào. "
                "Áp dụng phương pháp Tâm Trai / Tọa Vọng để thanh lọc định kiến, nhận diện thế cục ngầm và vận dụng thuật 'Dụng Vô Dụng'."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Lấy Tĩnh Chế Động & Tách Khỏi Cơn Lốc Cảm Xúc (Tâm Trai)",
                "verbatim": f'"Lúc này càng nóng vội càng dễ sập bẫy định kiến. Chúng ta lùi lại một bước để nhìn thấu toàn cảnh dòng chảy sự việc."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Thuận Thế Điều Hướng & Biến Bất Lợi Thành Cơ Hội (Dụng Vô Dụng)",
                "verbatim": f'"Không đối đầu trực diện với lực cản. Hãy nương theo đà của đối phương để chuyển hướng năng lượng về phía có lợi cho chúng ta."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Giải Quyết Trong Êm Đẹp Tự Nhiên (Vô Vi Nhi Vô Bất Vi)",
                "verbatim": f'"Khi mọi nút thắt tự bộc lộ, sự việc sẽ tự tìm về trạng thái cân bằng mới mà không cần hao tổn quá nhiều sức lực."'
            },
            "draft_official_communication": (
                f"THÔNG ĐIỆP ĐIỀU HÀNH: GIỮ VỮNG TÂM THẾ TRONG BIẾN ĐỘNG\n"
                f"--------------------------------------------------\n"
                f"Kính gửi: Các Lãnh Đạo Đơn Vị\n\n"
                f"Yêu cầu giữ vững sự bình tĩnh, duy trì vận hành ổn định và không phát ngôn khi chưa có dữ liệu kiểm chứng.\n\n"
                f"Ban Cố Vấn Chiến Lược"
            ),
            "financial_and_operational_directives": [
                "🧘 TẠM DỪNG QUYẾT ĐỊNH VỘI VÃ: Không ký duyệt các điều chỉnh chính sách lớn khi cảm xúc các bên đang căng thẳng.",
                "🌊 BẢO TOÀN NGUYÊN KHÍ: Tập trung nguồn lực vào hoạt động cốt lõi mang lại dòng tiền an toàn.",
                "🔄 TÙY THỜI THÍCH ỨNG: Chuẩn bị kịch bản đón đầu khi đối phương tự bộc lộ sơ hở."
            ],
            "action_principles": [
                "Lấy nhu thắng cương, lấy nhược thắng cường.",
                "Tâm trai tọa vọng: Lắng lòng để nhìn thấy những điều mắt thường bỏ sót.",
                "Thuận theo tự nhiên, không cưỡng ép những điều chưa chín muồi."
            ]
        }
    else:  # XUNZI or general
        return {
            "position_analysis": (
                f"Phân tích bối cảnh: \"{scenario_text[:80]}...\". Lăng kính Tuân Tử chỉ ra: "
                "Con người vốn có thiên hướng tư lợi và quán tính buông thả (Thuyết Tính Ác). "
                "Nếu không có Lễ chế rèn nắn (Vĩ) và mentorship liên tục (Khuyên Học), tổ chức sẽ tự trượt vào hỗn loạn. "
                "Cần dùng quy chuẩn định phần để uốn nắn hành vi và nâng tầm chuẩn mực."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Xác Lập Khung Quy Chuẩn Rèn Nắn (Dùng Lễ Định Phần)",
                "verbatim": f'"Mọi vị trí đều cần được rèn giũa để đạt chuẩn mực cao nhất. Sự cố hôm nay là cơ hội để chúng ta uốn nắn lại quy trình."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Thiết Lập Lộ Trình Huấn Luyện & Sát Hạch Bắt Buộc",
                "verbatim": f'"Yêu cầu tham gia đợt sát hạch nâng chuẩn trong 7 ngày tới. Nhân sự vượt qua thử thách sẽ được trao thêm quyền hạn mới."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Công Nhận Sự Chuyển Hóa & Bồi Dưỡng Lâu Dài",
                "verbatim": f'"Tổ chức luôn trân quý những cộng sự có ý chí cầu tiến và sẵn sàng uốn nắn bản thân vì tiêu chuẩn hoàn hảo."'
            },
            "draft_official_communication": (
                f"KẾ HOẠCH NÂNG CHUẨN NĂNG LỰC & KỶ LUẬT THỰC THI\n"
                f"----------------------------------------------\n"
                f"Gửi: Toàn thể Cán bộ Đơn vị\n\n"
                f"Khởi động chương trình sát hạch quy chuẩn và nâng tầm kỹ năng chuyên môn.\n\n"
                f"Ban Đào Tạo & Quản Trị Hiệu Năng"
            ),
            "financial_and_operational_directives": [
                "📖 MENTORSHIP BẮT BUỘC: Ghép cặp nhân sự còn non với cán bộ kỳ cựu để rèn nắn thực chiến.",
                "🎯 TIÊU CHUẨN HÓA KPI: Gắn 30% kết quả đánh giá với mức độ tuân thủ quy chuẩn.",
                "🔄 TÁI BỐ TRÍ LINH HOẠT: Chuyển giao các nhân sự không cam kết học hỏi sang vị trí hỗ trợ."
            ],
            "action_principles": [
                "Tính ác - Nhân vi vi: Con người cần sự rèn giũa có ý thức để trở nên hoàn thiện.",
                "Khuyên học: Việc học tập và rèn luyện kỹ năng phải diễn ra liên tục, không ngừng nghỉ.",
                "Dùng Lễ định phần: Phân định ranh giới chức trách để ngăn chặn tranh chấp."
            ]
        }


def diagnose_person_role_fit(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluates alignment between personal default traits and role behavioral expectations
    based on NT-MODEL-0007 (Person-Role Fit Model) and NT-PRINCIPLE-0067 (Standardize Evaluation).
    """
    candidate_name = payload.get("candidate_name", "").strip() or "Nhân sự"
    target_role = payload.get("target_role", "").strip() or "Vị trí quản lý"
    raw_traits = payload.get("traits", [])
    raw_demands = payload.get("role_demands", [])
    context = payload.get("context", "")

    # Normalize traits and demands
    traits = [t.strip() for t in raw_traits if t.strip()] if isinstance(raw_traits, list) else [s.strip() for s in str(raw_traits).split(",") if s.strip()]
    demands = [d.strip() for d in raw_demands if d.strip()] if isinstance(raw_demands, list) else [s.strip() for s in str(raw_demands).split(",") if s.strip()]

    if not traits:
        traits = ["Thiên hướng sáng tạo", "Thích tự chủ cao", "Ngại xung đột trực diện", "Nhạy bén cơ hội"]
    if not demands:
        demands = ["Kỷ luật quy trình nghiêm ngặt", "Đàm phán căng thẳng", "Chịu áp lực số hàng tuần", "Quản lý giám sát chi tiết"]

    # 1. Try to generate dynamically via LLM
    try:
        from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
        syn = KnowledgeSynthesizer()
        prompt = (
            f"Chẩn đoán độ tương thích Person-Role Fit (NT-MODEL-0007).\n"
            f"Nhân sự: {candidate_name}\n"
            f"Vai trò: {target_role}\n"
            f"Thiên hướng cá nhân: {traits}\n"
            f"Yêu cầu vai trò: {demands}\n\n"
            "TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU (Không bọc bằng markdown ```json):\n"
            "{\n"
            "  \"friction_score\": 75, (số nguyên từ 0 đến 100, 100 là cực kỳ xung đột)\n"
            "  \"fit_level\": \"Lệch Pha Nhận Thức Lớn | Ma Sát Thích Ứng Trung Bình | Tương Thích Cao\",\n"
            "  \"fit_color\": \"#ef4444 | #f59e0b | #10b981\",\n"
            "  \"adaptation_cost_analysis\": \"Phân tích chi phí thích ứng nhận thức\",\n"
            "  \"identified_friction_points\": [\"Điểm ma sát 1\", \"Điểm ma sát 2\"],\n"
            "  \"compensatory_strategies\": [\"Chiến lược bù trừ 1\", \"Chiến lược bù trừ 2\"],\n"
            "  \"placement_verdict\": \"Phán quyết bổ nhiệm (VD: CÂN NHẮC TÁI THIẾT KẾ VAI TRÒ HOẶC CHỌN ỨNG VIÊN BÙ TRỪ)\"\n"
            "}"
        )
        result = syn.generate_json(prompt)
        result["status"] = "success"
        result["candidate_name"] = candidate_name
        result["target_role"] = target_role
        result["cited_units"] = [
            {"id": "NT-MODEL-0007", "title": "Mô hình tương thích cá nhân - vai trò", "domain": "tri-nhan"},
            {"id": "NT-PRINCIPLE-0067", "title": "Chuẩn hóa đánh giá", "domain": "tri-nhan"},
            {"id": "NT-LAW-0034", "title": "Quy luật ma sát nhận thức", "domain": "tri-nhan"}
        ]
        return result
    except Exception as e:
        print(f"[NhanThuatAPI] LLM fit diagnosis failed, using fallback: {e}")

    # Trait vs Demand friction heuristic
    friction_points = []
    traits_text = " ".join(traits).lower()
    demands_text = " ".join(demands).lower()

    if any(k in traits_text for k in ["tự do", "tự chủ", "sáng tạo", "linh hoạt"]) and any(k in demands_text for k in ["kỷ luật", "quy trình", "nghiêm ngặt", "giám sát", "chi tiết"]):
        friction_points.append("Ma sát giữa nhu cầu tự do sáng tạo và kỳ vọng tuân thủ quy trình kiểm soát chặt chẽ.")

    if any(k in traits_text for k in ["ngại xung đột", "dĩ hòa", "nhân từ", "cảm xúc"]) and any(k in demands_text for k in ["đàm phán", "căng thẳng", "sa thải", "thu nợ", "áp lực số", "rắn mặt"]):
        friction_points.append("Chi phí nhận thức cao khi phải đối đầu trực diện hoặc đưa ra các phán quyết cứng rắn.")

    if any(k in traits_text for k in ["chuyên môn sâu", "hướng nội", "ít nói"]) and any(k in demands_text for k in ["ngoại giao", "xây dựng quan hệ", "thuyết trình", "lôi kéo bè phái", "networking"]):
        friction_points.append("Hao tổn năng lượng tự điều chỉnh trong các tương tác xã hội cường độ cao ngoài chuyên môn.")

    if not friction_points:
        friction_points.append("Cần theo dõi mức độ căng thẳng nhận thức trong 30 ngày đầu để xác định điểm nghẽn ẩn.")

    # Calculate adaptation friction score
    friction_score = min(85, max(25, 30 + len(friction_points) * 20))
    if friction_score < 40:
        fit_level = "Tương Thích Cao (High Alignment)"
        fit_color = "#10b981"
    elif friction_score <= 65:
        fit_level = "Ma Sát Thích Ứng Trung Bình (Manageable Friction)"
        fit_color = "#f59e0b"
    else:
        fit_level = "Lệch Pha Nhận Thức Lớn (High Risk Friction)"
        fit_color = "#ef4444"

    return {
        "status": "success",
        "candidate_name": candidate_name,
        "target_role": target_role,
        "friction_score": friction_score,
        "fit_level": fit_level,
        "fit_color": fit_color,
        "adaptation_cost_analysis": (
            f"Khi cá nhân [{candidate_name}] với các thiên hướng mặc định ({', '.join(traits[:3])}) "
            f"đảm nhiệm vị trí [{target_role}] đòi hỏi ({', '.join(demands[:3])}), "
            f"hệ thống ước tính mức độ ma sát nhận thức ở mức {friction_score}%. "
            f"Nhân sự sẽ phải liên tục kích hoạt cơ chế tự kiểm soát hành vi (self-regulation), "
            f"có thể dẫn đến kiệt sức nếu môi trường làm việc không có sự hỗ trợ bổ trợ."
        ),
        "identified_friction_points": friction_points,
        "compensatory_strategies": [
            "Bố trí 01 cộng sự có thiên hướng bù trừ (ví dụ: người mạnh chi tiết bổ trợ cho người mạnh ý tưởng).",
            "Tạo không gian tự chủ trong phạm vi chuyên môn cốt lõi, giảm bớt các cuộc họp điều hành không cần thiết.",
            "Chuẩn hóa tiêu chuẩn đánh giá đầu ra (NT-PRINCIPLE-0067) thay vì giám sát vi mô phương pháp làm việc."
        ],
        "placement_verdict": (
            "BỔ NHIỆM CÓ ĐIỀU KIỆN KÈM HỖ TRỢ MÔI TRƯỜNG" if friction_score <= 65 else "CÂN NHẮC TÁI THIẾT KẾ VAI TRÒ HOẶC CHỌN ỨNG VIÊN BÙ TRỪ"
        ),
        "cited_units": [
            {"id": "NT-MODEL-0007", "title": "Mô hình tương thích cá nhân - vai trò", "domain": "tri-nhan"},
            {"id": "NT-PRINCIPLE-0067", "title": "Chuẩn hóa đánh giá", "domain": "tri-nhan"},
            {"id": "NT-LAW-0034", "title": "Quy luật ma sát nhận thức", "domain": "tri-nhan"}
        ]
    }


def diagnose_team_structural_fit(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluates team structural compatibility, emergent interaction friction (NT-MODEL-0009),
    and detects the Homogeneity Trap (NT-ANTI-PATTERN-0011 & NT-ANTI-PATTERN-0017)
    under the principle of Selecting for Structural Fit (NT-PRINCIPLE-0066) and Cognitive Diversity (NT-LAW-0042).
    """
    candidate = payload.get("candidate", {})
    team = payload.get("team", {})

    candidate_name = candidate.get("name", "").strip() or payload.get("candidate_name", "").strip() or "Nhân sự mới"
    candidate_role = candidate.get("role", "").strip() or payload.get("candidate_role", "").strip() or "Thành viên chủ chốt"
    raw_cand_traits = candidate.get("traits", []) or payload.get("candidate_traits", [])

    team_name = team.get("name", "").strip() or payload.get("team_name", "").strip() or "Ban Điều Hành / Đội Ngũ Dự Án"
    team_mission = team.get("mission", "").strip() or payload.get("team_mission", "").strip() or "Thực thi mục tiêu chiến lược"
    raw_team_traits = team.get("traits", []) or payload.get("team_traits", [])

    def _norm(raw: Any) -> list[str]:
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]
        return [s.strip() for s in str(raw).split(",") if s.strip()]

    cand_traits = _norm(raw_cand_traits)
    team_traits = _norm(raw_team_traits)

    if not cand_traits:
        cand_traits = ["Tự do sáng tạo", "Tư duy cơ hội", "Thích tự chủ cao"]
    if not team_traits:
        team_traits = ["Kỷ luật quy trình nghiêm ngặt", "Giám sát số liệu chi tiết", "Ngại xung đột trực diện"]

    # 1. Dynamic LLM Generation
    try:
        from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
        syn = KnowledgeSynthesizer()
        prompt = (
            f"Chẩn đoán khớp cấu trúc đội ngũ Team Structural Fit (NT-PRINCIPLE-0066, NT-MODEL-0009, NT-ANTI-PATTERN-0011).\n"
            f"Nhân sự mới: {candidate_name} (Dự kiến vai trò: {candidate_role})\n"
            f"Thiên hướng nhân sự: {cand_traits}\n"
            f"Đội ngũ tiếp nhận: {team_name} (Sứ mệnh: {team_mission})\n"
            f"Đặc tính nhận thức hiện tại của đội ngũ: {team_traits}\n\n"
            "TRẢ VỀ ĐÚNG ĐỊNH DẠNG JSON SAU (Không bọc bằng markdown ```json):\n"
            "{\n"
            "  \"diversity_score\": 75, (số nguyên 0-100, đo độ đa dạng nhận thức tích cực)\n"
            "  \"homogeneity_risk_score\": 25, (số nguyên 0-100, đo nguy cơ bẫy đồng nhất và điểm mù)\n"
            "  \"structural_alignment_level\": \"Khớp Cấu Trúc Bổ Trợ | Cân Bằng Có Ma Sát | Bẫy Đồng Nhất Nguy Hiểm | Xung Đột Tương Tác Phát Sinh\",\n"
            "  \"status_color\": \"#10b981 | #f59e0b | #ef4444\",\n"
            "  \"structural_analysis\": \"Phân tích tương tác phát sinh khi nhân sự bước vào cấu trúc đội ngũ\",\n"
            "  \"emergent_frictions\": [\"Ma sát phát sinh 1\", \"Ma sát phát sinh 2\"],\n"
            "  \"systemic_blind_spots\": [\"Điểm mù hệ thống 1\", \"Điểm mù 2\"],\n"
            "  \"structural_directives\": [\"Chỉ thị cấu trúc 1\", \"Chỉ thị cấu trúc 2\"],\n"
            "  \"composition_verdict\": \"Phán quyết chuẩn bị và bố trí đội ngũ\"\n"
            "}"
        )
        result = syn.generate_json(prompt)
        result["status"] = "success"
        result["candidate_name"] = candidate_name
        result["candidate_role"] = candidate_role
        result["team_name"] = team_name
        result["cited_units"] = [
            {"id": "NT-PRINCIPLE-0066", "title": "Tuyển chọn theo sự khớp cấu trúc", "domain": "tri-nhan"},
            {"id": "NT-MODEL-0009", "title": "Mô hình tương tác phát sinh", "domain": "tri-nhan"},
            {"id": "NT-ANTI-PATTERN-0011", "title": "Bẫy đồng nhất (Homogeneity Trap)", "domain": "hop-chung"},
            {"id": "NT-LAW-0042", "title": "Quy luật đa dạng nhận thức", "domain": "hop-chung"},
            {"id": "NT-MODEL-0012", "title": "Đường cong gắn kết - ma sát", "domain": "hop-chung"}
        ]
        return result
    except Exception as e:
        print(f"[NhanThuatAPI] LLM team structural fit failed, using fallback: {e}")

    # 2. Deterministic Heuristic Analysis
    cand_text = " ".join(cand_traits).lower()
    team_text = " ".join(team_traits).lower()

    # Shared keywords / traits count
    overlap_count = 0
    keywords_list = ["sáng tạo", "tự chủ", "kỷ luật", "chi tiết", "xung đột", "quyết đoán", "cơ hội", "chuyên môn", "quyền lực"]
    for kw in keywords_list:
        if kw in cand_text and kw in team_text:
            overlap_count += 1

    blind_spots = []
    emergent_frictions = []
    structural_directives = []

    # 1. Check Emergent Friction / Power Conflict (NT-MODEL-0009)
    if ("quyết đoán" in cand_text or "quyền lực" in cand_text or "áp đặt" in cand_text) and \
       ("quyết đoán" in team_text or "quyền lực" in team_text or "áp đặt" in team_text):
        homogeneity_risk_score = 45
        diversity_score = 55
        structural_alignment_level = "Xung Đột Tương Tác Phát Sinh (Emergent Power Conflict)"
        status_color = "#f59e0b"
        emergent_frictions.append("Nguy cơ phân tranh phạm vi ảnh hưởng và va chạm quyền lực ngầm giữa các thành viên có bản năng chi phối cao.")
        emergent_frictions.append("Căng thẳng nhận thức gia tăng khi ra quyết định trong điều kiện ranh giới trách nhiệm không rõ ràng.")
        structural_directives.append("Áp dụng nguyên tắc Dùng Lễ Định Phần (Tuân Tử): Phân định tuyệt đối ranh giới quyền hạn và mục tiêu đo lường.")
        structural_directives.append("Thiết lập cơ chế trọng tài trung gian (Confucian/Legalism) khi có bất đồng quan điểm chiến lược.")
        composition_verdict = "BỔ NHIỆM KÈM PHÂN ĐỊNH RANH GIỚI BẮT BUỘC ĐỂ NGĂN XUNG ĐỘT QUYỀN LỰC"
    # 2. Check Homogeneity Trap (NT-ANTI-PATTERN-0011)
    elif overlap_count >= 2 or (("hòa hoãn" in cand_text or "ngại xung đột" in cand_text) and ("hòa hoãn" in team_text or "ngại xung đột" in team_text)):
        homogeneity_risk_score = 85
        diversity_score = 25
        structural_alignment_level = "Bẫy Đồng Nhất Nguy Hiểm (Homogeneity Trap)"
        status_color = "#ef4444"
        blind_spots.append("Thiếu năng lực phản biện đối kháng; đội ngũ dễ rơi vào tư duy tập thể (Groupthink) và thiên kiến xác nhận.")
        blind_spots.append("Chậm phát hiện sai sót trong giả định kinh doanh do các thành viên có chung điểm mù nhận thức.")
        emergent_frictions.append("Ma sát thấp giả tạo trong ngắn hạn nhưng tích tụ rủi ro bùng nổ khi gặp khủng hoảng bên ngoài.")
        structural_directives.append("Bắt buộc chỉ định vai trò Phản Biện Độc Lập (Devil's Advocate) trong mọi quyết định trọng yếu.")
        structural_directives.append("Bổ sung nhân sự có thiên hướng đối nghịch để phá vỡ cấu trúc đồng nhất (NT-LAW-0042).")
        composition_verdict = "CẢNH BÁO BẪY ĐỒNG NHẤT: CẦN BỔ TRỢ NHÂN SỰ CÓ PHONG CÁCH TƯ DUY ĐỐI TRỌNG"
    # 3. Complementary / Structural Fit (NT-PRINCIPLE-0066)
    else:
        homogeneity_risk_score = 25
        diversity_score = 85
        structural_alignment_level = "Khớp Cấu Trúc Bổ Trợ (High Complementarity)"
        status_color = "#10b981"
        emergent_frictions.append("Cần thời gian điều chỉnh nhịp giao tiếp giữa phong cách sáng tạo/tự do và kỷ luật quy trình sẵn có.")
        structural_directives.append("Thiết lập cơ chế Tương Thuộc Bắt Buộc (NT-PRINCIPLE-0071): Buộc nhân sự mới và đội ngũ hiện tại phải phụ thuộc đầu ra của nhau.")
        structural_directives.append("Tận dụng góc nhìn mới để rà soát các quy trình cũ đã xơ cứng.")
        composition_verdict = "CẤU TRÚC BỔ TRỢ TỐI ƯU: ĐỀ XUẤT TIẾP NHẬN VÀ THIẾT LẬP CƠ CHẾ PHỐI HỢP"

    structural_analysis = (
        f"Đội ngũ [{team_name}] với đặc tính nhận thức nền ({', '.join(team_traits[:3])}) "
        f"khi tiếp nhận nhân sự [{candidate_name}] mang thiên hướng ({', '.join(cand_traits[:3])}), "
        f"hệ thống xác định chỉ số đa dạng nhận thức ở mức {diversity_score}% và nguy cơ bẫy đồng nhất ở mức {homogeneity_risk_score}%. "
        f"Trạng thái cấu trúc: {structural_alignment_level}."
    )

    return {
        "status": "success",
        "candidate_name": candidate_name,
        "candidate_role": candidate_role,
        "team_name": team_name,
        "diversity_score": diversity_score,
        "homogeneity_risk_score": homogeneity_risk_score,
        "structural_alignment_level": structural_alignment_level,
        "status_color": status_color,
        "structural_analysis": structural_analysis,
        "emergent_frictions": emergent_frictions,
        "systemic_blind_spots": blind_spots,
        "structural_directives": structural_directives,
        "composition_verdict": composition_verdict,
        "cited_units": [
            {"id": "NT-PRINCIPLE-0066", "title": "Tuyển chọn theo sự khớp cấu trúc", "domain": "tri-nhan"},
            {"id": "NT-MODEL-0009", "title": "Mô hình tương tác phát sinh", "domain": "tri-nhan"},
            {"id": "NT-ANTI-PATTERN-0011", "title": "Bẫy đồng nhất (Homogeneity Trap)", "domain": "hop-chung"},
            {"id": "NT-LAW-0042", "title": "Quy luật đa dạng nhận thức", "domain": "hop-chung"},
            {"id": "NT-MODEL-0012", "title": "Đường cong gắn kết - ma sát", "domain": "hop-chung"}
        ]
    }


def process_nhan_thuat_analysis(scenario_text: str, scenario_type_hint: str = "general") -> dict[str, Any]:
    orchestrator = get_orchestrator()
    text_lower = scenario_text.lower()

    # 0. Context Ambiguity Check
    is_ambiguous, warning_msg = check_context_ambiguity(scenario_text)

    # 0. Check Interactive Sparring / Roleplay Mode
    if scenario_type_hint == "sparring":
        from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
        syn = KnowledgeSynthesizer()
        sparring_prompt = (
            f"Bạn đang đóng vai trò là một ĐỐI TÁC ĐÀM PHÁN / NHÂN SỰ CỰC KỲ RẮN MẶT, lão luyện, sắc sảo và kiên quyết bảo vệ tối đa quyền lợi của mình trong một phiên thương lượng thực chiến.\n\n"
            f"LỜI THOẠI / LẬP LUẬN CỦA NGƯỜI DÙNG: \"{scenario_text}\"\n\n"
            f"NHIỆM VỤ CỦA BẠN (TRẢ LỜI BẰNG MARKDOWN CHIA LÀM 2 PHẦN):\n\n"
            f"### ⚔️ 1. ĐỐI ĐÁP PHẢN BIỆN TRỰC DIỆN (LỜI THOẠI ĐỐI KHÁNG)\n"
            f"(Hãy cất lời thoại với thái độ sắc sảo, tự tin, xoáy thẳng vào điểm yếu hoặc chỗ chưa chặt chẽ trong lời nói của người dùng. Dùng lý lẽ đanh thép để đẩy quả bóng trách nhiệm hoặc bảo vệ mức giá/điều kiện của mình).\n\n"
            f"### 💡 2. GỢI Ý ĐÒN BẨY HÓA GIẢI (GÓC NHÌN CỐ VẤN NHÂN THUẬT)\n"
            f"- **Điểm sơ hở trong lập luận vừa rồi:** [Chỉ ra ngắn gọn]\n"
            f"- **Đòn bẩy Binh pháp / Tâm lý nên dùng ở lượt tiếp theo:** [Đưa ra câu gợi ý đối đáp sắc bén nhất để người dùng lật ngược thế cờ]."
        )
        try:
            generated_text = syn.generate_text(sparring_prompt)
            from nhan_thuat.runtime.synthesizer import provider_name as _provider_name, _model as _synth_model
            return {
                "status": "success",
                "scenario_text": scenario_text,
                "is_ambiguous": False,
                "ambiguity_warning": "",
                "philosophy_routing": {
                    "primary_philosophy": "SPARRING_ADVERSARIAL",
                    "secondary_philosophy": "BEHAVIORAL",
                    "tertiary_philosophy": "SUNZI",
                },
                "synthesis_result": {
                    "mode": "llm",
                    "synthesis": generated_text,
                    "citations": [],
                    "audit": {
                        "provider": _provider_name(),
                        "model": _synth_model(),
                        "correlation_id": f"CORR-SPAR-{uuid.uuid4().hex[:8].upper()}"
                    }
                },
                "correlation_id": f"CORR-SPAR-{uuid.uuid4().hex[:8].upper()}",
            }
        except Exception:
            pass  # fall through to standard synthesis

    # 1. Determine scenario type
    ops_keywords = ["vật tư", "nhà cung cấp", "chậm tiến độ", "công trình", "thi công", "hợp đồng", "chế tài", "vi phạm hợp đồng", "trách nhiệm", "nợ", "đòi nợ", "thanh toán"]
    if any(w in text_lower for w in ops_keywords) or any(w in text_lower for w in ["báo cáo láo", "dối trá", "kỷ luật", "vi phạm", "đình công", "quy chế"]):
        scenario_type = "governance"
    elif any(w in text_lower for w in ["chê", "đắt", "báo giá", "từ chối", "giá"]):
        scenario_type = "objection"
    elif any(w in text_lower for w in ["đào tạo", "hướng dẫn", "mentorship", "huấn luyện", "onboarding"]):
        scenario_type = "training"
    elif any(w in text_lower for w in ["tranh chấp", "mâu thuẫn", "xung đột", "bất đồng"]):
        scenario_type = "conflict"
    elif any(w in text_lower for w in ["lãnh đạo", "văn hóa", "tâm trí", "quản trị"]):
        scenario_type = "leadership"
    else:
        scenario_type = scenario_type_hint

    # 2. Route Philosophy Router
    router_res = orchestrator.philosophy_router.route({
        "scenario_type": scenario_type,
        "intent": scenario_text,
        "keywords": scenario_text.split(),
    })

    # 3. Match Knowledge Units
    matched_units = find_relevant_units(scenario_text, orchestrator.knowledge_engine, top_k=3)
    
    # If no match from synonyms, pass ALL units so Gemini can act as a retriever
    all_units = list(orchestrator.knowledge_engine.units_by_id.values())
    units_for_synthesis = matched_units if len(matched_units) >= 1 else all_units

    # Convert IndexedUnit to KnowledgeUnit expected by synthesizer
    from nhan_thuat.models import KnowledgeUnit
    knowledge_units = [KnowledgeUnit.from_mapping(u.raw_data) for u in units_for_synthesis]

    # 4. Generate Actionable Script
    primary_phil = router_res.get("primary_philosophy", "NONE").upper()
    action_script = generate_actionable_script_details(primary_phil, scenario_text)

    # 5. Use KnowledgeSynthesizer to generate exact Streamlit format
    from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer
    synthesizer = KnowledgeSynthesizer()
    synthesis_result = synthesizer.synthesize(scenario_text, knowledge_units)

    correlation_id = f"CORR-WEB-{uuid.uuid4().hex[:8].upper()}"

    matched_units_payload = [
        {
            "unit_id": u.unit_id,
            "title": u.title,
            "domain": u.domain,
            "unit_type": u.unit_type,
            "summary": u.raw_data.get("summary", ""),
            "checksum": u.checksum,
        }
        for u in matched_units
    ]

    return {
        "status": "success",
        "scenario_text": scenario_text,
        "is_ambiguous": is_ambiguous,
        "ambiguity_warning": warning_msg if is_ambiguous else "",
        "philosophy_routing": {
            "primary_philosophy": primary_phil,
            "secondary_philosophy": router_res.get("secondary_philosophy"),
            "tertiary_philosophy": router_res.get("tertiary_philosophy"),
            "lens_weights": router_res.get("lens_weights", {}),
            "lens_confidence_scores": router_res.get("lens_confidence_scores", {}),
            "conflict_resolution": router_res.get("conflict_resolution", {}),
            "explanation": router_res.get("explanation", ""),
        },
        "matched_knowledge_units": matched_units_payload,
        "matched_custom_docs": [],
        "action_script": action_script,
        "synthesis_result": synthesis_result,  # This contains mode, synthesis, citations, audit
        "correlation_id": correlation_id,
    }
