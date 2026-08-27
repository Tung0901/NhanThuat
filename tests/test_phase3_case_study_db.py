"""
Test Suite for Phase 3: Stateful Storage, Case Study Database, Sparring Engine, Department Packs & Executive Briefing.
"""

from pathlib import Path

import pytest

from nhan_thuat.engine.sparring_engine import SparringEngine
from nhan_thuat.export.executive_brief import ExecutiveBriefExporter
from nhan_thuat.knowledge_engine import KnowledgeEngine
from nhan_thuat.packs.department_pack import DepartmentPackRegistry
from nhan_thuat.storage.db import DatabaseManager
from nhan_thuat.storage.models import CaseStudy, SparringMessage, SparringSession


@pytest.fixture
def mem_db() -> DatabaseManager:
    """Provides an isolated, in-memory SQLite database manager for fast testing."""
    return DatabaseManager(db_path=":memory:")


@pytest.fixture
def sparring_engine(mem_db: DatabaseManager) -> SparringEngine:
    engine = KnowledgeEngine()
    return SparringEngine(db_manager=mem_db, knowledge_engine=engine)


def test_database_initialization_and_seed_data(mem_db: DatabaseManager) -> None:
    # Verify default seed case studies were created
    cases = mem_db.list_case_studies()
    assert len(cases) >= 3

    domains = {c.domain for c in cases}
    assert "OPS" in domains
    assert "SALES" in domains
    assert "HR" in domains

    # Verify specific case fields
    ops_case = next(c for c in cases if c.domain == "OPS")
    assert "Nhà Bè" in ops_case.title
    assert "position_analysis" in ops_case.decision_script
    assert len(ops_case.lessons_learned) >= 1


def test_sparring_session_crud(mem_db: DatabaseManager) -> None:
    # 1. Create
    session = mem_db.create_session(
        title="Đàm phán gia hạn hợp đồng Nhà Bè",
        philosophy_lens="LEGALISM",
        metadata={"project": "Nha Be Phase 2"},
    )
    assert session.id.startswith("SPAR-SESS-")
    assert session.status == "active"
    assert session.metadata.get("project") == "Nha Be Phase 2"

    # 2. Get
    fetched = mem_db.get_session(session.id)
    assert fetched is not None
    assert fetched.title == "Đàm phán gia hạn hợp đồng Nhà Bè"

    # 3. Update
    updated = mem_db.update_session(session.id, status="completed", summary="Đã thống nhất chế tài.")
    assert updated is True
    fetched_after = mem_db.get_session(session.id)
    assert fetched_after.status == "completed"
    assert fetched_after.summary == "Đã thống nhất chế tài."

    # 4. List
    sessions = mem_db.list_sessions(limit=10)
    assert len(sessions) >= 1
    assert any(s.id == session.id for s in sessions)

    # 5. Delete
    deleted = mem_db.delete_session(session.id)
    assert deleted is True
    assert mem_db.get_session(session.id) is None


def test_sparring_message_logging(mem_db: DatabaseManager) -> None:
    session = mem_db.create_session(title="Phiên tranh biện kỷ luật")
    
    # Add User message
    msg1 = mem_db.add_message(
        session_id=session.id,
        role="user",
        content="Nhân viên vi phạm báo cáo sai số liệu, tôi định du di nhắc nhở riêng.",
    )
    assert msg1.id.startswith("MSG-")
    assert msg1.role == "user"

    # Add Assistant message
    msg2 = mem_db.add_message(
        session_id=session.id,
        role="assistant",
        content="Lập luận này mắc bẫy cả nể của Nho gia biến tướng! Cần áp dụng Pháp gia.",
        matched_unit_ids=["NT-LAW-0005", "NT-PRINCIPLE-0061"],
    )
    assert msg2.role == "assistant"
    assert "NT-LAW-0005" in msg2.matched_unit_ids

    # List messages
    messages = mem_db.list_messages(session.id)
    assert len(messages) == 2
    assert messages[0].role == "user"
    assert messages[1].role == "assistant"


def test_case_study_crud_and_filtering(mem_db: DatabaseManager) -> None:
    new_case = mem_db.create_case_study(
        domain="FINANCE",
        title="Xử lý công nợ khó đòi đối tác chiến lược",
        context_description="Đối tác nợ 5 tỷ quá hạn 90 ngày.",
        decision_script={"action": "Gửi công văn hạn định 48h"},
        lessons_learned=["Không để đối tác chiếm dụng dòng tiền."],
        tags=["debt", "cashflow", "legalism"],
    )
    assert new_case.id.startswith("CASE-FINANCE-")
    assert new_case.domain == "FINANCE"

    # Filter by domain
    finance_cases = mem_db.list_case_studies(domain="FINANCE")
    assert len(finance_cases) == 1
    assert finance_cases[0].id == new_case.id

    ops_cases = mem_db.list_case_studies(domain="OPS")
    assert all(c.domain == "OPS" for c in ops_cases)

    # Delete
    assert mem_db.delete_case_study(new_case.id) is True
    assert mem_db.get_case_study(new_case.id) is None


def test_sparring_engine_multi_turn_flow(sparring_engine: SparringEngine) -> None:
    # 1. Start session
    session = sparring_engine.start_session(
        title="Thương lượng đối tác chậm vật tư",
        philosophy_lens="LEGALISM",
        initial_context="Công trình Nhà Bè chậm 3 ngày.",
    )
    assert session.id.startswith("SPAR-SESS-")

    # 2. Turn 1: User proposal
    turn1 = sparring_engine.process_turn(
        session_id=session.id,
        user_message="Tôi muốn gia hạn thêm 2 ngày không phạt để giữ mối quan hệ hữu hảo.",
        override_lens="LEGALISM",
    )
    assert turn1["status"] == "success"
    assert turn1["philosophy_lens"] == "LEGALISM"
    assert "ĐỐI ĐÁP PHẢN BIỆN TRỰC DIỆN" in turn1["response"]
    assert "GỢI Ý ĐÒN BẨY HÓA GIẢI" in turn1["response"]
    assert len(turn1["matched_unit_ids"]) >= 1
    assert len(turn1["citations"]) >= 1

    # 3. Turn 2: User responds
    turn2 = sparring_engine.process_turn(
        session_id=session.id,
        user_message="Nếu đối tác vẫn cương quyết đòi hủy hợp đồng thì tôi nên mở Plan B như thế nào?",
    )
    assert turn2["status"] == "success"
    assert turn2["session_id"] == session.id

    # Verify persistent transcript in DB
    all_msgs = sparring_engine.db.list_messages(session.id)
    # 1 system + 2 user + 2 assistant = 5 messages
    assert len(all_msgs) == 5


def test_department_pack_registry() -> None:
    registry = DepartmentPackRegistry()
    packs = registry.list_packs()
    assert len(packs) == 3

    # Test HR Pack
    hr_pack = registry.get_pack("HR")
    assert hr_pack is not None
    assert hr_pack.domain_id == "HR"
    assert hr_pack.philosophy_primary == "XUNZI"
    assert len(hr_pack.core_laws) >= 1

    # Test Ops Pack
    ops_pack = registry.get_pack("OPS")
    assert ops_pack is not None
    assert ops_pack.domain_id == "OPS"
    assert ops_pack.philosophy_primary == "LEGALISM"

    # Test Sales Pack
    sales_pack = registry.get_pack("SALES")
    assert sales_pack is not None
    assert sales_pack.domain_id == "SALES"
    assert sales_pack.philosophy_primary == "RHETORIC"

    # Test evaluation
    eval_res = registry.evaluate_scenario("OPS", "Chậm vật tư hiện trường")
    assert eval_res["status"] == "success"
    assert len(eval_res["rubrics"]) == 3
    assert "NT-LAW-0005" in eval_res["recommended_units"]


def test_executive_brief_exporter(mem_db: DatabaseManager) -> None:
    exporter = ExecutiveBriefExporter()
    case = mem_db.list_case_studies(domain="OPS")[0]

    # 1. Export Case Study to Markdown
    md_output = exporter.export_case_study(case, format="markdown")
    assert "# BẢN THAM MƯU & CHỈ ĐẠO ĐIỀU HÀNH:" in md_output
    assert "1. TÓM TẮT TÌNH HUỐNG HIỆN TRƯỜNG" in md_output
    assert "3. KỊCH BẢN ĐỐI THOẠI 3 BƯỚC" in md_output
    assert "6. BÀI HỌC QUẢN TRỊ RÚT RA" in md_output

    # 2. Export Case Study to HTML
    html_output = exporter.export_case_study(case, format="html")
    assert "<!DOCTYPE html>" in html_output
    assert "BẢN THAM MƯU ĐIỀU HÀNH" in html_output
    assert "BusinessOS Executive Briefing" in html_output
    assert "@media print" in html_output

    # 3. Export Sparring Session Transcript
    session = mem_db.create_session(title="Phiên đàm phán mẫu")
    mem_db.add_message(session.id, "user", "Khách hàng chê đắt.")
    mem_db.add_message(session.id, "assistant", "Bẻ gãy khung chi phí.", matched_unit_ids=["NT-LAW-0054"])
    msgs = mem_db.list_messages(session.id)

    sparring_md = exporter.export_sparring_session(session, msgs, format="markdown")
    assert "BIÊN BẢN ĐẤU TRÍ ĐIỀU HÀNH" in sparring_md
    assert "CHỦ TỊCH / NGƯỜI DÙNG" in sparring_md
    assert "CỐ VẤN ĐẤU TRÍ NHÂN THUẬT" in sparring_md

    sparring_html = exporter.export_sparring_session(session, msgs, format="html")
    assert "<!DOCTYPE html>" in sparring_html
    assert "BIÊN BẢN ĐẤU TRÍ ĐIỀU HÀNH" in sparring_html


def test_main_api_gateway_integration() -> None:
    from backend.app.main import brief_exporter, db_manager, department_packs, sparring_engine

    # 1. Sparring flow via global instances
    sess = sparring_engine.start_session("Phiên đàm phán hợp đồng cung ứng", philosophy_lens="LEGALISM")
    assert sess.id.startswith("SPAR-SESS-")

    turn = sparring_engine.process_turn(sess.id, "Nhà thầu phụ dọa dừng thi công nếu không ứng tiền trước.")
    assert turn["status"] == "success"
    assert turn["philosophy_lens"] == "LEGALISM"
    assert len(turn["matched_unit_ids"]) >= 1

    # 2. Case study creation & retrieval
    c = db_manager.create_case_study(
        domain="OPS",
        title="Quản trị an toàn lao động hiện trường",
        context_description="Công nhân không tuân thủ đồ bảo hộ.",
        decision_script={"rule": "Đình chỉ và xử phạt nhà thầu phụ."},
        lessons_learned=["Kỷ luật không thỏa hiệp."],
        tags=["safety", "ops"],
    )
    assert c.id.startswith("CASE-OPS-")
    fetched = db_manager.get_case_study(c.id)
    assert fetched is not None
    assert fetched.title == "Quản trị an toàn lao động hiện trường"

    # 3. Department packs
    packs = department_packs.list_packs()
    assert len(packs) == 3
    assert department_packs.get_pack("HR").domain_id == "HR"

    # 4. Brief Exporter
    brief_md = brief_exporter.export_brief(
        title="Chỉ đạo thi công khẩn cấp",
        situation_summary="Hiện trường ngưng trệ 24h",
        philosophy_analysis="Kích hoạt chế tài Pháp gia",
        action_script={"step_1": "Lập biên bản vi phạm", "step_2": "Ấn định 12h", "step_3": "Plan B"},
        knowledge_units=[{"id": "NT-LAW-0005", "title": "Động lực & Chế tài", "domain": "OPS"}],
        directives=["Phạt 0.5%/ngày"],
        format="markdown",
    )
    assert "CHỈ ĐẠO THI CÔNG KHẨN CẤP" in brief_md
    assert "NT-LAW-0005" in brief_md

