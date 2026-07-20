from pathlib import Path

import pytest

from nhan_thuat.evidence import build_traceability
from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_record_loads_into_registry_and_catalog() -> None:
    registry = load_registry(ROOT)
    evidence = registry.get_evidence("NT-EVIDENCE-0001")
    catalog = registry.catalog().to_mapping()

    assert evidence.source.kind == "internal_document"
    assert evidence.confidence.level == "supported"
    assert "NT-LAW-0004" in evidence.contextualizes
    assert "NT-EVIDENCE-0001" in catalog["evidence"]
    assert catalog["indexes"]["by_evidence_confidence"]["supported"] == ["NT-EVIDENCE-0001"]
    assert catalog["evidence_traceability"]["by_unit"]["NT-LAW-0004"]["contextualizes"] == [
        "NT-EVIDENCE-0001"
    ]


def test_evidence_traceability_is_bidirectional() -> None:
    registry = load_registry(ROOT)
    traceability = build_traceability(registry.evidence.values())

    assert traceability.by_evidence["NT-EVIDENCE-0001"]["contextualizes"]
    assert traceability.by_unit["NT-PRINCIPLE-0043"]["contextualizes"] == ["NT-EVIDENCE-0001"]


def test_missing_evidence_reference_fails_validation(tmp_path: Path) -> None:
    repo = _copy_minimal_repo(tmp_path)
    unit_path = repo / "knowledge" / "units" / "laws" / "NT-LAW-0001.yaml"
    unit = load_document(unit_path)
    unit["evidence"]["references"] = ["NT-EVIDENCE-9999"]
    unit_path.write_text(_dump_minimal_yaml(unit), encoding="utf-8")

    issues = validate_repository(repo)

    assert any("broken evidence reference: NT-EVIDENCE-9999" in issue.message for issue in issues)


def test_broken_evidence_target_fails_validation(tmp_path: Path) -> None:
    repo = _copy_minimal_repo(tmp_path)
    evidence_path = repo / "knowledge" / "evidence" / "NT-EVIDENCE-0001-batch-1-pilot-review.yaml"
    evidence = load_document(evidence_path)
    evidence["contextualizes"] = ["NT-LAW-9999"]
    evidence_path.write_text(_dump_minimal_yaml(evidence), encoding="utf-8")

    issues = validate_repository(repo)

    assert any(
        "broken evidence contextualizes reference: NT-LAW-9999" in issue.message
        for issue in issues
    )


def test_unknown_claim_citation_fails_validation(tmp_path: Path) -> None:
    repo = _copy_minimal_repo(tmp_path)
    evidence_path = repo / "knowledge" / "evidence" / "NT-EVIDENCE-0001-batch-1-pilot-review.yaml"
    evidence = load_document(evidence_path)
    evidence["claims"][0]["citations"] = ["CIT-999"]
    evidence_path.write_text(_dump_minimal_yaml(evidence), encoding="utf-8")

    issues = validate_repository(repo)

    assert any("claim references unknown citation: CIT-999" in issue.message for issue in issues)


def _copy_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path
    for directory in (
        "schemas",
        "knowledge/domains",
        "knowledge/units/laws",
        "knowledge/units/principles",
        "knowledge/evidence",
        "epics/epic-00-bootstrap",
        "governance",
    ):
        (repo / directory).mkdir(parents=True)
    for schema_name in (
        "domain.schema.json",
        "knowledge-unit.schema.json",
        "evidence.schema.json",
        "epic.schema.json",
    ):
        (repo / "schemas" / schema_name).write_text(
            (ROOT / "schemas" / schema_name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    for domain_path in (ROOT / "knowledge" / "domains").glob("*.yaml"):
        (repo / "knowledge" / "domains" / domain_path.name).write_text(
            domain_path.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    for unit_id in ("NT-LAW-0001", "NT-LAW-0004", "NT-PRINCIPLE-0043"):
        source = next((ROOT / "knowledge" / "units").rglob(f"{unit_id}*.yaml"))
        target_dir = repo / "knowledge" / "units" / source.parent.name
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_source = ROOT / "knowledge" / "evidence" / "NT-EVIDENCE-0001-batch-1-pilot-review.yaml"
    evidence = load_document(evidence_source)
    evidence["contextualizes"] = ["NT-LAW-0004", "NT-PRINCIPLE-0043"]
    (repo / "knowledge" / "evidence" / evidence_source.name).write_text(
        _dump_minimal_yaml(evidence),
        encoding="utf-8",
    )
    status = load_document(ROOT / "epics" / "epic-00-bootstrap" / "status.yaml")
    (repo / "epics" / "epic-00-bootstrap" / "status.yaml").write_text(
        _dump_minimal_yaml(status),
        encoding="utf-8",
    )
    return repo


def _dump_minimal_yaml(data: dict[str, object]) -> str:
    yaml = pytest.importorskip("yaml")
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
