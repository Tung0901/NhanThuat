from pathlib import Path

from nhan_thuat.factory import (
    FACTORY_STAGES,
    QUALITY_GATES,
    detect_duplicate_candidates,
    review_batch,
)
from nhan_thuat.loader import load_document
from nhan_thuat.registry import load_registry

ROOT = Path(__file__).resolve().parents[1]
BATCH_IDS = tuple(
    [f"NT-LAW-{number:04d}" for number in range(4, 24)]
    + [f"NT-PRINCIPLE-{number:04d}" for number in range(4, 44)]
)


def test_factory_stage_and_gate_contracts_are_stable() -> None:
    assert FACTORY_STAGES[0] == "intake"
    assert FACTORY_STAGES[-1] == "freeze"
    assert "duplicates" in QUALITY_GATES
    assert "governance" in QUALITY_GATES


def test_factory_review_marks_batch_freeze_eligible_with_human_approval() -> None:
    report = review_batch(
        ROOT,
        "NT-BATCH-001",
        BATCH_IDS,
        human_approved=True,
        accepted_fixes=["EPIC 3 count assertions broadened for approved library growth."],
    )

    assert report.status == "frozen"
    assert report.freeze_eligible is True
    assert len(report.units_reviewed) == 60
    assert report.duplicate_candidates == ()
    assert report.conflict_candidates == ()
    assert {gate.status for gate in report.quality_gates} == {"pass"}


def test_factory_requires_human_approval_for_freeze_eligibility() -> None:
    report = review_batch(ROOT, "NT-BATCH-001", BATCH_IDS, human_approved=False)

    assert report.status == "ready_for_review"
    assert report.freeze_eligible is False
    assert any(gate.gate == "governance" and gate.status == "fail" for gate in report.quality_gates)


def test_factory_reports_exact_duplicate_candidates() -> None:
    registry = load_registry(ROOT)
    left = registry.get_unit("NT-LAW-0004")
    right = registry.get_unit("NT-LAW-0005")
    duplicate = type(right)(
        **{
            **right.__dict__,
            "id": "NT-LAW-9999",
            "title": left.title,
            "raw": {**right.raw, "id": "NT-LAW-9999", "title": left.title},
        }
    )

    findings = detect_duplicate_candidates((left, duplicate))

    assert findings
    assert findings[0].kind == "exact_duplicate"
    assert findings[0].severity == "blocker"


def test_pilot_review_artifacts_are_machine_and_human_readable() -> None:
    manifest = load_document(ROOT / "knowledge" / "foundation" / "batch-01" / "manifest.yaml")
    report = load_document(ROOT / "knowledge" / "foundation" / "batch-01" / "review-report.yaml")
    human_report = ROOT / "docs" / "reviews" / "KNOWLEDGE-FOUNDATION-BATCH-01-PILOT-REVIEW.md"

    assert manifest["lifecycle"]["current_state"] == "frozen"
    assert report["units_reviewed"]["total"] == 60
    assert report["freeze_eligibility"]["eligible"] is True
    assert human_report.exists()
