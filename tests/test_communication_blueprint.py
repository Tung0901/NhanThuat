from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_communication_status_is_ready_for_review() -> None:
    status = load_document(ROOT / "docs" / "domains" / "communication" / "status.yaml")

    assert status["domain_area_id"] == "NT-DA-0008"
    assert status["slug"] == "communication"
    assert status["status"] in ("ready_for_review", "frozen")
    assert status["previous_status"] in ("review", "ready_for_review")
    assert status["unit_counts"] == {
        "laws": 2,
        "principles": 3,
        "models": 1,
        "anti_patterns": 2,
    }


def test_communication_blueprint_files_exist() -> None:
    docs = ROOT / "docs" / "domains" / "communication"

    assert (docs / "ARCHITECTURE.md").exists()
    assert (docs / "CONCEPT-MAP.md").exists()
    assert (docs / "GLOSSARY.md").exists()
    assert (docs / "DEPENDENCIES.md").exists()
    assert (docs / "evidence-placeholders.yaml").exists()


def test_communication_relations_validate() -> None:
    assert validate_repository(ROOT) == []
