from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]
MOTIVATION_LAWS = {f"NT-LAW-{number:04d}" for number in range(29, 34)}
MOTIVATION_PRINCIPLES = {f"NT-PRINCIPLE-{number:04d}" for number in range(52, 60)}
MOTIVATION_PATTERNS = {f"NT-MODEL-{number:04d}" for number in range(4, 7)}
MOTIVATION_ANTI_PATTERNS = {f"NT-ANTI-PATTERN-{number:04d}" for number in range(5, 9)}
MOTIVATION_UNITS = (
    MOTIVATION_LAWS
    | MOTIVATION_PRINCIPLES
    | MOTIVATION_PATTERNS
    | MOTIVATION_ANTI_PATTERNS
)


def test_motivation_status_is_frozen() -> None:
    status = load_document(ROOT / "docs" / "domains" / "motivation" / "status.yaml")

    assert status["domain_area_id"] == "NT-DA-0002"
    assert status["slug"] == "motivation"
    assert status["status"] == "frozen"
    assert status["previous_status"] == "ready_for_review"
    assert status["approved_by"] == "Product Owner"
    assert status["blockers"] == []
    assert status["unit_counts"] == {
        "laws": 5,
        "principles": 8,
        "models": 3,
        "anti_patterns": 4,
    }


def test_motivation_units_are_registered_and_scoped() -> None:
    registry = load_registry(ROOT)

    assert MOTIVATION_UNITS.issubset(registry.units)
    for unit_id in MOTIVATION_UNITS:
        unit = registry.get_unit(unit_id)
        assert unit.status == "frozen"
        assert unit.primary_domain == "tu-than"
        assert unit.tags
        assert unit.evidence.level == "provisional"
        assert unit.evidence.references == ()


def test_motivation_unit_types_match_expected_counts() -> None:
    registry = load_registry(ROOT)

    assert {registry.get_unit(unit_id).type for unit_id in MOTIVATION_LAWS} == {"law"}
    assert {registry.get_unit(unit_id).type for unit_id in MOTIVATION_PRINCIPLES} == {
        "principle"
    }
    assert {registry.get_unit(unit_id).type for unit_id in MOTIVATION_PATTERNS} == {"model"}
    assert {registry.get_unit(unit_id).type for unit_id in MOTIVATION_ANTI_PATTERNS} == {
        "anti-pattern"
    }


def test_motivation_relations_validate() -> None:
    assert validate_repository(ROOT) == []


def test_motivation_docs_and_evidence_placeholders_exist() -> None:
    docs = ROOT / "docs" / "domains" / "motivation"

    assert (docs / "ARCHITECTURE.md").exists()
    assert (docs / "CONCEPT-MAP.md").exists()
    assert (docs / "GLOSSARY.md").exists()
    assert (docs / "DEPENDENCIES.md").exists()
    assert (docs / "REVIEW-REPORT.md").exists()

    evidence = load_document(docs / "evidence-placeholders.yaml")
    assert evidence["evidence_posture"]["default_level"] == "provisional"
    assert evidence["evidence_posture"]["external_references_fabricated"] is False


def test_motivation_frozen_inventory_is_explicit() -> None:
    status = load_document(ROOT / "docs" / "domains" / "motivation" / "status.yaml")
    docs = ROOT / "docs" / "domains" / "motivation"

    assert set(status["members"]["laws"]) == MOTIVATION_LAWS
    assert set(status["members"]["principles"]) == MOTIVATION_PRINCIPLES
    assert set(status["members"]["models"]) == MOTIVATION_PATTERNS
    assert set(status["members"]["anti_patterns"]) == MOTIVATION_ANTI_PATTERNS
    assert set(status["artifacts"]) == {
        f"docs/domains/motivation/{path.name}" for path in docs.iterdir() if path.is_file()
    }
