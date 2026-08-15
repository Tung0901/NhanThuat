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


def test_repository_validation_accepts_valid_domain_freeze(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review")
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert issues == []


def test_repository_validation_reports_duplicate_domain_freeze_entries(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review")
    register = _frozen_domain_register()
    register["entries"].append(register["entries"][0].copy())
    (repo / "governance" / "frozen-register.yaml").write_text(
        _dump_minimal_yaml(register), encoding="utf-8"
    )

    issues = validate_repository(repo)

    assert any("duplicate frozen entry: domain_area NT-DA-0001" in issue.message for issue in issues)
    assert any("duplicate frozen source: docs/domains/human-nature/status.yaml" in issue.message for issue in issues)


def test_repository_validation_reports_unregistered_frozen_domain(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review")

    issues = validate_repository(repo)

    assert any("frozen domain is not registered: docs/domains/human-nature/status.yaml" in issue.message for issue in issues)


def test_repository_validation_requires_domain_registry_for_domain_status(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    (repo / "knowledge" / "domain-registry.yaml").unlink()
    _write_domain_status(repo, status="ready_for_review")

    issues = validate_repository(repo)

    assert any("domain status validation requires domain registry" in issue.message for issue in issues)


def test_repository_validation_reports_invalid_domain_transition(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="draft")
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("invalid domain lifecycle transition: draft -> frozen" in issue.message for issue in issues)


def test_repository_validation_reports_self_domain_transition(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="frozen")
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("invalid domain lifecycle transition: frozen -> frozen" in issue.message for issue in issues)


def test_repository_validation_preserves_non_domain_frozen_register_compatibility(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="ready_for_review")
    _copy_epic_statuses(repo)
    register = load_document(ROOT / "governance" / "frozen-register.yaml")
    register["entries"] = [
        entry for entry in register["entries"] if entry.get("type") != "domain_area"
    ]
    (repo / "governance" / "frozen-register.yaml").write_text(
        _dump_minimal_yaml(register),
        encoding="utf-8",
    )

    issues = validate_repository(repo)

    assert issues == []


def test_repository_validation_reports_frozen_domain_metadata_errors(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review", member_status="review")
    _write_frozen_domain_register(repo, approved_by="Someone Else")

    issues = validate_repository(repo)

    assert any("frozen domain approved_by does not match source" in issue.message for issue in issues)
    assert any("frozen domain member is not frozen: NT-LAW-0001" in issue.message for issue in issues)


def test_repository_validation_requires_domain_status_metadata(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(
        repo,
        status="frozen",
        previous_status="ready_for_review",
        include_name=False,
        include_blockers=False,
    )
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("domain status must declare name" in issue.message for issue in issues)
    assert any("domain status must declare blockers list" in issue.message for issue in issues)


def test_repository_validation_reports_frozen_domain_member_type_mismatch(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review", member_group="principles")
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("frozen domain member type mismatch: principles NT-LAW-0001" in issue.message for issue in issues)


def test_repository_validation_reports_frozen_domain_count_mismatch(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review", unit_counts={"laws": 2})
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("unit_counts does not match members for laws" in issue.message for issue in issues)


def test_repository_validation_reports_unknown_frozen_domain_member_group(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(repo, status="frozen", previous_status="ready_for_review", member_group="unknowns")
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("unknown frozen domain member group: unknowns" in issue.message for issue in issues)


def test_repository_validation_reports_frozen_domain_artifact_errors(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    _write_domain_status(
        repo,
        status="frozen",
        previous_status="ready_for_review",
        artifacts=[
            "docs/domains/human-nature/status.yaml",
            "docs/domains/human-nature/status.yaml",
            "docs/domains/other/status.yaml",
        ],
    )
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert any("frozen domain artifact is outside domain directory" in issue.message for issue in issues)
    assert any("frozen domain artifacts must be unique" in issue.message for issue in issues)
    assert any("frozen domain artifacts must match domain file inventory" in issue.message for issue in issues)


def test_repository_validation_reports_domain_area_not_in_registry(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    unit = load_document(ROOT / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml")
    unit["domain_area"] = "NT-DA-9999"
    (repo / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml").write_text(
        _dump_minimal_yaml(unit), encoding="utf-8"
    )

    issues = validate_repository(repo)

    assert any("domain_area not in domain registry: NT-DA-9999" in issue.message for issue in issues)


def test_repository_validation_accepts_frozen_domain_with_phenomena_members(tmp_path: Path) -> None:
    repo = _minimal_validation_repo(tmp_path)
    phenomenon = load_document(ROOT / "knowledge" / "units" / "phenomena" / "NT-PHENOMENON-3001.yaml")
    phenomenon["status"] = "frozen"
    phenomenon.pop("domain_area", None)
    (repo / "knowledge" / "units" / "phenomena").mkdir(parents=True, exist_ok=True)
    (repo / "knowledge" / "units" / "phenomena" / "NT-PHENOMENON-3001.yaml").write_text(
        _dump_minimal_yaml(phenomenon), encoding="utf-8"
    )
    domain_status = {
        "domain_area_id": "NT-DA-0001",
        "slug": "human-nature",
        "name": "Human Nature",
        "status": "frozen",
        "previous_status": "ready_for_review",
        "progress": 100,
        "approved_by": "Product Owner",
        "frozen_at": "2026-07-21",
        "blockers": [],
        "unit_counts": {"phenomena": 1},
        "members": {"phenomena": ["NT-PHENOMENON-3001"]},
        "artifacts": ["docs/domains/human-nature/status.yaml"],
    }
    (repo / "docs" / "domains" / "human-nature" / "status.yaml").write_text(
        _dump_minimal_yaml(domain_status), encoding="utf-8"
    )
    _write_frozen_domain_register(repo)

    issues = validate_repository(repo)

    assert issues == []


def _dump_minimal_yaml(data: dict[str, object]) -> str:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def _minimal_validation_repo(tmp_path: Path) -> Path:
    repo = tmp_path
    (repo / "schemas").mkdir()
    (repo / "knowledge" / "domains").mkdir(parents=True)
    (repo / "knowledge" / "units" / "laws").mkdir(parents=True)
    (repo / "knowledge").mkdir(exist_ok=True)
    (repo / "docs" / "domains" / "human-nature").mkdir(parents=True)
    (repo / "epics").mkdir()
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

    for domain_path in (ROOT / "knowledge" / "domains").glob("*.yaml"):
        target = repo / "knowledge" / "domains" / domain_path.name
        target.write_text(domain_path.read_text(encoding="utf-8"), encoding="utf-8")

    registry = {
        "version": "0.1.0",
        "domains": [{"id": "NT-DA-0001", "slug": "human-nature"}],
    }
    (repo / "knowledge" / "domain-registry.yaml").write_text(
        _dump_minimal_yaml(registry), encoding="utf-8"
    )
    return repo


def _copy_epic_statuses(repo: Path) -> None:
    for epic_status in (ROOT / "epics").glob("*/status.yaml"):
        target = repo / "epics" / epic_status.parent.name / "status.yaml"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(epic_status.read_text(encoding="utf-8"), encoding="utf-8")


def _write_domain_status(
    repo: Path,
    *,
    status: str,
    previous_status: str | None = None,
    member_status: str = "frozen",
    member_group: str = "laws",
    unit_counts: dict[str, int] | None = None,
    artifacts: list[str] | None = None,
    include_name: bool = True,
    blockers: list[str] | None = None,
    include_blockers: bool = True,
) -> None:
    unit = load_document(ROOT / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml")
    unit["status"] = member_status
    (repo / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml").write_text(
        _dump_minimal_yaml(unit), encoding="utf-8"
    )
    domain_status = {
        "domain_area_id": "NT-DA-0001",
        "slug": "human-nature",
        "status": status,
        "progress": 100,
        "unit_counts": unit_counts if unit_counts is not None else {member_group: 1},
        "last_reviewed_at": "2026-07-21",
    }
    if include_name:
        domain_status["name"] = "Human Nature"
    if include_blockers:
        domain_status["blockers"] = blockers or []
    if previous_status is not None:
        domain_status["previous_status"] = previous_status
    if status == "frozen":
        domain_status["approved_by"] = "Product Owner"
        domain_status["frozen_at"] = "2026-07-21"
        domain_status["members"] = {member_group: ["NT-LAW-0001"]}
        domain_status["artifacts"] = artifacts if artifacts is not None else ["docs/domains/human-nature/status.yaml"]
    (repo / "docs" / "domains" / "human-nature" / "status.yaml").write_text(
        _dump_minimal_yaml(domain_status), encoding="utf-8"
    )


def _frozen_domain_register(
    *,
    approved_by: str = "Product Owner",
) -> dict[str, object]:
    return {
        "version": "0.1.0",
        "entries": [
            {
                "id": "NT-DA-0001",
                "type": "domain_area",
                "title": "Human Nature",
                "status": "frozen",
                "frozen_at": "2026-07-21",
                "approved_by": approved_by,
                "source": "docs/domains/human-nature/status.yaml",
                "rationale": "Product Owner approved Human Nature domain freeze.",
            }
        ],
    }


def _write_frozen_domain_register(
    repo: Path,
    *,
    approved_by: str = "Product Owner",
) -> None:
    (repo / "governance" / "frozen-register.yaml").write_text(
        _dump_minimal_yaml(_frozen_domain_register(approved_by=approved_by)),
        encoding="utf-8",
    )
