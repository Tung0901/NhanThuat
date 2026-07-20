from pathlib import Path

from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry
from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_epic3_laws_and_principles_are_registered() -> None:
    registry = load_registry(ROOT)

    assert {"NT-LAW-0002", "NT-LAW-0003"}.issubset(registry.units)
    assert {"NT-PRINCIPLE-0001", "NT-PRINCIPLE-0002", "NT-PRINCIPLE-0003"}.issubset(
        registry.units
    )
    assert len(registry.units_by_type("law")) >= 3
    assert len(registry.units_by_type("principle")) >= 3


def test_epic3_principles_depend_on_existing_laws() -> None:
    registry = load_registry(ROOT)

    assert registry.get_unit("NT-PRINCIPLE-0001").relations["depends_on"] == ("NT-LAW-0001",)
    assert registry.get_unit("NT-PRINCIPLE-0003").relations["depends_on"] == (
        "NT-LAW-0002",
        "NT-LAW-0003",
    )
    assert validate_repository(ROOT) == []


def test_epic3_status_is_frozen() -> None:
    status = load_document(ROOT / "epics" / "epic-03-laws-principles" / "status.yaml")

    assert status["epic_id"] == "NT-EPIC-03"
    assert status["status"] == "frozen"
    assert status["progress"] == 100
