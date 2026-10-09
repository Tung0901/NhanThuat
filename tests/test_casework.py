import io
import json
from unittest.mock import MagicMock

from nhan_thuat.casework import CaseFileRepository, CaseFileService, EpistemicClaim
from nhan_thuat.storage.db import DatabaseManager


def test_case_file_keeps_ownership_revision_and_stale_artifacts() -> None:
    db = DatabaseManager(db_path=":memory:")
    repository = CaseFileRepository(db)
    service = CaseFileService(repository)
    case = service.create(
        title="Supplier delay",
        situation_statement="Delivery is late by 48 hours.",
        objective="Protect the project schedule.",
        owner_user_id="user-1",
        org_id="org-1",
        known_facts=[EpistemicClaim("fact-1", "The contract has a deadline.", "observed_fact")],
    )
    assert repository.get(case.case_id, owner_user_id="user-2") is None
    assert repository.get(case.case_id, owner_user_id="user-1").revision == 1

    service.add_artifact(
        case,
        artifact_type="recommendation",
        source_module="war_room",
        module_version="1.0.0",
        payload_schema_version="recommendation.v1",
        input_hash="abc123",
        summary="Escalate with a written deadline.",
        payload={"step": 1},
        knowledge_refs=["NT-LAW-0005"],
        provenance={"epistemic_status": "recommendation"},
    )
    revised = service.revise(case, expected_revision=1, status="review")
    assert revised is not None
    assert revised.revision == 2
    assert repository.list_artifacts(case.case_id) == []
    assert len(repository.list_artifacts(case.case_id, include_stale=True)) == 1


def test_runtime_database_defaults_outside_knowledge(tmp_path, monkeypatch) -> None:
    runtime_path = tmp_path / "runtime" / "nhan_thuat.db"
    monkeypatch.setenv("NT_RUNTIME_DB_PATH", str(runtime_path))
    db = DatabaseManager()
    assert db.db_path == str(runtime_path)
    assert runtime_path.exists()


def test_case_file_api_requires_session_and_scopes_records(monkeypatch) -> None:
    from backend.app import main as app_main
    from backend.app.main import BusinessOSGatewayHandler

    isolated = DatabaseManager(db_path=":memory:")
    monkeypatch.setattr(app_main, "case_file_service", CaseFileService(CaseFileRepository(isolated)))
    session = app_main.auth_manager.create_session(
        {"name": "Test Owner", "role": "ADVISOR", "avatar": "T"}, "test-owner", custom_ttl=60
    )

    def handler_for(path: str, payload: dict | None = None, token: str = "") -> BusinessOSGatewayHandler:
        handler = BusinessOSGatewayHandler.__new__(BusinessOSGatewayHandler)
        handler.path = path
        body = json.dumps(payload or {}).encode("utf-8")
        handler.rfile = io.BytesIO(body)
        handler.headers = {"Content-Length": str(len(body)), "Authorization": f"Bearer {token}"}
        handler._send_json_response = MagicMock()
        return handler

    unauthorized = handler_for("/api/v1/case-files")
    unauthorized.do_GET()
    assert unauthorized._send_json_response.call_args.args[0] == 401

    creator = handler_for(
        "/api/v1/case-files",
        {"title": "Test case", "situation_statement": "A delay", "objective": "Recover time"},
        session["token"],
    )
    creator.do_POST()
    assert creator._send_json_response.call_args.args[0] == 201
    case_id = creator._send_json_response.call_args.args[1]["case_file"]["case_id"]

    reader = handler_for("/api/v1/case-files", token=session["token"])
    reader.do_GET()
    data = reader._send_json_response.call_args.args[1]
    assert data["count"] == 1
    assert data["case_files"][0]["case_id"] == case_id

    app_main.auth_manager.revoke_session(session["token"])
