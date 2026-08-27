"""
Department Solution Packs for NhanThuat (HR-OS, Ops-OS, SalesOS).
Provides standardized executive frameworks, assessment rubrics, and incident directive templates.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DepartmentPack:
    domain_id: str
    name: str
    description: str
    philosophy_primary: str
    philosophy_secondary: str
    core_laws: list[str]
    core_principles: list[str]
    core_anti_patterns: list[str]
    assessment_rubrics: list[dict[str, Any]] = field(default_factory=list)
    action_templates: dict[str, str] = field(default_factory=dict)


class DepartmentPackRegistry:
    """Registry of specialized Department Solution Packs."""

    def __init__(self) -> None:
        self._packs: dict[str, DepartmentPack] = {}
        self._register_default_packs()

    def _register_default_packs(self) -> None:
        # 1. HR-OS Pack (Human Resources, Leadership, Culture, Discipline)
        self._packs["HR"] = DepartmentPack(
            domain_id="HR",
            name="HR-OS: Quản Trị Nhân Sự & Dụng Nhân Thực Chiến",
            description="Khung giải pháp xử lý khủng hoảng nhân sự, tranh chấp kỷ luật, chọn và đặt tướng, rèn nắn tiêu chuẩn vận hành.",
            philosophy_primary="XUNZI",
            philosophy_secondary="CONFUCIAN",
            core_laws=["NT-LAW-0034", "NT-LAW-0035", "NT-LAW-0038"],
            core_principles=["NT-PRINCIPLE-0061", "NT-PRINCIPLE-0065"],
            core_anti_patterns=["NT-ANTI-PATTERN-0010", "NT-ANTI-PATTERN-0014"],
            assessment_rubrics=[
                {"criterion": "Độ tương thích Vai trò (Person-Role Fit)", "weight": 0.35, "standard": "Không đòi hỏi nhân sự thay đổi tính cách; tái cấu trúc ranh giới công việc trước."},
                {"criterion": "Kỷ luật Quy chuẩn (Lễ Định Phần)", "weight": 0.35, "standard": "Mọi quyền hạn phải đi kèm trách nhiệm và bài sát hạch tiêu chuẩn."},
                {"criterion": "Kênh Đối thoại & Động viên (Đức Trị)", "weight": 0.30, "standard": "Duy trì con đường cải thiện và trao lại vị thế khi nhân sự đạt chuẩn."},
            ],
            action_templates={
                "labor_dispute": "QUY TRÌNH 3 BƯỚC XỬ LÝ TRANH CHẤP LAO ĐỘNG: 1. Chốt biên bản hiện trạng -> 2. Ấn định thời hạn 24h trở lại vị trí -> 3. Thưởng tiến độ cho nhóm tuân thủ.",
                "onboarding_mentorship": "LỘ TRÌNH KHUYÊN HỌC 14 NGÀY: Sát hạch quy chuẩn làm việc trước khi phân quyền chính thức.",
            }
        )

        # 2. Ops-OS Pack (Operations, Construction, Logistics, Supply Chain)
        self._packs["OPS"] = DepartmentPack(
            domain_id="OPS",
            name="Ops-OS: Điều Hành Hiện Trường & Kiểm Soát Tiến Độ",
            description="Khung giải pháp siết kỷ luật công trường, xử lý nhà cung cấp chậm vật tư, chế tài hợp đồng và bảo đảm tiến độ tuyệt đối.",
            philosophy_primary="LEGALISM",
            philosophy_secondary="TAOISM",
            core_laws=["NT-LAW-0005", "NT-LAW-0068", "NT-LAW-0069"],
            core_principles=["NT-PRINCIPLE-0064", "NT-PRINCIPLE-0086"],
            core_anti_patterns=["NT-ANTI-PATTERN-0001", "NT-ANTI-PATTERN-0015"],
            assessment_rubrics=[
                {"criterion": "Hình Danh Tham Đồng (Cam kết vs Thực tế)", "weight": 0.40, "standard": "Đối chiếu 100% biên bản tiến độ với hợp đồng đã ký kết."},
                {"criterion": "Chế tài Nhị Bỉnh (Thưởng / Phạt minh bạch)", "weight": 0.35, "standard": "Áp dụng phạt chậm tiến độ 0.5%/ngày và cấn trừ thanh toán khi vi phạm."},
                {"criterion": "Kế hoạch Dự phòng (Plan B Readiness)", "weight": 0.25, "standard": "Luôn kích hoạt song song đơn vị cung ứng dự phòng khi trễ quá 24h."},
            ],
            action_templates={
                "material_delay": "CÔNG VĂN THÔNG BÁO CHẾ TÀI VẬT TƯ: 1. Ghi nhận vi phạm chậm trễ -> 2. Hạn chót giao bù 12h00 -> 3. Kích hoạt Plan B và giữ thanh toán đợt 2.",
                "site_inspection": "BIÊN BẢN KIỂM SOÁT AN TOÀN & ĐỊNH MỨC: Lập hồ sơ kiểm toán hiện trường định kỳ 48h.",
            }
        )

        # 3. SalesOS Pack (Commercial, Enterprise Negotiation, B2B Pricing)
        self._packs["SALES"] = DepartmentPack(
            domain_id="SALES",
            name="SalesOS: Đàm Phán Thương Mại & Đối Ứng Từ Chối",
            description="Khung chiến lược đàm phán hợp đồng lớn, bẻ gãy luận điểm chê giá cao, định khung giá trị TCO 3 năm và chốt thỏa thuận.",
            philosophy_primary="RHETORIC",
            philosophy_secondary="SUNZI",
            core_laws=["NT-LAW-0054", "NT-LAW-0055", "NT-LAW-0058"],
            core_principles=["NT-PRINCIPLE-0086", "NT-PRINCIPLE-0087"],
            core_anti_patterns=["NT-ANTI-PATTERN-0012", "NT-ANTI-PATTERN-0018"],
            assessment_rubrics=[
                {"criterion": "Định Khung Giá Trị (Value Framing)", "weight": 0.40, "standard": "Chuyển tâm trí khách từ chi phí đầu tư ban đầu sang tổng chi phí sở hữu TCO 3 năm."},
                {"criterion": "Bảo Toàn Biên Lợi Nhuận (Concession Discipline)", "weight": 0.30, "standard": "Không chiết khấu quá 3% tiền mặt; ưu tiên tặng gói bảo trì gia tăng giá trị."},
                {"criterion": "Cam Kết Hiệu Năng & Chốt Thỏa Thuận (Closing Power)", "weight": 0.30, "standard": "Bảo hành 100% bằng văn bản và ấn định thời hạn chiết khấu hợp đồng."},
            ],
            action_templates={
                "price_objection": "KỊCH BẢN ĐỐI ỨNG CHÊ GIÁ ĐẮT: 1. Bẻ gãy khung chi phí -> 2. Đưa ra phản đề rủi ro gián đoạn giá rẻ -> 3. Chốt gói bảo trì 12 tháng.",
                "commercial_brief": "BẢN PHÂN TÍCH TỔNG CHI PHÍ TCO: Minh chứng khoản tiết kiệm vận hành dài hạn cho ban giám đốc đối tác.",
            }
        )

    def get_pack(self, domain: str) -> DepartmentPack | None:
        """Get Department Solution Pack by domain slug or ID."""
        key = domain.upper().strip()
        if "HR" in key or "NHAN_SU" in key:
            return self._packs.get("HR")
        if "OPS" in key or "CONG_TRINH" in key or "VAN_HANH" in key:
            return self._packs.get("OPS")
        if "SALE" in key or "THUONG_MAI" in key or "DAM_PHAN" in key:
            return self._packs.get("SALES")
        return self._packs.get(key)

    def list_packs(self) -> list[DepartmentPack]:
        """Return list of all registered department packs."""
        return list(self._packs.values())

    def evaluate_scenario(self, domain: str, scenario_text: str) -> dict[str, Any]:
        """Evaluate an operational scenario against the department's assessment rubric."""
        pack = self.get_pack(domain)
        if not pack:
            return {"status": "error", "message": f"Department pack for domain '{domain}' not found."}

        return {
            "status": "success",
            "domain": pack.domain_id,
            "pack_name": pack.name,
            "primary_lens": pack.philosophy_primary,
            "rubrics": pack.assessment_rubrics,
            "recommended_template": list(pack.action_templates.values())[0] if pack.action_templates else "",
            "recommended_units": pack.core_laws + pack.core_principles,
        }
