"""
Test suite for Grand Philosophy Architecture & 5-Tier Strategic Treatise Engine.
"""

from backend.app.engine.philosophies.router import PhilosophyRouter, PhilosophyType
from nhan_thuat.engine.sparring_engine import SparringEngine, default_route_philosophy
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.models import KnowledgeUnit
from nhan_thuat.runtime.synthesizer import KnowledgeSynthesizer


def test_grand_philosophy_engines_loaded():
    """Verify that all grand philosophy engines including Machiavellian, Guiguzi, Game Theory, and Biases are loaded."""
    router = PhilosophyRouter()
    assert PhilosophyType.MACHIAVELLIAN in router.engines
    assert PhilosophyType.GUIGUZI in router.engines
    assert PhilosophyType.GAME_THEORY in router.engines
    assert PhilosophyType.BEHAVIORAL_BIASES in router.engines
    assert "error" not in router.engines[PhilosophyType.MACHIAVELLIAN]
    assert "error" not in router.engines[PhilosophyType.GUIGUZI]
    assert "error" not in router.engines[PhilosophyType.GAME_THEORY]
    assert "error" not in router.engines[PhilosophyType.BEHAVIORAL_BIASES]


def test_grand_philosophy_routing_resolution():
    """Verify scenario routing to the new grand philosophy lenses."""
    router = PhilosophyRouter()

    res_mach = router.route({"scenario_type": "power", "intent": "Đối tác đe dọa phản trắc và lộng quyền, cần áp dụng tư duy quân vương Machiavellian sư tử và cáo"})
    assert res_mach["primary_philosophy"] == "machiavellian"

    res_gui = router.route({"scenario_type": "negotiation", "intent": "Vận dụng thuật Quỷ Cốc Tử bách hợp và phi kiềm để thấu tâm can và gài thế đối phương"})
    assert res_gui["primary_philosophy"] == "guiguzi"

    res_game = router.route({"scenario_type": "strategy", "intent": "Phân tích thế trận theo lý thuyết trò chơi và ma trận cân bằng Nash trong đàm phán"})
    assert res_game["primary_philosophy"] == "game_theory"

    res_bias = router.route({"scenario_type": "psychology", "intent": "Nhận diện bẫy tâm lý loss aversion ác cảm mất mát và mỏ neo giá của khách hàng"})
    assert res_bias["primary_philosophy"] == "behavioral_biases"


def test_sparring_engine_grand_philosophies():
    """Verify sparring engine routing and fallback generation for new grand lenses."""
    assert default_route_philosophy("Dùng tư duy Quân vương Machiavellian để răn đe") == "MACHIAVELLIAN"
    assert default_route_philosophy("Vận dụng Quỷ Cốc Tử bách hợp đối thoại") == "GUIGUZI"
    assert default_route_philosophy("Ma trận trò chơi game theory Nash") == "GAME_THEORY"
    assert default_route_philosophy("Bẫy tâm lý mỏ neo và loss aversion") == "BEHAVIORAL_BIASES"

    sparring = SparringEngine()
    resp_mach, _ = sparring._generate_sparring_response(
        user_text="Chúng tôi muốn hợp tác hòa bình",
        lens="MACHIAVELLIAN",
        units=[],
        related_map={},
    )
    assert "Sư tử" in resp_mach
    assert "Cáo" in resp_mach
    assert "### ⚔️ 1. ĐỐI ĐÁP PHẢN BIỆN TRỰC DIỆN" in resp_mach
    assert "### 💡 2. GỢI Ý ĐÒN BẨY HÓA GIẢI" in resp_mach


def test_synthesizer_5_tier_strategic_treatise():
    """Verify KnowledgeSynthesizer produces an exhaustive 5-tier strategic treatise with verbatim action script."""
    engine = KnowledgeEngine()
    units = [KnowledgeUnit.from_mapping(iu.raw_data, source_path=None) for iu in list(engine.units_by_id.values())[:3]]

    synthesizer = KnowledgeSynthesizer()
    prompt = synthesizer._build_prompt("Đối tác dọa cắt hợp đồng nếu không giảm giá 25%", units)
    assert "NGŨ ĐẠI HỆ HÌNH TRIẾT HỌC" in prompt
    assert "### 🎯 TÓM TẮT ĐIỀU HÀNH" in prompt
    assert "### 👁️ TỔNG QUAN TÌNH THẾ" in prompt
    assert "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM" in prompt
    assert "### ⚠️ 2. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH" in prompt
    assert "### ⚔️ 3. ĐÒN BẨY ĐỊNH CỤC & KỊCH BẢN LỜI THOẠI THỰC CHIẾN (VERBATIM SCRIPT)" in prompt

    result = synthesizer.synthesize("Đối tác dọa cắt hợp đồng nếu không giảm giá 25%", units)
    synthesis = result["synthesis"]

    assert "### 🎯 TÓM TẮT ĐIỀU HÀNH" in synthesis
    assert "### 👁️ TỔNG QUAN TÌNH THẾ" in synthesis
    assert "### 🔍 1. BÓC TÁCH BẢN CHẤT & ĐỘNG CƠ NGẦM" in synthesis
    assert "Tam tầng lợi ích" in synthesis
    assert "### ⚠️ 2. NHỮNG BẪY TÂM LÝ & SAI LẦM CẦN TRÁNH" in synthesis
    assert "### ⚔️ 3. ĐÒN BẨY ĐỊNH CỤC & KỊCH BẢN LỜI THOẠI THỰC CHIẾN (VERBATIM SCRIPT)" in synthesis
    assert "Pha 1: Tháo ngòi nổ" in synthesis
    assert "Pha 2: Tái định vị ranh giới" in synthesis
    assert "Pha 3: Khóa thế" in synthesis
    assert "Chiếc cầu vàng" in synthesis or "Chiếc Cầu Vàng" in synthesis
