"""Tests for SPEC-EXECUTIVE-CONSIGLIERE-ENGINE (Living Case Dossiers, Consigliere Mode, Kairos/ROI Cockpit, and Tactical Strike Audit)."""

from __future__ import annotations

import json
import threading
from http.server import HTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from backend.app.engine.cases_service import cases_service
from backend.app.engine.nhan_thuat_api import (
    diagnose_person_role_fit,
    diagnose_team_structural_fit,
    evaluate_sparring_tactical_audit,
    process_nhan_thuat_analysis,
)
from backend.app.main import BusinessOSGatewayHandler


@pytest.fixture(scope="module")
def live_server_url():
    server = HTTPServer(("127.0.0.1", 0), BusinessOSGatewayHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def _http_get_json(url: str) -> tuple[int, dict]:
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def _http_post_json(url: str, payload: dict) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def test_living_dossiers_catalog_completeness():
    """Verify all 30 Living Case Dossiers exist across the 3 core categories with full schema."""
    res = cases_service.list_dossiers()
    all_dossiers = res["dossiers"]
    assert len(all_dossiers) == 30

    categories = res["categories_summary"]
    assert categories == {
        "all": 30,
        "internal_power": 10,
        "field_crisis": 10,
        "high_stakes_negotiation": 10,
    }

    for idx in range(1, 31):
        case_id = f"NT-CASE-{idx:04d}"
        dossier = cases_service.get_dossier(case_id)
        assert dossier is not None, f"Missing dossier {case_id}"
        assert dossier["title"]
        assert dossier["power_map"]
        assert dossier["fatal_mistake"]
        assert isinstance(dossier["quantified_damage"], dict)
        assert "₫" in dossier["quantified_damage"]["financial_vnd"]
        assert len(dossier["surgical_strike"]) == 3
        assert dossier["kairos_rhythm"]
        assert len(dossier["cited_units"]) >= 2


def test_living_dossiers_filtering_and_scenario_matching():
    """Verify category filtering, keyword search, and scenario relevance matching."""
    field_cases = cases_service.list_dossiers(category="field_crisis")["dossiers"]
    assert len(field_cases) == 10
    assert all(c["category"] == "field_crisis" for c in field_cases)

    mep_search = cases_service.list_dossiers(query="MEP")["dossiers"]
    assert any(c["id"] == "NT-CASE-0012" for c in mep_search)

    matched = cases_service.match_relevant_dossiers(
        "Nhà thầu phụ MEP độc quyền tự ý ngưng lắp đặt đòi tăng giá 25% trước ngày nghiệm thu PCCC",
        top_k=2,
    )
    assert len(matched) == 2
    assert matched[0]["id"] == "NT-CASE-0012"


def test_http_living_dossiers_endpoints(live_server_url: str):
    """Verify GET /api/v1/cases/dossiers and GET /api/v1/cases/dossiers/<id>."""
    status, data = _http_get_json(f"{live_server_url}/api/v1/cases/dossiers")
    assert status == 200
    assert data["status"] == "success"
    assert data["total"] == 30
    assert len(data["dossiers"]) == 30

    status_cat, data_cat = _http_get_json(
        f"{live_server_url}/api/v1/cases/dossiers?category=high_stakes_negotiation"
    )
    assert status_cat == 200
    assert data_cat["total"] == 10

    status_one, data_one = _http_get_json(
        f"{live_server_url}/api/v1/cases/dossiers/NT-CASE-0001"
    )
    assert status_one == 200
    assert data_one["status"] == "success"
    assert data_one["dossier"]["id"] == "NT-CASE-0001"

    status_404, data_404 = _http_get_json(
        f"{live_server_url}/api/v1/cases/dossiers/NT-CASE-9999"
    )
    assert status_404 == 404
    assert data_404["status"] == "error"


def test_advisory_consigliere_mode_and_executive_metrics():
    """Verify process_nhan_thuat_analysis produces executive_metrics, consigliere_brief, and matched_cases."""
    resp = process_nhan_thuat_analysis(
        scenario_text=(
            "Phó Tổng Giám Đốc Kinh Doanh nắm 60% khách hàng VIP đang ngầm lập công ty sân sau "
            "và đe dọa rút toàn bộ đội ngũ nếu HĐQT cắt giảm hoa hồng."
        ),
        scenario_type_hint="leadership",
        consigliere_mode=True,
    )
    assert resp["consigliere_mode"] is True
    assert resp["executive_metrics"] is not None
    assert 0 <= resp["executive_metrics"]["kairos_score"] <= 100
    assert "₫" in resp["executive_metrics"]["cost_of_inaction_vnd"]
    assert resp["consigliere_brief"] is not None
    assert len(resp["consigliere_brief"]["three_step_checkmate"]) == 3
    assert resp["consigliere_brief"]["shadow_motive_dissection"]
    assert len(resp["matched_cases"]) >= 1
    assert resp["tactical_audit"] is not None


def test_diagnostics_fit_lab_executive_metrics():
    """Verify Person-Role Fit and Team Structural Fit return quantified executive_metrics."""
    person_resp = diagnose_person_role_fit(
        {
            "candidate_name": "Nguyễn Hoàng Long",
            "target_role": "Giám Đốc Vận Hành (COO)",
            "traits": ["Tự do sáng tạo", "Ngại xung đột trực diện"],
            "role_demands": ["Tuân thủ quy trình nghiêm ngặt", "Sa thải / Kỷ luật nhân sự"],
        }
    )
    assert person_resp["executive_metrics"] is not None
    assert "₫" in person_resp["executive_metrics"]["cost_of_inaction_vnd"]
    assert person_resp["executive_metrics"]["kairos_score"] > 0

    team_resp = diagnose_team_structural_fit(
        {
            "candidate_name": "Trần Đình Trí",
            "candidate_role": "Phó Tổng Giám Đốc",
            "candidate_traits": ["Quyết đoán nhanh", "Tham vọng quyền lực"],
            "team_name": "Ban Điều Hành",
            "team_mission": "Tăng trưởng doanh thu 150%",
            "existing_team_traits": ["Quyết đoán nhanh", "Tham vọng quyền lực"],
        }
    )
    assert team_resp["executive_metrics"] is not None
    assert "₫" in team_resp["executive_metrics"]["cost_of_inaction_vnd"]


def test_sparring_tactical_strike_analyzer():
    """Verify evaluate_sparring_tactical_audit distinguishes weak concessions from strong Legalist/Voss strikes."""
    weak_audit = evaluate_sparring_tactical_audit(
        "Mong anh thông cảm cố gắng giúp bên em giảm giá một chút nhé."
    )
    strong_audit = evaluate_sparring_tactical_audit(
        "Làm thế nào chúng ta có thể giải ngân khi biên bản nghiệm thu và bảo lãnh hợp đồng trước 17h00 vẫn chưa hoàn tất?"
    )
    assert strong_audit["dominance_score"] > weak_audit["dominance_score"]
    assert strong_audit["counter_strike_upgrade"]


def test_frontend_consigliere_and_dossiers_dom_elements():
    """Verify frontend/app.html contains all Executive Consigliere, Kairos Cockpit, Living Dossiers, and Reorganized Codex elements."""
    html = Path("frontend/app.html").read_text(encoding="utf-8")
    assert 'id="consigliere-mode-toggle"' in html
    assert 'id="consigliere-presets-bar"' in html
    assert 'id="codex-living-dossiers-block"' in html
    assert 'id="dossier-detail-modal"' in html
    assert "renderExecutiveMetricsHTML" in html
    assert "renderConsigliereBriefHTML" in html
    assert "renderClientTacticalAudit" in html
    assert 'id="codex-subnav-bar"' in html
    assert 'id="codex-panel-overview"' in html
    assert 'id="codex-panel-books"' in html
    assert 'id="codex-panel-iching"' in html
    assert 'id="codex-panel-dossiers"' in html
    assert 'id="codex-panel-catalog"' in html
    assert 'id="codex-global-search-input"' in html
    assert "switchCodexSubView" in html
    assert "handleCodexGlobalSearch" in html
