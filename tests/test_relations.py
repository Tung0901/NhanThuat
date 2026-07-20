from pathlib import Path

from nhan_thuat.validator import validate_repository

ROOT = Path(__file__).resolve().parents[1]


def test_no_broken_relations() -> None:
    issues = validate_repository(ROOT)
    assert not [issue for issue in issues if "broken relation" in issue.message]

