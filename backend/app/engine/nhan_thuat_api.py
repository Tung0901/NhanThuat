"""
NhanThuat Knowledge Engine & BusinessOS Cognitive API Handler.
Provides detailed actionable execution scripts, step-by-step dialogues, draft communications, financial & operational directives, and custom RAG docs matching.
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.app.engine.runtime import BusinessOSRuntimeOrchestrator
from nhan_thuat.knowledge_engine import IndexedUnit, KnowledgeEngine

_orchestrator: BusinessOSRuntimeOrchestrator = None
_dialogue_few_shots: Dict[str, Any] = None


def get_orchestrator() -> BusinessOSRuntimeOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = BusinessOSRuntimeOrchestrator()
    return _orchestrator


def get_dialogue_few_shots() -> Dict[str, Any]:
    global _dialogue_few_shots
    if _dialogue_few_shots is None:
        template_file = Path(__file__).resolve().parent.parent.parent / "docs" / "templates" / "dialogue_few_shots.json"
        if template_file.exists():
            try:
                _dialogue_few_shots = json.loads(template_file.read_text(encoding="utf-8"))
            except Exception:
                _dialogue_few_shots = {}
        else:
            _dialogue_few_shots = {}
    return _dialogue_few_shots


def find_relevant_units(scenario_text: str, engine: KnowledgeEngine, top_k: int = 3) -> List[IndexedUnit]:
    text_lower = scenario_text.lower()
    synonym_map = {
        "báo cáo láo": ["báo cáo", "dối", "sự thật", "hình danh", "chức danh", "kỷ luật", "truth", "threat", "formal", "position"],
        "đình công": ["đình công", "lương", "tranh chấp", "đòi", "tổ đội", "quyền lợi", "xung đột", "coercive", "compliance", "structural", "fit"],
        "đắt": ["đắt", "giá", "báo giá", "chi phí", "từ chối", "khách hàng", "giá trị", "khung", "rhetoric", "framing", "exchange"],
        "đòi nợ": ["nợ", "đòi nợ", "quá hạn", "thanh toán", "tiền hàng", "thu hồi", "công nợ"],
        "vật tư": ["vật tư", "nhà cung cấp", "hợp đồng", "tiến độ", "chậm", "chế tài", "vi phạm", "giao"],
        "nhà cung cấp": ["nhà cung cấp", "vật tư", "hợp đồng", "tiến độ", "chậm", "chế tài"],
        "nhà bè": ["công trình", "thi công", "hiện trường", "dự án", "địa điểm", "tiến độ", "nhà cung cấp"],
        "công trình": ["thi công", "hiện trường", "dự án", "tiến độ", "chậm"],
    }

    tokens = [t.strip() for t in text_lower.split() if len(t.strip()) > 1]
    expanded_tokens = list(tokens)

    for key, syn_list in synonym_map.items():
        if key in text_lower:
            expanded_tokens.extend(syn_list)

    scores: Dict[str, Tuple[int, IndexedUnit]] = {}
    for unit_id, unit in engine.units_by_id.items():
        score = 0
        raw = unit.raw_data
        unit_text = f"{unit.unit_id} {unit.title} {unit.domain} {unit.unit_type} {raw.get('summary', '')} {raw.get('definition', '')} {' '.join(unit.tags)} {' '.join(raw.get('key_mechanisms', []))} {' '.join(raw.get('operational_rules', []))}".lower()

        for token in expanded_tokens:
            if token in unit_text:
                score += 2
            if token in unit.title.lower():
                score += 5
            if token in unit.tags:
                score += 4
            if token in unit.domain.lower():
                score += 3

        if score > 0:
            scores[unit_id] = (score, unit)

    if not scores:
        return list(engine.units_by_id.values())[:top_k]

    sorted_units = sorted(scores.values(), key=lambda x: (x[0], x[1].unit_id), reverse=True)
    return [u[1] for u in sorted_units[:top_k]]


def check_context_ambiguity(scenario_text: str) -> Tuple[bool, str]:
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


def generate_actionable_script_details(primary: str, scenario_text: str) -> Dict[str, Any]:
    """Generates Senior Executive Co-Pilot Strategic Analysis, 3-step verbatim dialogue, draft communications, and financial/operational directives."""
    few_shots = get_dialogue_few_shots().get("templates", {})
    text_lower = scenario_text.lower()

    # Debt collection scenario
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

    if primary == "LEGALISM":
        tmpl = few_shots.get("material_delay", {})
        return {
            "position_analysis": tmpl.get(
                "position_analysis",
                "Vụ việc này Nhà cung cấp đang vi phạm cam kết tiến độ hợp đồng. Nếu nể hờn xử lý bằng tình cảm, công trình sẽ bị sụp dây chuyền và dự án chịu phạt tiến độ nặng. Phải lập tức siết kỷ luật pháp lý, dùng điều khoản phạt làm đòn bẩy buộc đối tác dồn lực giao bù trong 24h-48h."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Thiết lập Vị thế & Căn cứ Hợp đồng ('Hình Danh Tương Phù')",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_1_anchor",
                    '"Anh [Tên Giám Đốc/Đại Diện NCC], theo Hợp đồng [Số HĐ] và Biên bản chốt tiến độ tuần trước, vật tư phải có mặt tại công trình Nhà Bè muộn nhất 17h00 hôm qua. Việc bên anh giao trễ đã làm ngưng trệ 100% tổ đội công nhân và máy móc hiện trường. Bên em làm việc đúng theo căn cứ hợp đồng (\'Hình Danh Tương Phù\'), không chấp nhận các lý do khách quan không có xác nhận văn bản."'
                )
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Ấn định Thời hạn & Chế tài Ràng buộc (Chế Tài Nhị Bỉnh)",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_2_deadline_consequence",
                    '"Em yêu cầu bên anh dồn ngay xe hàng giao đủ 100% khối lượng về công trình trước 12h00 trưa mai. Sau mốc này, Ban Quản lý Dự án sẽ lập Biên bản Vi phạm Đơn phương, bắt đầu tính phạt 0.5%/ngày và treo toàn bộ đợt thanh toán Kỳ 2 để cấn trừ chi phí thiệt hại dừng thi công."'
                )
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Mở Đường lui & Kích hoạt Phương án Dự phòng (Plan B)",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_3_way_out_plan_b",
                    '"Nếu bên anh tập trung xử lý giao đủ trước 17h00 chiều mai và có cam kết tiến độ đợt sau, em sẽ bảo lãnh với Chủ tịch không tính phạt vi phạm đợt này. Nhưng nếu trưa mai hàng không tới, em buộc phải cho kích hoạt Đơn vị dự phòng (Plan B) nhập hàng thế chỗ và trừ thẳng chi phí chênh lệch vào tài khoản bên anh."'
                )
            },
            "draft_official_communication": tmpl.get(
                "ready_to_send_text",
                "CÔNG VĂN YÊU CẦU GIAO BÙ VẬT TƯ & THÔNG BÁO CHẾ TÀI HỢP ĐỒNG\n---------------------------------------------------------------\nKính gửi Ban Giám đốc [Tên Nhà Cung Cấp],\n\nCăn cứ Hợp đồng số [Số HĐ/2026] và Biên bản giao nhận tiến độ hiện trường.\nBan Quản lý Dự án chính thức thông báo:\n1. Ghi nhận vi phạm chậm giao vật tư [Tên vật tư] làm ngưng trệ thi công hiện trường.\n2. Yêu cầu Quý công ty hoàn thành giao bù 100% khối lượng trước 12h00 ngày [DD/MM/YYYY].\n3. Quá thời hạn trên, chúng tôi sẽ áp dụng điều khoản phạt chậm tiến độ 0.5%/ngày và giữ thanh toán Đợt 2 để bảo đảm thiệt hại.\n\nRất mong sự hợp tác khẩn trương của Quý công ty.\n[Ban Quản Lý Dự Án BusinessOS]"
            ),
            "financial_and_operational_directives": [
                "💰 TẠM TẮT GIẢI NGÂN: Tạm giữ lại 10% - 20% giá trị thanh toán đợt tiếp theo theo Điều 2 Quy chế QC-OPS-01/2026.",
                "⚖️ CHẾ TÀI PHẠT VI PHẠM: Áp dụng phạt 0.5%/ngày chậm trễ tính từ 17h00 ngày hôm qua.",
                "🚀 KÍCH HOẠT PLAN B: Chuyển 100% khối lượng còn lại cho Đơn vị Cung cấp Dự phòng B và cấn trừ tiền chênh lệch vào tài khoản bên vi phạm."
            ],
            "action_principles": [
                "Đối chiếu cam kết thực tế theo nguyên tắc Hình Danh Tương Phù.",
                "Áp dụng Nhị Bỉnh (Thưởng - Phạt minh bạch), không dung dưỡng vi phạm.",
                "Kích hoạt song song Plan B dự phòng để đảm bảo tiến độ tuyệt đối."
            ]
        }
    elif primary == "RHETORIC":
        tmpl = few_shots.get("price_objection", {})
        return {
            "position_analysis": tmpl.get(
                "position_analysis",
                "Khách hàng đang dùng bài 'chê giá cao' để ép chiết khấu. Nếu vội vàng giảm giá, ta tự hạ thấp giá trị giải pháp và đưa dự án vào thế 'làm ráng lấy volume'. Phải lập tức bóc tách khung đối thoại: Chuyển tâm trí khách từ 'Chi phí đầu tư ban đầu' sang 'Dòng tiền và Tiết kiệm chi phí vận hành 3 năm'."
            ),
            "step_1_anchor": {
                "title": "Bước 1: Bẻ gãy Khung Chi phí & Chuyển đổi sang Dòng tiền (Reframing)",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_1_anchor",
                    '"Em rất hiểu Anh/Chị luôn đặt tiêu chí tối ưu ngân sách lên hàng đầu. Nhưng nếu so sánh báo giá bên em với các đơn vị giá rẻ trên thị trường, giống như so sánh một hệ thống tự động dài hạn với giải pháp chắp vá tạm thời. Giá trị thực sự không nằm ở \'số tiền chi ra hôm nay\', mà nằm ở \'dòng tiền và chi phí vận hành 3 năm tới\'."'
                )
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Bóc tách Rủi ro & Đưa ra Phản đề (Consequence Probe)",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_2_deadline_consequence",
                    '"Nếu chọn phương án rẻ hơn 15%, Anh/Chị tiết kiệm được ngay đợt 1, nhưng rủi ro gián đoạn hệ thống và chi phí khắc phục sự cố sau 6 tháng sẽ cao gấp 3 lần số tiền tiết kiệm đó. Anh/chị có sẵn sàng đánh đổi sự ổn định của toàn bộ hoạt động kinh doanh chỉ vì mức chênh lệch ban đầu này không?"'
                )
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Cam kết Giá trị & Chốt Thoả thuận (Closing Commitment)",
                "verbatim": tmpl.get("direct_dialogue", {}).get(
                    "step_3_way_out_plan_b",
                    '"Để Anh/chị hoàn toàn yên tâm, bên em cam kết bảo hành hiệu năng 100% bằng văn bản. Nếu Anh/Chị duyệt hợp đồng trong tuần này, em xin tặng thêm Gói Bảo trì Chuyên sâu 12 tháng trị giá [X triệu]. Em gửi bản Hợp đồng cập nhật để Anh/Chị chốt luôn nhé."'
                )
            },
            "draft_official_communication": tmpl.get(
                "ready_to_send_text",
                "TƯ VẤN THAM MƯU GỬI KHÁCH HÀNG / ĐỐI TÁC\n---------------------------------------\nChào Anh/Chị [Tên Khách Hàng],\n\nEm đã xem xét kỹ mối quan tâm của Anh/Chị về ngân sách đầu tư.\nBên em không cạnh tranh bằng giá thấp nhất, mà cam kết hiệu quả dòng tiền và độ ổn định cao nhất cho hệ thống của Anh/Chị.\n\nEm xin gửi Bảng Phân Tích Tổng Chi Phí Sở Hữu (TCO 3 Năm) để Anh/Chị thấy rõ khoản tiết kiệm vận hành dài hạn [X triệu].\nChiều nay 15h00 em xin phép gọi điện hỗ trợ Anh/Chị chốt phương án tốt nhất nhé!\n\n[Tên Quản Lý Kinh Doanh BusinessOS]"
            ),
            "financial_and_operational_directives": [
                "💰 GIỮ KHUNG GIÁ NGUYÊN BẢN: Giữ nguyên đơn giá báo giá chuẩn, không tự ý chiết khấu quá 3% ngân sách.",
                "📊 TỐI ƯU DÒNG TIỀN: Cấu trúc lộ trình thanh toán linh hoạt làm 4 đợt (30% - 30% - 30% - 10%) để giảm áp lực vốn ban đầu cho khách.",
                "🎁 GÓI GIA TĂNG GIÁ TRỊ: Tặng Gói Bảo trì Chuyên sâu 12 tháng thay vì giảm trừ tiền mặt."
            ],
            "action_principles": [
                "Rút củi đáy nồi: Thay đổi khung đối thoại từ Chi phí sang Dòng tiền.",
                "Bóc tách bản chất từ chối: Khách chưa thấy giá trị tương xứng.",
                "Chốt hạ cam kết bằng gói gia tăng giá trị dài hạn."
            ]
        }
    elif primary == "XUNZI":
        return {
            "position_analysis": "Vi phạm quy trình hiện tại xuất phát từ thói quen thiếu rèn nắn tiêu chuẩn. Cần áp dụng thuyết Tính Ác: Dùng kỷ luật quy chuẩn để uốn nắn hành vi nhân sự, kết hợp với lộ trình Khuyên Học để đào tạo nâng chuẩn.",
            "step_1_anchor": {
                "title": "Bước 1: Chuẩn hóa Quy chuẩn & Xác lập Khung Tiêu chuẩn (Khuyên Học)",
                "verbatim": '"Mọi vị trí trong tổ chức đều phải tuân thủ đúng Quy chế Vận hành đã ban hành. Việc phát sinh sai sót/vi phạm hiện tại phản ánh khoảng hống về năng lực và kỷ luật quy trình. Chúng ta cần rèn nắn lại tiêu chuẩn ngay lập tức."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Đưa ra Lộ trình Huấn luyện & Đánh giá (Assessment)",
                "verbatim": '"Yêu cầu toàn bộ nhân sự liên quan tham gia đợt Sát hạch Quy trình và Kỷ luật làm việc trong vòng 3 ngày tới. Nhân sự nào không đạt tiêu chuẩn sẽ bị tái bố trí công việc."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Động viên & Tạo Cơ hội Cải thiện (Rehabilitation)",
                "verbatim": '"Tổ chức luôn mở đường cho những nhân sự cam kết học tập và sửa đổi. Khi vượt qua bài kiểm tra tiêu chuẩn, các bạn sẽ được công nhận và trao lại đúng quyền hạn."'
            },
            "draft_official_communication": (
                "THÔNG BÁO VỀ VIỆC CHUẨN HÓA QUY TRÌNH & KỶ LUẬT THI CÔNG\n"
                "--------------------------------------------------------\n"
                "Kính gửi: Toàn thể Cán bộ Nhân viên / Đội ngũ Hiện trường\n\n"
                "Căn cứ Quy chế Kỷ luật và Tiêu chuẩn Vận hành BusinessOS.\n"
                "Ban Quản lý yêu cầu:\n"
                "1. Nghiêm túc tuân thủ 100% quy trình báo cáo và thi công theo tiêu chuẩn.\n"
                "2. Tổ chức đợt huấn luyện & kiểm tra quy chuẩn vào [Ngày/Giờ].\n"
                "3. Mọi hành vi vi phạm quy chuẩn sẽ bị xử lý nghiêm theo quy định.\n\n"
                "Ban Quản lý Dự án BusinessOS"
            ),
            "financial_and_operational_directives": [
                "💰 CHÍNH SÁCH THƯỞNG PHẠT QUY TRÌNH: Trừ 5% quỹ thưởng tháng đối với đơn vị vi phạm quy chuẩn báo cáo.",
                "📋 SÁT HẠCH TIÊU CHUẨN: Tổ chức sát hạch bắt buộc trong 72 giờ đối với 100% nhân sự hiện trường.",
                "🔄 TÁI BỐ TRÍ TỰ ĐỘNG: Chuyển giao các nhân sự không đạt sát hạch sang bộ phận hỗ trợ."
            ],
            "action_principles": [
                "Áp dụng thuyết Tính Ác: Rèn nắn hành vi qua kỷ luật và học tập.",
                "Đưa ra lộ trình Khuyên Học và kiểm tra quy chuẩn.",
                "Chuẩn hóa tiêu chuẩn làm việc trước khi giao quyền."
            ]
        }
    else:
        return {
            "position_analysis": "Cần bình tĩnh đánh giá sự cố trên tinh thần trung thực và tôn trọng sự thật khách quan. Không xử lý hấp vội mà cần bóc tách đúng nguyên nhân cốt lõi.",
            "step_1_anchor": {
                "title": "Bước 1: Thiết lập Vị thế & Nhận diện Mâu thuẫn",
                "verbatim": '"Chúng ta cần đối diện trực tiếp với bản chất sự cố trên tinh thần trung thực và tôn trọng sự thật."'
            },
            "step_2_deadline_consequence": {
                "title": "Bước 2: Xác lập Thời hạn & Trách nhiệm Cụ thể",
                "verbatim": '"Yêu cầu hoàn thành việc khắc phục sự cố đúng thời hạn và có báo cáo nguyên nhân minh bạch."'
            },
            "step_3_way_out_plan_b": {
                "title": "Bước 3: Thỏa thuận Phương án Khắc phục & Đồng hành",
                "verbatim": '"Tổ chức sẽ đồng hành và tạo điều kiện tối đa nếu các bên thể hiện sự thiện chí và tinh thần trách nhiệm."'
            },
            "draft_official_communication": (
                "THÔNG BÁO CHỈ ĐẠO XỬ LÝ SỰ CỐ & THỎA THUẬN GIẢI PHÁP\n"
                "---------------------------------------------------\n"
                "Kính gửi: Các Bộ phận / Đơn vị Liên quan\n\n"
                "Đề nghị các bên nghiêm túc phối hợp xử lý sự cố theo đúng chỉ đạo và báo cáo kết quả trước [HH:MM ngày DD/MM/YYYY].\n\n"
                "Ban Điều Hành BusinessOS"
            ),
            "financial_and_operational_directives": [
                "💰 BẢO ĐẢM TÀI CHÍNH: Tạm dừng các khoản chi phi chính thức ngoài dự toán.",
                "📋 BÓC TÁCH NGUYÊN NHÂN: Lập biên bản kiểm toán tài chính và tiến độ hiện trường.",
                "🤝 ĐỒNG HÀNH KHẮC PHỤC: Hỗ trợ nguồn lực kỹ thuật cho bộ phận vướng mắc."
            ],
            "action_principles": [
                "Đối diện sự thật và xác lập trách nhiệm minh bạch.",
                "Đưa ra thời hạn và yêu cầu cam kết cụ thể.",
                "Duy trì tinh thần hợp tác xây dựng."
            ]
        }


def process_nhan_thuat_analysis(scenario_text: str, scenario_type_hint: str = "general") -> Dict[str, Any]:
    orchestrator = get_orchestrator()
    text_lower = scenario_text.lower()

    # 0. Context Ambiguity Check
    is_ambiguous, warning_msg = check_context_ambiguity(scenario_text)

    # 1. Determine scenario type
    ops_keywords = ["vật tư", "nhà cung cấp", "chậm tiến độ", "công trình", "thi công", "hợp đồng", "chế tài", "vi phạm hợp đồng", "trách nhiệm", "nợ", "đòi nợ", "thanh toán"]
    if any(w in text_lower for w in ops_keywords):
        scenario_type = "governance"
    elif any(w in text_lower for w in ["báo cáo láo", "dối trá", "kỷ luật", "vi phạm", "đình công", "quy chế"]):
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

    # 3b. Match Custom RAG Company Documents / SOPs / Contracts
    custom_rag_docs = orchestrator.knowledge_engine.query_custom_documents(scenario_text, top_k=2)

    primary = router_res.get("primary_philosophy", "NONE").upper()
    secondary = router_res.get("secondary_philosophy")
    tertiary = router_res.get("tertiary_philosophy")

    # 4. Generate Detailed Actionable Script & Communication Drafts & Directives
    script_details = generate_actionable_script_details(primary, scenario_text)

    correlation_id = f"CORR-WEB-{uuid.uuid4().hex[:8].upper()}"

    return {
        "status": "success",
        "scenario_text": scenario_text,
        "is_ambiguous": is_ambiguous,
        "ambiguity_warning": warning_msg if is_ambiguous else "",
        "philosophy_routing": {
            "primary_philosophy": primary,
            "secondary_philosophy": secondary.upper() if secondary else None,
            "tertiary_philosophy": tertiary.upper() if tertiary else None,
            "lens_weights": router_res.get("lens_weights", {}),
            "lens_confidence_scores": router_res.get("lens_confidence_scores", {}),
            "explanation": router_res.get("explanation", ""),
        },
        "matched_knowledge_units": [
            {
                "unit_id": u.unit_id,
                "unit_type": u.unit_type,
                "title": u.title,
                "domain": u.domain,
                "checksum": u.checksum,
                "summary": str(u.raw_data.get("summary", u.title)),
            }
            for u in matched_units
        ],
        "matched_custom_docs": [
            {
                "doc_id": d.doc_id,
                "title": d.title,
                "file_path": d.file_path,
                "checksum": d.checksum,
                "snippet": d.content[:200] + "...",
            }
            for d in custom_rag_docs
        ],
        "action_script": {
            "primary_lens": primary,
            "execution_config": {
                "temperature": 0.1,
                "reproducibility_seed": 42,
            },
            "position_analysis": script_details["position_analysis"],
            "step_1_anchor": script_details["step_1_anchor"],
            "step_2_deadline_consequence": script_details["step_2_deadline_consequence"],
            "step_3_way_out_plan_b": script_details["step_3_way_out_plan_b"],
            "draft_official_communication": script_details["draft_official_communication"],
            "financial_and_operational_directives": script_details["financial_and_operational_directives"],
            "action_principles_summary": script_details["action_principles"],
        },
        "correlation_id": correlation_id,
    }
