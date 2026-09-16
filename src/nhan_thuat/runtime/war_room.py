"""
War Room Sandbox Runtime Engine (Sa Bàn Tình Thế Đa Tác Nhân)
Module: nhan_thuat.runtime.war_room

Implements multi-agent social and political organizational simulation based on
Nhan Thuat 379 Knowledge Units and 5 Strategic Schools (Confucianism, Legalism, Taoism, Xunzi, Rhetoric).
Provides multi-round progression, God-mode intervention, and Strategic War Room Synthesis.
"""

from __future__ import annotations

import json
import os
import random
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

import requests

from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.runtime.synthesizer import get_provider_configs

# Preset classic organizational dilemma scenarios
WAR_ROOM_PRESETS: list[dict[str, Any]] = [
    {
        "id": "scenario-layoffs",
        "title": "Cắt Giảm 30% Nhân Sự Toàn Công Ty",
        "category": "Tái Cấu Trúc & Khủng Hoảng",
        "badge": "Nguy cơ cao",
        "description": "Hội đồng Quản trị yêu cầu cắt giảm 30% định biên nhân sự trong 45 ngày để thu gọn chi phí sau 2 quý thua lỗ. Thông tin mật bắt đầu rò rỉ ra các trưởng phòng.",
        "icon": "⚡",
        "default_scenario": "Công ty cổ phần công nghệ - bán lẻ quy mô 450 nhân sự đang đối mặt với dòng tiền âm 2 quý liên tiếp. HĐQT chỉ thị Tổng Giám đốc phải tinh giản 30% biên chế các khối, ưu tiên cắt giảm nhân sự thâm niên lương cao kém hiệu quả trong vòng 45 ngày. Tin đồn rò rỉ khiến nội bộ hoang mang, các trưởng bộ phận bắt đầu hình thành liên minh tự vệ.",
    },
    {
        "id": "scenario-sales-leak",
        "title": "Nghi Vấn Giám Đốc Kinh Doanh Bán Tệp Khách Sang Đối Thủ",
        "category": "Chống Phản Bội & Gián Điệp",
        "badge": "Khẩn cấp",
        "description": "Giám đốc Kinh doanh chủ lực phụ trách 65% doanh số có dấu hiệu đàm phán với đối thủ truyền kiếp và chuẩn bị lôi kéo 5 nhân viên kinh doanh giỏi nhất cùng tệp khách hàng VIP ra đi.",
        "icon": "🕵️",
        "default_scenario": "Giám đốc Kinh doanh thâm niên 5 năm, người nắm giữ quan hệ với các khách hàng VIP chiếm 65% doanh số toàn công ty, vừa bị bộ phận IT và An ninh nội bộ phát hiện tải trọn bộ database CRM ra ổ cứng cá nhân. Cùng lúc, đối thủ cạnh tranh trực tiếp vừa thông báo sắp thành lập chi nhánh mới do một 'nhân vật giấu tên' đứng đầu.",
    },
    {
        "id": "scenario-audit-fraud",
        "title": "Kiểm Toán Nội Bộ Phát Hiện Chênh Lệch Quỹ Mua Hàng",
        "category": "Pháp Trị & Trừng Phạt",
        "badge": "Nhạy cảm",
        "description": "Ban kiểm soát phát hiện thất thoát và chênh lệch 12 tỷ đồng tiền hoa hồng ngầm tại Ban Cung ứng & Mua hàng, liên quan mật thiết đến người nhà của một Cổ đông sáng lập.",
        "icon": "⚖️",
        "default_scenario": "Báo cáo kiểm toán nội bộ mật vừa trình lên bàn Chủ tịch: Trưởng ban Cung ứng (em họ một cổ đông sáng lập nắm 20% vốn) đã cấu kết với nhà cung cấp vật tư suốt 3 năm, nâng khống giá thành và rút ruột ước tính 12 tỷ đồng. Nếu xử lý hình sự, công ty đối mặt nguy cơ vỡ nợ chuỗi cung ứng và rạn nứt nội bộ cổ đông.",
    },
    {
        "id": "scenario-power-struggle",
        "title": "Xung Đột Quyền Lực: CTO Công Thần vs Phó TGĐ Mới",
        "category": "Tranh Chấp Quyền Bính",
        "badge": "Căng thẳng",
        "description": "Phó Tổng Giám đốc Vận hành mới được tuyển dụng về với mức lương cao đang tìm cách tước quyền phê duyệt nhân sự và ngân sách của Giám đốc Công nghệ kỳ cựu sáng lập công ty.",
        "icon": "⚔️",
        "default_scenario": "Tổng Giám đốc tuyển một Phó Tổng Giám đốc Vận hành từ tập đoàn đa quốc gia về với kỳ vọng thiết lập lại kỷ cương. Ngay trong tháng đầu tiên, Phó TGĐ đã từ chối phê duyệt tăng lương cho nhóm kỹ sư cốt cán của Giám đốc Công nghệ (CTO - co-founder 7 năm). Hai bên công khai khẩu chiến tại cuộc họp giao ban, đẩy toàn bộ đội ngũ kỹ thuật vào trạng thái chuẩn bị nộp đơn nghỉ việc tập thể.",
    },
]


@dataclass
class Persona:
    id: str
    name: str
    role: str
    faction: str
    core_interest: str
    hidden_fear: str
    stance: str
    loyalty_score: int = 70  # 0 - 100
    stress_level: int = 40   # 0 - 100
    influence_score: int = 60 # 0 - 100
    avatar: str = "👤"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PersonaAction:
    persona_id: str
    persona_name: str
    role: str
    avatar: str
    public_action: str
    private_thought: str
    whisper_target: str = ""
    whisper_content: str = ""
    stance_shift: str = ""
    loyalty_change: int = 0
    stress_change: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoundResult:
    round_number: int
    stage_name: str
    round_summary: str
    intervention: str | None = None
    actions: list[PersonaAction] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "round_number": self.round_number,
            "stage_name": self.stage_name,
            "round_summary": self.round_summary,
            "intervention": self.intervention,
            "actions": [a.to_dict() for a in self.actions],
        }


@dataclass
class WarRoomSession:
    session_id: str
    scenario: str
    current_round: int = 0
    max_rounds: int = 3
    status: str = "INITIALIZED"  # INITIALIZED, RUNNING, COMPLETED
    personas: list[Persona] = field(default_factory=list)
    rounds: list[RoundResult] = field(default_factory=list)
    interventions: list[dict[str, Any]] = field(default_factory=list)
    report: dict[str, Any] | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    relevant_units: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "scenario": self.scenario,
            "current_round": self.current_round,
            "max_rounds": self.max_rounds,
            "status": self.status,
            "personas": [p.to_dict() for p in self.personas],
            "rounds": [r.to_dict() for r in self.rounds],
            "interventions": self.interventions,
            "report": self.report,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "relevant_units": self.relevant_units,
        }


class WarRoomEngine:
    """Core stateful engine managing multi-agent organizational war room simulations."""

    def __init__(self, knowledge_engine: KnowledgeEngine | None = None) -> None:
        self.knowledge_engine = knowledge_engine or KnowledgeEngine()
        self._sessions: dict[str, WarRoomSession] = {}

    def get_presets(self) -> list[dict[str, Any]]:
        return WAR_ROOM_PRESETS

    def get_session(self, session_id: str) -> WarRoomSession | None:
        return self._sessions.get(session_id)

    def _find_relevant_knowledge(self, scenario: str, top_k: int = 4) -> list[dict[str, Any]]:
        """Retrieve top relevant knowledge units matching scenario theme."""
        results = []
        try:
            from nhan_thuat.rag.hybrid_retriever import HybridRetriever
            units_list = list(self.knowledge_engine.units_by_id.values())
            retriever = HybridRetriever(units=units_list)
            res = retriever.retrieve(scenario, top_k=top_k, expand_relations=True)
            matched_units = res.primary_units[:top_k] if res.primary_units else units_list[:top_k]
            for u in matched_units:
                results.append({
                    "id": getattr(u, "unit_id", getattr(u, "id", "")),
                    "title": getattr(u, "title", ""),
                    "domain": getattr(u, "domain", getattr(u, "primary_domain", "HUMAN_NATURE")),
                    "summary": getattr(u, "summary", "") or getattr(u, "claim", ""),
                })
        except Exception:
            # Safe deterministic units
            sample_units = list(self.knowledge_engine.units_by_id.values())[:top_k]
            for u in sample_units:
                results.append({
                    "id": getattr(u, "unit_id", getattr(u, "id", "")),
                    "title": getattr(u, "title", ""),
                    "domain": getattr(u, "domain", getattr(u, "primary_domain", "HUMAN_NATURE")),
                    "summary": getattr(u, "summary", ""),
                })
        return results

    def _call_llm_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        """Call configured LLM (DeepSeek / Gemini / OpenAI) and parse JSON response."""
        configs = get_provider_configs()
        if not configs:
            return None

        for cfg in configs:
            try:
                base_url = cfg["base_url"].rstrip("/")
                endpoint = f"{base_url}/chat/completions"
                headers = {
                    "Authorization": f"Bearer {cfg['api_key']}",
                    "Content-Type": "application/json",
                }
                body = {
                    "model": cfg["model"],
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"} if "deepseek" in cfg["model"].lower() or "gemini" in cfg["model"].lower() or "gpt" in cfg["model"].lower() else None,
                }
                resp = requests.post(endpoint, headers=headers, json=body, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    # Extract JSON payload
                    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
                    raw_json = match.group(1) if match else content
                    raw_json = raw_json.strip()
                    # Try to parse
                    return json.loads(raw_json)
            except Exception:
                continue
        return None

    def initialize_session(self, scenario: str, custom_personas: list[dict[str, Any]] | None = None) -> WarRoomSession:
        """Seed scenario and generate 4-6 deep psychological personas."""
        scenario_text = scenario.strip()
        if not scenario_text:
            scenario_text = WAR_ROOM_PRESETS[0]["default_scenario"]

        session_id = f"WAR-ROOM-{uuid.uuid4().hex[:8].upper()}"
        relevant_units = self._find_relevant_knowledge(scenario_text)

        personas: list[Persona] = []

        if custom_personas and len(custom_personas) >= 3:
            for i, p_data in enumerate(custom_personas):
                personas.append(Persona(
                    id=p_data.get("id", f"p_{i+1}"),
                    name=p_data.get("name", f"Nhân Vật {i+1}"),
                    role=p_data.get("role", "Quản Lý"),
                    faction=p_data.get("faction", "Trung lập"),
                    core_interest=p_data.get("core_interest", "Bảo toàn vị thế"),
                    hidden_fear=p_data.get("hidden_fear", "Mất quyền lực"),
                    stance=p_data.get("stance", "Thận trọng"),
                    loyalty_score=int(p_data.get("loyalty_score", 70)),
                    stress_level=int(p_data.get("stress_level", 40)),
                    influence_score=int(p_data.get("influence_score", 60)),
                    avatar=p_data.get("avatar", "👤"),
                ))
        else:
            # Try LLM generation
            llm_personas = self._generate_personas_llm(scenario_text, relevant_units)
            if llm_personas:
                personas = llm_personas
            else:
                personas = self._generate_personas_deterministic(scenario_text)

        session = WarRoomSession(
            session_id=session_id,
            scenario=scenario_text,
            current_round=0,
            max_rounds=3,
            status="INITIALIZED",
            personas=personas,
            rounds=[],
            interventions=[],
            relevant_units=relevant_units,
        )
        self._sessions[session_id] = session
        return session

    def _generate_personas_llm(self, scenario: str, relevant_units: list[dict[str, Any]]) -> list[Persona] | None:
        """Call LLM to generate realistic personas."""
        system_prompt = (
            "Bạn là Chuyên gia Kiến trúc Nhân sự & Phân tích Động cơ Quyền lực cao cấp của hệ thống Nhân Thuật. "
            "Nhiệm vụ: Phân tích kịch bản tình thế và sinh ra đúng 4 hoặc 5 nhân vật chủ chốt trong tổ chức với các động cơ ngầm, "
            "nỗi sợ thầm kín và phe phái sắc nét. Trả về định dạng JSON thuần túy:\n"
            "{\n"
            '  "personas": [\n'
            '    {\n'
            '      "id": "p_1",\n'
            '      "name": "Tên người Việt",\n'
            '      "role": "Chức danh",\n'
            '      "faction": "Phe phái hoặc khối phòng ban",\n'
            '      "core_interest": "Lợi ích cốt lõi thiết thân",\n'
            '      "hidden_fear": "Nỗi sợ sâu kín nhất",\n'
            '      "stance": "Lập trường (ví dụ: Bảo thủ phòng vệ, Cấp tiến cơ hội, Phản kháng ngầm, Hoài nghi)",\n'
            '      "loyalty_score": 65,\n'
            '      "stress_level": 55,\n'
            '      "influence_score": 75,\n'
            '      "avatar": "👔"\n'
            '    }\n'
            '  ]\n'
            "}"
        )
        user_prompt = f"Bối cảnh tình thế:\n{scenario}\n\nTri thức tham chiếu: {json.dumps(relevant_units, ensure_ascii=False)}"
        data = self._call_llm_json(system_prompt, user_prompt)
        if data and isinstance(data.get("personas"), list) and len(data["personas"]) >= 3:
            res = []
            for i, p in enumerate(data["personas"]):
                res.append(Persona(
                    id=str(p.get("id", f"p_{i+1}")),
                    name=str(p.get("name", f"Nhân vật {i+1}")),
                    role=str(p.get("role", "Thành viên")),
                    faction=str(p.get("faction", "Nội bộ")),
                    core_interest=str(p.get("core_interest", "Bảo toàn quyền lợi")),
                    hidden_fear=str(p.get("hidden_fear", "Bị quy trách nhiệm")),
                    stance=str(p.get("stance", "Thận trọng")),
                    loyalty_score=int(p.get("loyalty_score", 65)),
                    stress_level=int(p.get("stress_level", 45)),
                    influence_score=int(p.get("influence_score", 60)),
                    avatar=str(p.get("avatar", "👤")),
                ))
            return res
        return None

    def _generate_personas_deterministic(self, scenario: str) -> list[Persona]:
        """High-depth deterministic persona generator matched to common corporate profiles."""
        scenario_lower = scenario.lower()

        if any(w in scenario_lower for w in ["cắt giảm", "nhân sự", "biên chế", "sa thải", "layoff"]):
            return [
                Persona(
                    id="p_1",
                    name="Trần Thế Dũng",
                    role="Giám Đốc Khối Vận Hành (COO)",
                    faction="Phe Cựu Trào / Sáng Lập",
                    core_interest="Bảo vệ đội ngũ thân tín và giữ nguyên định mức ngân sách vận hành",
                    hidden_fear="Bị xem là quản lý yếu kém khi hiệu suất sụt giảm",
                    stance="Phản kháng thụ động & Kéo dài thời gian",
                    loyalty_score=68,
                    stress_level=75,
                    influence_score=85,
                    avatar="👔",
                ),
                Persona(
                    id="p_2",
                    name="Lê Hoàng Yến",
                    role="Giám Đốc Nhân Sự (CHRO)",
                    faction="Ban Chấp Hành / Trung Gian",
                    core_interest="Hoàn thành chỉ tiêu cắt giảm nhưng không vướng rủi ro pháp lý lao động",
                    hidden_fear="Bị nhân viên tẩy chay và trở thành 'tội đồ' hứng búa rìu dư luận",
                    stance="Thận trọng & Nguyên tắc pháp lý",
                    loyalty_score=80,
                    stress_level=85,
                    influence_score=70,
                    avatar="👩‍💼",
                ),
                Persona(
                    id="p_3",
                    name="Nguyễn Khắc Minh",
                    role="Trưởng Phòng Kỹ Thuật Chủ Lực",
                    faction="Khối Chuyên Môn / Công Nghệ",
                    core_interest="Bảo toàn mức lương và các chế độ đãi ngộ cho dàn kỹ sư cứng",
                    hidden_fear="Dự án cốt lõi đổ vỡ do mất nhân sự chủ chốt, sẵn sàng nộp đơn nghỉ tập thể",
                    stance="Đối đầu trực diện nếu chạm vào quyền lợi",
                    loyalty_score=45,
                    stress_level=80,
                    influence_score=78,
                    avatar="💻",
                ),
                Persona(
                    id="p_4",
                    name="Vũ Đức Nam",
                    role="Giám Đốc Tài Chính (CFO)",
                    faction="Phái Kỷ Cương / HĐQT",
                    core_interest="Cắt giảm tức thì 30% chi phí cố định để cứu vãn dòng tiền quý tới",
                    hidden_fear="Dòng tiền âm chạm ngưỡng vỡ nợ ngắn hạn trước mắt ngân hàng",
                    stance="Cương quyết thực thi theo con số",
                    loyalty_score=88,
                    stress_level=60,
                    influence_score=82,
                    avatar="📊",
                ),
                Persona(
                    id="p_5",
                    name="Phạm Thanh Hà",
                    role="Trưởng Nhóm Kinh Doanh Ngôi Sao",
                    faction="Khối Tiền Tuyến / Cơ Hội",
                    core_interest="Tận dụng khủng hoảng để đòi chia lại hoa hồng và thăng chức vượt cấp",
                    hidden_fear="Bị xếp vào diện xem xét tinh giản và giảm chỉ tiêu",
                    stance="Quan sát cơ hội & Ngấm ngầm liên minh",
                    loyalty_score=50,
                    stress_level=65,
                    influence_score=62,
                    avatar="🎯",
                ),
            ]

        if any(w in scenario_lower for w in ["kinh doanh", "khách hàng", "bán", "gián điệp", "crm", "đối thủ"]):
            return [
                Persona(
                    id="p_1",
                    name="Vũ Mạnh Cường",
                    role="Giám Đốc Kinh Doanh (CCO)",
                    faction="Phe Độc Lập / Ngôi Sao Doanh Số",
                    core_interest="Tối đa hóa giá trị vị thế cá nhân, chuẩn bị đường lùi sang đối thủ",
                    hidden_fear="Bị phát hiện hành vi tuồn dữ liệu trước khi hoàn tất hợp đồng mới",
                    stance="Bề ngoài phục tùng - Ngấm ngầm phản phúc",
                    loyalty_score=30,
                    stress_level=70,
                    influence_score=90,
                    avatar="💼",
                ),
                Persona(
                    id="p_2",
                    name="Đỗ Phương Thảo",
                    role="Phó Ban Chăm Sóc Khách Hàng VIP",
                    faction="Trung Gian / Nằm Vùng",
                    core_interest="Được Giám đốc CCO cất nhắc nhưng sợ mất công việc ổn định",
                    hidden_fear="Bị kéo vào vụ bê bối pháp lý hoặc bị sa thải đột ngột",
                    stance="Lưỡng lự - Chờ bên nào thắng thế",
                    loyalty_score=55,
                    stress_level=80,
                    influence_score=60,
                    avatar="🗂️",
                ),
                Persona(
                    id="p_3",
                    name="Hoàng Bá Phúc",
                    role="Trưởng Ban An Ninh Nội Bộ & IT",
                    faction="Cận Thần Của Chủ Tịch",
                    core_interest="Thu thập đủ chứng cứ pháp lý xác thực để trừ khử mầm mống phản loạn",
                    hidden_fear="Hành động hấp tấp làm bứt dây động rừng khiến đối tượng xóa sạch dấu vết",
                    stance="Rình rập & Thu thập bằng chứng",
                    loyalty_score=95,
                    stress_level=50,
                    influence_score=65,
                    avatar="🛡️",
                ),
                Persona(
                    id="p_4",
                    name="Trần Đình Trọng",
                    role="Phó Tổng Giám Đốc Phụ Trách Thị Trường",
                    faction="Ban Điều Hành",
                    core_interest="Trám ngay lỗ hổng thị trường nếu CCO rũ áo ra đi",
                    hidden_fear="Doanh số quý này sập hầm kéo sập luôn uy tín điều hành của bản thân",
                    stance="Chuẩn bị phương án B & Giữ chân nhân viên kinh doanh",
                    loyalty_score=85,
                    stress_level=75,
                    influence_score=80,
                    avatar="📈",
                ),
            ]

        # Generic deep organizational matrix
        return [
            Persona(
                id="p_1",
                name="Nguyễn Văn Khang",
                role="Trưởng Ban Chiến Lược & Kế Hoạch",
                faction="Phe Kỹ Trị / Tham Mưu",
                core_interest="Duy trì ảnh hưởng cố vấn và kiểm soát quy trình ra quyết định",
                hidden_fear="Bị gạt ra rìa khỏi vòng thân cận quyền lực",
                stance="Phân tích duy lý & Thận trọng",
                loyalty_score=78,
                stress_level=55,
                influence_score=80,
                avatar="🏛️",
            ),
            Persona(
                id="p_2",
                name="Bùi Quốc Toàn",
                role="Giám Đốc Vận Hành Thực Địa",
                faction="Phe Công Thần / Khối Hiện Trường",
                core_interest="Quyền tự chủ ngân sách địa phương và bảo vệ đàn em",
                hidden_fear="Bị thanh tra siết chặt kiểm soát và cắt giảm hạn mức",
                stance="Kháng cự ngầm mọi chính sách mới",
                loyalty_score=60,
                stress_level=68,
                influence_score=75,
                avatar="🛠️",
            ),
            Persona(
                id="p_3",
                name="Lê Thùy Dung",
                role="Trưởng Ban Kiểm Soát Tuân Thủ",
                faction="Pháp Trị / HĐQT",
                core_interest="Thiết lập trật tự kỷ cương tuyệt đối không nhân nhượng",
                hidden_fear="Bị cô lập do quá cứng nhắc hoặc bị qua mặt",
                stance="Cứng rắn nguyên tắc",
                loyalty_score=90,
                stress_level=62,
                influence_score=68,
                avatar="⚖️",
            ),
            Persona(
                id="p_4",
                name="Tạ Minh Trí",
                role="Đại Diện Nhóm Quản Lý Trẻ Cấp Tiến",
                faction="Khối Đổi Mới / Cơ Hội",
                core_interest="Chớp thời cơ khủng hoảng để thế chân các vị trí kỳ cựu",
                hidden_fear="Bị nhóm cựu trào dập tắt từ trong trứng nước",
                stance="Cấp tiến & Tích cực thể hiện",
                loyalty_score=65,
                stress_level=50,
                influence_score=58,
                avatar="🚀",
            ),
        ]

    def step_round(self, session_id: str, intervention: str = "") -> RoundResult:
        """Run next simulation round factoring in user's God-mode intervention."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        if session.status == "COMPLETED":
            raise ValueError("Simulation has already completed all rounds.")

        next_round_num = session.current_round + 1
        intervention_clean = intervention.strip() if intervention else None

        if intervention_clean:
            session.interventions.append({
                "round": next_round_num,
                "text": intervention_clean,
                "timestamp": time.time(),
            })

        stage_titles = {
            1: "Vòng 1: Thăm Dò & Lan Truyền Tin Đồn (Information Leak & Probing)",
            2: "Vòng 2: Phân Hóa & Thiết Lập Liên Minh Ngầm (Factional Alignment & Secret Alliances)",
            3: "Vòng 3: Đỉnh Điểm Đụng Độ & Điểm Gãy Tổ Chức (Climax Confrontation & Breaking Points)",
            4: "Vòng 4: Tái Cân Bằng Hoặc Đột Phá Hậu Can Thiệp (Post-Intervention Realignment)",
        }
        stage_name = stage_titles.get(next_round_num, f"Vòng {next_round_num}: Biến Động Tiếp Diễn")

        # Try LLM round simulation
        round_result = self._step_round_llm(session, next_round_num, stage_name, intervention_clean)
        if not round_result:
            round_result = self._step_round_deterministic(session, next_round_num, stage_name, intervention_clean)

        # Apply state changes to personas
        action_map = {a.persona_id: a for a in round_result.actions}
        for p in session.personas:
            if p.id in action_map:
                act = action_map[p.id]
                p.loyalty_score = max(5, min(100, p.loyalty_score + act.loyalty_change))
                p.stress_level = max(5, min(100, p.stress_level + act.stress_change))
                if act.stance_shift:
                    p.stance = act.stance_shift

        session.rounds.append(round_result)
        session.current_round = next_round_num
        session.updated_at = time.time()

        if next_round_num >= session.max_rounds and not intervention_clean:
            session.status = "COMPLETED"
        else:
            session.status = "RUNNING"

        return round_result

    def _step_round_llm(self, session: WarRoomSession, round_num: int, stage_name: str, intervention: str | None) -> RoundResult | None:
        """Use LLM to generate nuanced conversational & political round dynamics."""
        system_prompt = (
            "Bạn là Engine Giả lập Tâm lý & Hành vi Sa bàn Chính trị Doanh nghiệp của Nhân Thuật. "
            "Mỗi nhân vật phải hành động đúng với bản chất tâm lý: Lợi ích cốt lõi, Nỗi sợ ngầm và Lập trường. "
            "Có 3 lớp hành vi rõ rệt:\n"
            "1. public_action: Lời nói hoặc động thái công khai tại cuộc họp/văn phòng.\n"
            "2. private_thought: Toan tính mưu mô thật sự trong đầu (độc thoại nội tâm).\n"
            "3. whisper_target & whisper_content: Lời thì thầm hành lang, cấu kết phe cánh với nhân vật khác.\n"
            "Định dạng trả về JSON thuần túy:\n"
            "{\n"
            '  "round_summary": "Tóm lược toàn cảnh cục diện vòng này (3-4 câu sắc bén)",\n'
            '  "actions": [\n'
            '    {\n'
            '      "persona_id": "p_1",\n'
            '      "public_action": "...",\n'
            '      "private_thought": "...",\n'
            '      "whisper_target": "Tên người thì thầm (nếu có)",\n'
            '      "whisper_content": "Lời rỉ tai toan tính",\n'
            '      "stance_shift": "Lập trường mới",\n'
            '      "loyalty_change": -5,\n'
            '      "stress_change": 10\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        history_summary = []
        for r in session.rounds:
            history_summary.append(f"Vòng {r.round_number} ({r.stage_name}): {r.round_summary}")

        user_prompt = (
            f"Kịch bản: {session.scenario}\n"
            f"Lịch sử các vòng trước: {chr(10).join(history_summary) if history_summary else 'Chưa có'}\n"
            f"Vòng hiện tại: {stage_name} (Vòng {round_num})\n"
            f"Lệnh can thiệp của Người điều hành (nếu có): {intervention or 'Không có (để diễn biến tự nhiên)'}\n"
            f"Danh sách nhân vật hiện tại:\n{json.dumps([p.to_dict() for p in session.personas], ensure_ascii=False)}"
        )

        data = self._call_llm_json(system_prompt, user_prompt)
        if data and isinstance(data.get("actions"), list) and len(data["actions"]) >= 2:
            p_dict = {p.id: p for p in session.personas}
            actions = []
            for act in data["actions"]:
                pid = act.get("persona_id", "")
                persona = p_dict.get(pid)
                name = persona.name if persona else f"Nhân vật {pid}"
                role = persona.role if persona else "Quản lý"
                avatar = persona.avatar if persona else "👤"

                actions.append(PersonaAction(
                    persona_id=pid,
                    persona_name=name,
                    role=role,
                    avatar=avatar,
                    public_action=str(act.get("public_action", "")),
                    private_thought=str(act.get("private_thought", "")),
                    whisper_target=str(act.get("whisper_target", "")),
                    whisper_content=str(act.get("whisper_content", "")),
                    stance_shift=str(act.get("stance_shift", "")),
                    loyalty_change=int(act.get("loyalty_change", 0)),
                    stress_change=int(act.get("stress_change", 0)),
                ))

            return RoundResult(
                round_number=round_num,
                stage_name=stage_name,
                round_summary=str(data.get("round_summary", f"Giai đoạn {stage_name} hoàn tất với nhiều toan tính ngầm bộc lộ.")),
                intervention=intervention,
                actions=actions,
            )
        return None

    def _step_round_deterministic(self, session: WarRoomSession, round_num: int, stage_name: str, intervention: str | None) -> RoundResult:
        """Deep deterministic behavioral progression generator."""
        actions: list[PersonaAction] = []
        summary = ""

        # Pre-built narrative arcs per round
        if round_num == 1:
            summary = (
                "Thông tin biến cố bắt đầu lan truyền ngầm qua các kênh phi chính thức. "
                "Bầu không khí công sở chùng xuống, các cuộc trò chuyện hành lang và nhóm chat mật liên tục xuất hiện. "
                "Từng nhân vật bắt đầu dựng rào chắn phòng thủ tâm lý."
            )
            for p in session.personas:
                if "vận hành" in p.role.lower() or "coo" in p.role.lower() or "kỹ thuật" in p.role.lower():
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"Tại buổi họp giao ban, {p.name} nhấn mạnh: 'Đội ngũ của tôi đang quá tải nghiêm trọng, bất kỳ xáo trộn nào lúc này cũng sẽ làm tê liệt sản phẩm'.",
                        private_thought="Mình phải cảnh báo trước để cấp trên thấy hậu quả. Đồng thời phải rà soát lại các dự án huyết mạch, không để bị nắm đằng chuôi.",
                        whisper_target="Trưởng bộ phận thân tín",
                        whisper_content="Bảo anh em cứ bình tĩnh làm việc, nhưng cập nhật ngay CV và sao lưu các tài liệu quan trọng đề phòng bất trắc.",
                        stance_shift="Thận trọng & Đề phòng cao độ",
                        loyalty_change=-5,
                        stress_change=+15,
                    )
                elif "nhân sự" in p.role.lower() or "chro" in p.role.lower():
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} ra thông báo nội bộ kêu gọi toàn thể cán bộ công nhân viên 'tập trung vào công việc và không lan truyền tin đồn thất thiệt'.",
                        private_thought="Tin tức rò rỉ nhanh quá, danh sách thẩm định còn chưa xong. Nếu công đoàn hoặc truyền thông biết thì mình sẽ là bia đỡ đạn đầu tiên.",
                        whisper_target="Cố Vấn Pháp Lý",
                        whisper_content="Kiểm tra lại toàn bộ điều khoản trợ cấp thôi việc và rà soát hợp đồng của các nhân sự diện ký không thời hạn ngay.",
                        stance_shift="Tập trung phòng thủ pháp lý",
                        loyalty_change=0,
                        stress_change=+20,
                    )
                elif "tài chính" in p.role.lower() or "cfo" in p.role.lower() or "kiểm soát" in p.role.lower():
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} trình bày bảng biểu chi phí lạnh lùng: 'Các phòng ban cần tự rà soát hiệu suất, con số không biết nói dối'.",
                        private_thought="Nếu không hạ chi phí ngay, tháng sau ngân sách sẽ cạn kiệt. Cứ theo nguyên tắc mà làm, tình cảm lúc này là tự sát.",
                        whisper_target="Tổng Giám Đốc",
                        whisper_content="Không thể chần chừ thêm được nữa, mỗi tuần trì hoãn công ty mất thêm hàng trăm triệu chi phí thừa.",
                        stance_shift="Triệt để tuân thủ kỷ luật số liệu",
                        loyalty_change=+5,
                        stress_change=+10,
                    )
                else:
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} khéo léo dò hỏi quan điểm của các bên trong các buổi ăn trưa và cà phê.",
                        private_thought="Gió sắp đổi chiều. Cần xác định xem phe nào đang nắm quyền sinh sát thực sự để chọn chỗ đứng an toàn.",
                        whisper_target="Đồng nghiệp lâu năm",
                        whisper_content="Nghe nói đợt này Chủ tịch quyết tâm làm sạch, liệu có ai bảo kê cho phòng mình không?",
                        stance_shift="Dao động & Quan sát",
                        loyalty_change=-8,
                        stress_change=+12,
                    )
                actions.append(act)

        elif round_num == 2:
            summary = (
                "Sự phân hóa quyền lực diễn ra sâu sắc. Các phe phái bắt đầu thiết lập liên minh ngầm để bảo vệ nhau. "
                "Có dấu hiệu trì hoãn công việc và phản kháng thụ động ở các bộ phận chủ lực."
            )
            if intervention:
                summary += f" Lệnh can thiệp từ Người điều hành ('{intervention[:60]}...') tạo ra làn sóng phản ứng mạnh mẽ trong toàn tổ chức."

            for p in session.personas:
                if "vận hành" in p.role.lower() or "kỹ thuật" in p.role.lower():
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} chủ động báo cáo dự án chậm tiến độ với lý do 'tâm lý anh em bất an, không thể tập trung chạy nước rút'.",
                        private_thought="Đây là lá bài thương lượng duy nhất của mình. Nếu Ban lãnh đạo ép quá, toàn bộ deadline quý này sẽ sụp đổ.",
                        whisper_target="Các Trưởng Nhóm",
                        whisper_content="Cứ làm đúng giờ hành chính, không nhận thêm task ngoài lề. Để xem không có chúng ta thì hệ thống chạy kiểu gì.",
                        stance_shift="Kháng cự có tổ chức (Lãnh công thụ động)",
                        loyalty_change=-15,
                        stress_change=+25,
                    )
                elif "nhân sự" in p.role.lower():
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} tổ chức các cuộc đối thoại 1-1 nhằm xoa dịu những nhân vật có dấu hiệu quá khích.",
                        private_thought="Phe kỹ thuật đang làm giá, phe tài chính thì thúc ép. Mình kẹt ở giữa như chiếc bánh mì kẹp thịt.",
                        whisper_target="Chủ Tịch HĐQT",
                        whisper_content="Cần có chính sách giữ chân đặc biệt cho top 5% cốt cán, nếu không sẽ xảy ra làn sóng tháo chạy dây chuyền.",
                        stance_shift="Tìm kiếm giải pháp thỏa hiệp",
                        loyalty_change=+5,
                        stress_change=+25,
                    )
                else:
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} bắt đầu công khai thể hiện sự ủng hộ có điều kiện đối với các quyết sách từ thượng tầng.",
                        private_thought="Nhóm công thần đang chống đối, đây là cơ hội vàng để nhóm mình chứng minh giá trị và chiếm lĩnh các dự án bỏ trống.",
                        whisper_target="Cộng sự thân cận",
                        whisper_content="Chuẩn bị sẵn tài liệu phương án thay thế, khi bên kia gãy là chúng ta nhảy vào tiếp quản ngay.",
                        stance_shift="Cơ hội & Tiến công",
                        loyalty_change=-5,
                        stress_change=-5,
                    )
                actions.append(act)

        else: # Round 3 or later
            summary = (
                "Xung đột quyền lợi bùng nổ đến đỉnh điểm. Mắt xích yếu nhất trong hệ thống bắt đầu xuất hiện vết nứt nghiêm trọng. "
                "Cục diện đòi hỏi một đòn quyết định mang tính chiến lược dứt khoát từ người nắm quyền tối cao."
            )
            if intervention:
                summary += f" Tác động trực tiếp từ sắc lệnh can thiệp ('{intervention[:60]}...') đã buộc các nhân vật phải ngửa bài tẩy."

            for p in session.personas:
                if p.loyalty_score < 50:
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} chính thức đệ trình bản yêu sách hoặc đơn xin từ nhiệm kèm danh sách các dự án dang dở.",
                        private_thought="Thế cờ đã tàn, ở lại chỉ chuốc lấy thua thiệt. Ra đi lúc này vừa giữ được giá trị vừa tạo áp lực cực đại cho tổ chức.",
                        whisper_target="Đối thủ / Headhunter ngoài",
                        whisper_content="Tôi đã sẵn sàng bắt đầu vào tuần tới, toàn bộ dữ liệu quan trọng đã được đồng bộ an toàn.",
                        stance_shift="Đoạn tuyệt & Đối kháng trực diện",
                        loyalty_change=-20,
                        stress_change=+30,
                    )
                elif p.loyalty_score >= 80:
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} công bố lộ trình kỷ luật thép và phương án thay thế khẩn cấp để phong tỏa thiệt hại.",
                        private_thought="Phải chặt đứt ung nhọt ngay lập tức. Đau một lần rồi thôi, thà tổ chức nhỏ lại nhưng kỷ cương còn hơn đông đúc mà loạn thế.",
                        whisper_target="Đội ngũ kế thừa",
                        whisper_content="Các em chuẩn bị nhận bàn giao các mảng việc của phòng bên cạnh, ai nhận việc tốt sẽ được bổ nhiệm ngay.",
                        stance_shift="Kiên định thanh trừng & Tái lập trật tự",
                        loyalty_change=+10,
                        stress_change=+15,
                    )
                else:
                    act = PersonaAction(
                        persona_id=p.id,
                        persona_name=p.name,
                        role=p.role,
                        avatar=p.avatar,
                        public_action=f"{p.name} im lặng tuyệt đối trong cuộc họp chung nhưng gấp rút hoàn thành các nghĩa vụ tối thiểu.",
                        private_thought="Cơn bão đã ập đến. Chỉ cần không dính líu đến phe nổi loạn thì sau đợt này ghế của mình vẫn vững.",
                        whisper_target="Trợ lý cá nhân",
                        whisper_content="Tuyệt đối không ký bất kỳ văn bản nào trong 72 giờ tới nếu chưa có chữ ký nháy của Tổng Giám Đốc.",
                        stance_shift="Quy ẩn phòng thân (Đạo Gia Vô Vi)",
                        loyalty_change=-5,
                        stress_change=-10,
                    )
                actions.append(act)

        return RoundResult(
            round_number=round_num,
            stage_name=stage_name,
            round_summary=summary,
            intervention=intervention,
            actions=actions,
        )

    def generate_strategic_report(self, session_id: str) -> dict[str, Any]:
        """Synthesize simulation history into an executive strategic war room report."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # Identify most dangerous/vulnerable link
        lowest_loyalty_persona = min(session.personas, key=lambda p: p.loyalty_score)
        highest_stress_persona = max(session.personas, key=lambda p: p.stress_level)

        # Try LLM report generation
        report = self._generate_report_llm(session, lowest_loyalty_persona, highest_stress_persona)
        if not report:
            report = self._generate_report_deterministic(session, lowest_loyalty_persona, highest_stress_persona)

        session.report = report
        session.status = "COMPLETED"
        session.updated_at = time.time()
        return report

    def _generate_report_llm(self, session: WarRoomSession, vulnerable_p: Persona, stressed_p: Persona) -> dict[str, Any] | None:
        """Call LLM to synthesize deep strategic war room recommendations."""
        system_prompt = (
            "Bạn là Cố Vấn Tối Cao của Viện Chiến Lược Nhân Thuật. Hãy tổng hợp toàn bộ dữ liệu mô phỏng Sa Bàn Tình Thế "
            "thành một Báo Cáo Tham Mưu Chiến Lược chuẩn mực, sắc sảo, vận dụng tri thức 5 phái (Pháp, Nho, Đạo, Tuân, Hùng Biện). "
            "Trả về JSON định dạng:\n"
            "{\n"
            '  "executive_summary": "Tóm lược kết cục tình thế và rủi ro lớn nhất",\n'
            '  "vulnerable_link": "Phân tích mắt xích nguy hiểm nhất và toan tính của nhân vật này",\n'
            '  "critical_breakdown_point": "Điểm gãy tổ chức dự báo nếu không xử lý kịp thời",\n'
            '  "factional_matrix": [\n'
            '    {"faction": "Tên phe", "motive": "Động cơ", "risk_level": "Cao/Trung bình/Thấp"}\n'
            '  ],\n'
            '  "actionable_strategies": [\n'
            '    {\n'
            '      "name": "Tên kế sách (Chuẩn văn phong Nhân Thuật)",\n'
            '      "philosophy": "Pháp Trị / Nho Gia / Đạo Gia / Tuân Tử",\n'
            '      "steps": ["Bước 1...", "Bước 2..."],\n'
            '      "expected_outcome": "Kết quả dự kiến",\n'
            '      "citation": "Mã Unit hoặc quy luật tham chiếu"\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        simulation_log = []
        for r in session.rounds:
            simulation_log.append(f"Vòng {r.round_number} ({r.stage_name}):\n- Tóm lược: {r.round_summary}")
            for a in r.actions:
                simulation_log.append(f"  * {a.persona_name} ({a.role}): Công khai: {a.public_action} | Nghĩ ngầm: {a.private_thought} | Rỉ tai: {a.whisper_content}")

        user_prompt = (
            f"Kịch bản khởi tạo: {session.scenario}\n\n"
            f"Diễn biến qua các vòng mô phỏng:\n{chr(10).join(simulation_log)}\n\n"
            f"Các can thiệp của Người điều hành:\n{json.dumps(session.interventions, ensure_ascii=False)}\n\n"
            f"Tri thức đối chiếu liên quan: {json.dumps(session.relevant_units, ensure_ascii=False)}"
        )

        data = self._call_llm_json(system_prompt, user_prompt)
        if data and "executive_summary" in data and "actionable_strategies" in data:
            return data
        return None

    def _generate_report_deterministic(self, session: WarRoomSession, vulnerable_p: Persona, stressed_p: Persona) -> dict[str, Any]:
        """Rich deterministic strategic report based on classic statecraft patterns."""
        factions = list({p.faction for p in session.personas})
        faction_matrix = []
        for f in factions:
            members = [p for p in session.personas if p.faction == f]
            avg_loyalty = sum(p.loyalty_score for p in members) // len(members)
            risk = "Nguy Cơ Cao (Bất Mãn)" if avg_loyalty < 55 else ("Nguy Cơ Trung Bình (Dao Động)" if avg_loyalty < 75 else "An Toàn (Kiểm Soát Được)")
            faction_matrix.append({
                "faction": f,
                "motive": f"Bảo toàn quyền lợi và vị thế của các nhân sự cốt cán thuộc {f}",
                "risk_level": risk,
                "key_actors": ", ".join([p.name for p in members]),
            })

        citation_unit = session.relevant_units[0]["title"] if session.relevant_units else "Quy Luật Cân Bằng Quyền Bính"

        return {
            "executive_summary": (
                f"Cuộc mô phỏng qua {session.current_round} vòng cho thấy tổ chức đang đối diện với sự chia rẽ quyền lực ngầm. "
                f"Tình thế không thể giải quyết bằng các mệnh lệnh hành chính đơn thuần khi mà lòng người đã ly tán và "
                f"các phe phái đã hình thành cơ chế phản kháng thụ động."
            ),
            "vulnerable_link": (
                f"Mắt xích nguy hiểm nhất hiện nay là {vulnerable_p.name} ({vulnerable_p.role} - Độ trung thành: {vulnerable_p.loyalty_score}%). "
                f"Nhân vật này đang nắm giữ tài nguyên trọng yếu nhưng cảm thấy bị đe dọa trực tiếp đến quyền lợi cốt lõi "
                f"('{vulnerable_p.core_interest}'), do đó đã chuyển từ thế thăm dò sang toan tính đối kháng ngầm hoặc đào tẩu."
            ),
            "critical_breakdown_point": (
                f"Điểm gãy tổ chức dự báo sẽ diễn ra tại khối {stressed_p.faction} do {stressed_p.name} dẫn đầu "
                f"(Mức độ stress: {stressed_p.stress_level}%). Sự quá tải áp lực kết hợp với nỗi sợ '{stressed_p.hidden_fear}' "
                f"sẽ khiến bộ phận này tê liệt vận hành hoặc tạo ra làn sóng nộp đơn nghỉ việc dây chuyền trong 14-30 ngày tới."
            ),
            "factional_matrix": faction_matrix,
            "actionable_strategies": [
                {
                    "name": "Kế Sách 1: Phân Hóa Lực Lượng & Tách Rời Thủ Lĩnh Ngầm",
                    "philosophy": "Pháp Trị (Hàn Phi Tử) - Minh Pháp Thẩm Lệnh",
                    "steps": [
                        f"Gặp gỡ riêng {vulnerable_p.name}, công khai khẳng định ghi nhận công lao trong quá khứ nhưng lập tức phân tán quyền phê duyệt độc quyền.",
                        "Tách rời các nhân sự cấp dưới có năng lực của phe phản kháng bằng cách trao cơ hội thăng tiến độc lập, phá vỡ thế liên minh bầy đàn.",
                        "Thiết lập kênh giám sát độc lập đối với các tài sản, dữ liệu hoặc hợp đồng nhạy cảm.",
                    ],
                    "expected_outcome": "Vô hiệu hóa thế kiềm tỏa của phe cựu trào mà không làm bùng phát khủng hoảng truyền thông công khai.",
                    "citation": f"Kế thừa từ tri thức: {citation_unit}",
                },
                {
                    "name": "Kế Sách 2: Ban Ơn Giải Tỏa Áp Lực & Ổn Định Tâm Lý Đám Đông",
                    "philosophy": "Nho Gia & Tuân Tử - Thu Phục Nhân Tâm",
                    "steps": [
                        f"Gặp gỡ và tháo gỡ trực tiếp gánh nặng stress cho {stressed_p.name} bằng cách cử thêm trợ lý đặc trách chia sẻ khối lượng công việc.",
                        "Tổ chức hội nghị đối thoại minh bạch, công bố các cam kết bảo vệ quyền lợi chính đáng cho những nhân sự tuân thủ kỷ luật.",
                        "Thiết lập cơ chế 'Ân trước Uy sau', cô lập nhóm chống đối cực đoan khỏi số đông còn lại.",
                    ],
                    "expected_outcome": "Hạ nhiệt căng thẳng nội bộ, kéo mức độ stress tổ chức về ngưỡng an toàn dưới 50%.",
                    "citation": "NT-LAW-003: Quy luật Vị Thế và Sự An Toàn Tâm Lý",
                },
                {
                    "name": "Kế Sách 3: Tái Cấu Trúc Bàn Cờ - Dụng Người Bất Nghi",
                    "philosophy": "Đạo Gia - Thuận Tự Nhiên & Dĩ Nhu Chế Cương",
                    "steps": [
                        "Chuyển đổi các xung đột đối đầu trực diện thành cuộc đua hiệu suất minh bạch (KPIs/OKRs định lượng).",
                        "Chuẩn bị sẵn sàng kịch bản nhân sự dự phòng (Shadow Team) để thay thế tức thì nếu mắt xích yếu nhất quyết định ra đi.",
                        "Giữ thái độ điềm tĩnh của người nắm chuôi gươm, không đưa ra quyết định trừng phạt trong lúc cảm xúc dâng cao.",
                    ],
                    "expected_outcome": "Thiết lập trạng thái cân bằng quyền lực mới bền vững và thanh lọc các phần tử tiêu cực mà không làm suy yếu cốt lõi doanh nghiệp.",
                    "citation": "NT-STRAT-012: Thế Cân Bằng Càn Khôn Trong Quản Trị Tổ Chức",
                },
            ],
        }
