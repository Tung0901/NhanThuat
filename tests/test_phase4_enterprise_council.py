"""
Test Suite for Phase 4: Enterprise Multi-Agent Advisory Council, Python SDK & Deployment Packaging.
"""

from pathlib import Path

import pytest

from nhan_thuat.council.council_engine import CouncilEngine
from nhan_thuat.knowledge_engine import KnowledgeEngine
from sdk.python.nhan_thuat_sdk import NhanThuatClient


@pytest.fixture(scope="module")
def council_engine() -> CouncilEngine:
    engine = KnowledgeEngine()
    return CouncilEngine(knowledge_engine=engine)


def test_council_engine_members_configuration(council_engine: CouncilEngine) -> None:
    members = council_engine.COUNCIL_MEMBERS
    assert len(members) == 5

    agent_ids = [m.agent_id for m in members]
    assert "LEGALISM" in agent_ids
    assert "TAOISM" in agent_ids
    assert "CONFUCIAN" in agent_ids
    assert "XUNZI" in agent_ids
    assert "SUNZI" in agent_ids


def test_council_deliberation_flow(council_engine: CouncilEngine) -> None:
    scenario = "Đối tác nợ 5 tỷ quá hạn 90 ngày và dọa đơn phương thanh lý hợp đồng hợp tác."
    result = council_engine.deliberate(scenario)

    assert result.session_id.startswith("COUNCIL-SESS-")
    assert result.scenario_text == scenario
    assert result.total_latency_ms > 0.0

    # 1. Check Stage 1: 5 Pitches
    assert len(result.pitches) == 5
    pitch_agents = [p.agent_id for p in result.pitches]
    assert "LEGALISM" in pitch_agents
    assert "TAOISM" in pitch_agents
    assert "CONFUCIAN" in pitch_agents
    assert "XUNZI" in pitch_agents
    assert "SUNZI" in pitch_agents

    for pitch in result.pitches:
        assert len(pitch.core_arguments) >= 2
        assert len(pitch.cited_unit_ids) >= 1
        assert len(pitch.risk_warning) > 0

    # 2. Check Stage 2: Cross-Debates
    assert len(result.cross_debates) >= 3
    for debate in result.cross_debates:
        assert debate.challenger_id != debate.target_id
        assert len(debate.critique) > 0
        assert len(debate.counter_recommendation) > 0

    # 3. Check Stage 3: Decision Matrix
    matrix = result.decision_matrix
    assert matrix is not None
    assert "Hội đồng Cố vấn thống nhất" in matrix.highest_consensus
    assert len(matrix.core_conflicts) >= 1
    assert "Phương án A" in matrix.plan_a_primary["name"]
    assert len(matrix.plan_a_primary["action_steps"]) == 3
    assert "Phương án B" in matrix.plan_b_fallback["name"]
    assert "Phương án C" in matrix.plan_c_containment["name"]
    assert len(matrix.critical_caveats) >= 1
    assert len(matrix.execution_directives) >= 1


def test_python_sdk_local_inprocess_mode() -> None:
    client = NhanThuatClient(mode="local")

    # 1. Analyze Scenario
    analysis = client.analyze_scenario("Công trình Nhà Bè chậm tiến độ do thiếu vật tư")
    assert analysis["status"] == "success"
    assert "action_script" in analysis
    assert len(analysis["matched_knowledge_units"]) >= 1

    # 2. Sparring Session
    spar_res = client.start_sparring_session("Đấu trí đàm phán hợp đồng", philosophy_lens="LEGALISM")
    assert spar_res["status"] == "success"
    session_id = spar_res["session"]["id"]

    turn_res = client.send_sparring_message(session_id, "Tôi muốn phạt nhà thầu 10% ngay lập tức.")
    assert turn_res["status"] == "success"
    assert "ĐỐI ĐÁP PHẢN BIỆN" in turn_res["response"]

    # 3. Council Deliberation
    council_res = client.deliberate_council("Nhân sự đình công đòi tăng đơn giá khoán")
    assert council_res["status"] == "success"
    assert len(council_res["deliberation"]["pitches"]) == 5

    # 4. List Case Studies
    cases = client.list_case_studies(domain="OPS")
    assert len(cases) >= 1

    # 5. Export Brief
    brief_md = client.export_executive_brief(
        title="Bản tham mưu hội đồng",
        situation_summary="Tranh chấp hợp đồng",
        philosophy_analysis="Áp dụng Pháp Gia",
        action_script={"step_1": "Biên bản", "step_2": "Hạn định", "step_3": "Plan B"},
        format="markdown",
    )
    assert "# BẢN THAM MƯU & CHỈ ĐẠO ĐIỀU HÀNH:" in brief_md


def test_enterprise_deployment_files_exist() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    # 1. Dockerfile
    dockerfile = repo_root / "Dockerfile"
    assert dockerfile.exists()
    df_content = dockerfile.read_text(encoding="utf-8")
    assert "python:3.11-slim" in df_content
    assert "appuser" in df_content
    assert "HEALTHCHECK" in df_content
    assert "EXPOSE 8000" in df_content

    # 2. docker-compose.yml
    compose_file = repo_root / "docker-compose.yml"
    assert compose_file.exists()
    compose_content = compose_file.read_text(encoding="utf-8")
    assert "nhan-thuat-core" in compose_content
    assert "8000:8000" in compose_content
    assert "knowledge" in compose_content

    # 3. DEPLOYMENT_GUIDE.md
    guide_file = repo_root / "docs" / "DEPLOYMENT_GUIDE.md"
    assert guide_file.exists()
    guide_content = guide_file.read_text(encoding="utf-8")
    assert "HƯỚNG DẪN TRIỂN KHAI DOANH NGHIỆP" in guide_content
    assert "Docker Compose" in guide_content
    assert "Systemd" in guide_content

    # 4. TypeScript SDK
    ts_index = repo_root / "sdk" / "typescript" / "src" / "index.ts"
    assert ts_index.exists()
    ts_content = ts_index.read_text(encoding="utf-8")
    assert "export class NhanThuatClient" in ts_content
    assert "deliberateCouncil" in ts_content
