"""Tests for Phase 3 & Phase 4 Knowledge Unit Recovery, Evidence Truthfulness, and Pilot Batch."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.knowledge_content_pilot_tool import (
    BANNED_BOILERPLATE_PHRASES,
    PILOT_UNIT_SPECS,
    SOURCE_CLASS_TAGS,
    apply_content_without_metadata_mutation,
    audit_evidence_truthfulness,
    audit_pilot_unit_quality,
    execute_controlled_recovery,
    is_placeholder_reference,
)

ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

EXPECTED_PILOT_RELEVANCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "NT-LAW-3201": ("Plassmann", "Thaler", "Sutherland", "Mental accounting"),
    "NT-LAW-4102": ("Kahneman", "Tversky", "Prospect Theory", "Walasek"),
    "NT-LAW-2101": ("Weick", "Mann Gulch", "Perrow", "Tôn Vũ"),
    "NT-PRINCIPLE-4101": ("Sweller", "Cognitive load", "Cowan"),
    "NT-PRINCIPLE-0063": ("Edmondson", "French", "Raven", "Psychological safety"),
    "NT-MODEL-2101": ("Bundy", "Coombs", "Crisis"),
    "NT-MODEL-2201": ("French", "Raven", "Podsakoff", "Nhị Bính"),
    "NT-PHENOMENON-4101": ("Veblen", "Bagwell", "Bernheim", "Conspicuous"),
    "NT-PHENOMENON-4102": ("Huber", "Payne", "Puto", "Frederick", "Ariely"),
    "NT-PHENOMENON-4103": ("Hasher", "Goldstein", "Toppino", "Fazio"),
    "NT-ANTI-PATTERN-0012": ("Khurana", "House", "Howell", "Charismatic"),
    "NT-ANTI-PATTERN-0013": ("Kelman", "Deci", "Ryan", "Compliance"),
}


def _load_all_units() -> dict[str, dict]:
    units: dict[str, dict] = {}
    for path in sorted((ROOT / "knowledge" / "units").rglob("*.yaml")):
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        units[str(data["id"])] = data
    return units


def test_evidence_truthfulness_and_no_placeholder_inflation() -> None:
    """Verify no unit claims supported/strong evidence with only EV-REQ-* placeholders or empty refs."""
    units = _load_all_units()
    assert len(units) == 379

    violations: list[str] = []
    for unit_id, data in units.items():
        violations.extend(audit_evidence_truthfulness(data))
        ev = data.get("evidence") or {}
        refs = [str(r).strip() for r in (ev.get("references") or []) if str(r).strip()]
        if "EV-REQ-0001-01" in refs and len(refs) == 1:
            assert ev.get("level") == "provisional", (
                f"{unit_id} has placeholder EV-REQ-0001-01 and must not be marked {ev.get('level')}"
            )

    assert violations == [], f"Evidence truthfulness violations found: {violations}"


def test_zero_mass_boilerplate_across_repository() -> None:
    """Verify all mass-generated template sentences have been removed across all 379 units."""
    units = _load_all_units()
    template_phrases = BANNED_BOILERPLATE_PHRASES[:6]

    offending: list[tuple[str, str]] = []
    for unit_id, data in units.items():
        content = str(data.get("content") or "")
        lower_content = content.lower()
        for phrase in template_phrases:
            if phrase.lower() in lower_content:
                offending.append((unit_id, phrase))

    assert offending == [], f"Found mass boilerplate phrases in units: {offending}"


def test_pilot_batch_covers_five_types_and_uncertainty_standards() -> None:
    """Verify the 12-unit pilot batch covers law/principle/model/phenomenon/anti-pattern and passes quality checks."""
    units = _load_all_units()
    pilot_ids = set(PILOT_UNIT_SPECS.keys())
    assert 10 <= len(pilot_ids) <= 15

    pilot_types = {units[uid]["type"] for uid in pilot_ids}
    assert pilot_types == {"law", "principle", "model", "phenomenon", "anti-pattern"}

    for uid in pilot_ids:
        unit_data = units[uid]
        issues = audit_pilot_unit_quality(unit_data)
        assert issues == [], f"Pilot unit {uid} failed quality audit: {issues}"

        # Verify direct topical relevance of references (not just len >= 1)
        joined_refs = " | ".join(str(r) for r in unit_data["evidence"]["references"])
        expected_keywords = EXPECTED_PILOT_RELEVANCE_KEYWORDS[uid]
        for kw in expected_keywords:
            assert kw.lower() in joined_refs.lower(), (
                f"Pilot unit {uid} references do not mention expected relevant source '{kw}'"
            )

        # Verify multiple source classifications are distinguished
        present_tags = [tag for tag in SOURCE_CLASS_TAGS if tag in joined_refs]
        assert len(present_tags) >= 2, (
            f"Pilot unit {uid} must distinguish at least 2 source categories, found {present_tags}"
        )


def test_pilot_generator_tool_dry_run_and_metadata_preservation(tmp_path: Path) -> None:
    """Verify generator tool supports --dry-run, manifest output, and never mutates metadata automatically."""
    sample_unit = {
        "id": "NT-LAW-3201",
        "type": "law",
        "status": "draft",
        "version": "1.0.0",
        "evidence": {"level": "provisional", "references": ["EV-REQ-0001-01"]},
        "content": "Old content",
    }
    updated = apply_content_without_metadata_mutation(sample_unit, "New bespoke content")
    assert updated["status"] == "draft"
    assert updated["version"] == "1.0.0"
    assert updated["evidence"] == {"level": "provisional", "references": ["EV-REQ-0001-01"]}
    assert updated["content"] == "New bespoke content"
    assert is_placeholder_reference("EV-REQ-0001-01") is True
    assert is_placeholder_reference("Kahneman (1979)") is False

    # Verify anti-boilerplate detector rejects banned phrases and placeholder inflation
    bad_unit = {
        "id": "NT-LAW-9999",
        "evidence": {"level": "supported", "references": ["EV-REQ-0001-01"]},
        "content": "Trong một phiên họp quyết định nhân sự, đây là chân lý bất biến và duy nhất.",
    }
    bad_issues = audit_pilot_unit_quality(bad_unit)
    assert any("Trong một phiên họp quyết định nhân sự" in i for i in bad_issues)
    assert any("chân lý bất biến" in i for i in bad_issues)
    assert any("duy nhất" in i for i in bad_issues)
    assert any("relies solely on placeholder" in i for i in bad_issues)

    # Verify dry-run manifest execution does not modify any files when already converged
    manifest_out = tmp_path / "dry_run_manifest.json"
    summary = execute_controlled_recovery(repo_root=ROOT, dry_run=True, manifest_path=manifest_out)
    assert manifest_out.exists()
    assert summary["total_target_units"] == 352
    assert summary["frozen_count"] == 346
    assert summary["draft_count"] == 6
    assert summary["files_updated_count"] == 0


def test_change_request_and_352_inventory_ready_for_review() -> None:
    """Verify Change Request dossier and 352-unit inventory exist and stop at ready_for_review."""
    cr_path = ROOT / "governance" / "change-requests" / "CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md"
    assert cr_path.exists()
    cr_text = cr_path.read_text(encoding="utf-8")
    assert "`ready_for_review`" in cr_text
    assert "346" in cr_text
    assert "EV-REQ-0001-01" in cr_text

    inv_path = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    assert inv_path.exists()
    inv_data = json.loads(inv_path.read_text(encoding="utf-8"))
    assert inv_data["total_target_units"] == 352
    assert inv_data["frozen_count"] == 346
    assert inv_data["draft_count"] == 6
    assert len(inv_data["inventory"]) == 352

