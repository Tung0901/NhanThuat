"""
Test suite for BusinessOS & NhanThuat Web Dashboard API Endpoints (Milestone M16).
"""

from backend.app.engine.nhan_thuat_api import process_nhan_thuat_analysis


def test_process_nhan_thuat_analysis_operational_scenario() -> None:
    scenario = "Công trình ở Nhà Bè bị chậm tiến độ do Nhà cung cấp giao vật tư trễ"
    res = process_nhan_thuat_analysis(scenario)

    assert res["status"] == "success"
    assert res["is_ambiguous"] is False
    assert res["philosophy_routing"]["primary_philosophy"] == "LEGALISM"
    assert len(res["matched_knowledge_units"]) == 3
    assert "matched_custom_docs" in res
    assert "position_analysis" in res["action_script"]
    assert "step_1_anchor" in res["action_script"]
    assert "step_2_deadline_consequence" in res["action_script"]
    assert "step_3_way_out_plan_b" in res["action_script"]
    assert "draft_official_communication" in res["action_script"]
    assert "financial_and_operational_directives" in res["action_script"]
    assert len(res["action_script"]["financial_and_operational_directives"]) >= 1
    assert res["correlation_id"].startswith("CORR-WEB-")


def test_process_nhan_thuat_analysis_ambiguous_scenario() -> None:
    scenario = "Công trình ở Nhà Bè"
    res = process_nhan_thuat_analysis(scenario)

    assert res["status"] == "success"
    assert res["is_ambiguous"] is True
    assert "AMBIGUOUS CONTEXT WARNING" in res["ambiguity_warning"]


def test_process_nhan_thuat_analysis_rhetoric_scenario() -> None:
    scenario = "Khách hàng chê báo giá đắt hơn đối thủ"
    res = process_nhan_thuat_analysis(scenario)

    assert res["status"] == "success"
    assert res["philosophy_routing"]["primary_philosophy"] == "RHETORIC"
    assert "Reframing" in res["action_script"]["step_1_anchor"]["title"]


def test_knowledge_unit_export_json() -> None:
    from backend.app.main import export_unit
    from nhan_thuat.knowledge_engine import KnowledgeEngine

    res = export_unit(KnowledgeEngine(), "NT-LAW-0001", fmt="json")

    assert res["status"] == "success"
    assert res["payload"]["format"] == "json"
    assert res["payload"]["unit"]["id"] == "NT-LAW-0001"
    assert "title" in res["payload"]["unit"]
    assert "primary_domain" in res["payload"]["unit"]


def test_knowledge_unit_export_markdown_shape() -> None:
    from backend.app.main import export_unit
    from nhan_thuat.knowledge_engine import KnowledgeEngine

    res = export_unit(KnowledgeEngine(), "NT-LAW-0001", fmt="markdown")

    assert res["status"] == "success"
    assert isinstance(res["payload"], str)
    assert res["payload"].startswith("# ")
    assert "ID: NT-LAW-0001" in res["payload"]
    assert "Type: law" in res["payload"]


def test_knowledge_unit_export_unknown_returns_error() -> None:
    from backend.app.main import export_unit
    from nhan_thuat.knowledge_engine import KnowledgeEngine

    res = export_unit(KnowledgeEngine(), "NT-LAW-9999", fmt="json")

    assert res["status"] == "error"
    assert res["code"] == 404
