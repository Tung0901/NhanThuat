from pathlib import Path

import pytest

from nhan_thuat.loader import load_document
from nhan_thuat.validator import validate_document, validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_epic_2_status_validates_after_freeze() -> None:
    schema = load_document(ROOT / "schemas" / "epic.schema.json")
    status = load_document(ROOT / "epics" / "epic-02-knowledge-architecture" / "status.yaml")

    assert status["status"] == "frozen"
    assert validate_document(status, schema) == []


def test_repository_validation_reports_naming_errors(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "schemas").mkdir()
    (repo / "knowledge" / "domains").mkdir(parents=True)
    (repo / "knowledge" / "units" / "laws").mkdir(parents=True)
    (repo / "epics").mkdir()

    for schema_name in (
        "domain.schema.json",
        "knowledge-unit.schema.json",
        "evidence.schema.json",
        "epic.schema.json",
    ):
        source = ROOT / "schemas" / schema_name
        target = repo / "schemas" / schema_name
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    for domain_path in (ROOT / "knowledge" / "domains").glob("*.yaml"):
        target = repo / "knowledge" / "domains" / domain_path.name
        target.write_text(domain_path.read_text(encoding="utf-8"), encoding="utf-8")

    unit = load_document(ROOT / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml")
    unit["id"] = "NT-TOOL-0001"
    bad_path = repo / "knowledge" / "units" / "laws" / "wrong-name.yaml"
    bad_path.write_text(_dump_minimal_yaml(unit), encoding="utf-8")

    issues = validate_repository(repo)

    assert any("does not match type" in issue.message for issue in issues)
    assert any("filename must contain record id" in issue.message for issue in issues)


def test_repository_validation_reports_frozen_register_drift(tmp_path: Path) -> None:
    repo = tmp_path
    (repo / "schemas").mkdir()
    (repo / "knowledge" / "domains").mkdir(parents=True)
    (repo / "knowledge" / "units").mkdir(parents=True)
    (repo / "epics" / "epic-00-bootstrap").mkdir(parents=True)
    (repo / "governance").mkdir()

    for schema_name in (
        "domain.schema.json",
        "knowledge-unit.schema.json",
        "evidence.schema.json",
        "epic.schema.json",
    ):
        source = ROOT / "schemas" / schema_name
        target = repo / "schemas" / schema_name
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    status = load_document(ROOT / "epics" / "epic-00-bootstrap" / "status.yaml")
    status["status"] = "ready_for_review"
    status_path = repo / "epics" / "epic-00-bootstrap" / "status.yaml"
    status_path.write_text(_dump_minimal_yaml(status), encoding="utf-8")

    register = {
        "version": "0.1.0",
        "entries": [
            {
                "id": "NT-EPIC-00",
                "type": "epic",
                "status": "frozen",
                "source": "epics/epic-00-bootstrap/status.yaml",
            }
        ],
    }
    (repo / "governance" / "frozen-register.yaml").write_text(
        _dump_minimal_yaml(register), encoding="utf-8"
    )

    issues = validate_repository(repo)

    assert any("frozen source is not frozen" in issue.message for issue in issues)


def _dump_minimal_yaml(data: dict[str, object]) -> str:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
