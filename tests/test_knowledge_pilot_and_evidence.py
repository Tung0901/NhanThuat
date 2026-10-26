"""Tests for Knowledge Unit Recovery, Evidence Truthfulness, Pilot Governance, and Tooling."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.knowledge_content_pilot_tool import (
    DEFAULT_BASE_REF,
    DRAFT_PILOT_IDS,
    FROZEN_PILOT_IDS,
    REQUIRED_PILOT_SECTIONS,
    SOURCE_CLASS_TAGS,
    ExclusiveTransactionLock,
    audit_unit_absolutism,
    audit_unit_evidence_classification,
    execute_apply_frozen,
    execute_audit,
    execute_rollback,
    is_placeholder_reference,
    load_base_commit_files,
    parse_change_request_metadata,
    recover_from_pending_journals,
    resolve_full_commit_hash,
    sha256_bytes,
    validate_proposed_unit_schema,
    verify_promotion_worktree,
)

ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

EXPECTED_PILOT_RELEVANCE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "NT-LAW-3201": ("Plassmann", "Thaler", "Sutherland"),
    "NT-LAW-4102": ("Kahneman", "Tversky", "Prospect Theory", "Walasek"),
    "NT-LAW-2101": ("Weick", "Mann Gulch", "Perrow"),
    "NT-PRINCIPLE-4101": ("Sweller", "Cognitive load", "Cowan"),
    "NT-PRINCIPLE-0063": ("Edmondson", "French", "Raven"),
    "NT-MODEL-2101": ("Bundy", "Coombs", "Crisis"),
    "NT-MODEL-2201": ("French", "Raven", "Podsakoff"),
    "NT-PHENOMENON-4101": ("Veblen", "Bagwell", "Bernheim"),
    "NT-PHENOMENON-4102": ("Huber", "Payne", "Puto", "Frederick"),
    "NT-PHENOMENON-4103": ("Hasher", "Goldstein", "Toppino"),
    "NT-ANTI-PATTERN-0012": ("Khurana", "House", "Howell"),
    "NT-ANTI-PATTERN-0013": ("Kelman", "Deci", "Ryan"),
}


def _load_unit_by_id(repo_root: Path, unit_id: str) -> dict:
    matches = list((repo_root / "knowledge" / "units").rglob(f"{unit_id}*.yaml"))
    assert matches, f"Unit {unit_id} not found in knowledge/units"
    return yaml.load(matches[0].read_text(encoding="utf-8"), Loader=YAML_LOADER)


def test_six_draft_canonical_pilots_quality_and_truthfulness() -> None:
    """Verify that all 6 Draft pilot units in canonical knowledge/units meet strict standards."""
    assert len(DRAFT_PILOT_IDS) == 6

    for draft_id in DRAFT_PILOT_IDS:
        data = _load_unit_by_id(ROOT, draft_id)
        assert data.get("status") == "draft", f"Draft pilot {draft_id} must have status 'draft'"

        # Anti-absolutism & anti-boilerplate audit
        abs_issues = audit_unit_absolutism(data, draft_id)
        assert abs_issues == [], f"Draft pilot {draft_id} contains absolutist or boilerplate phrasing: {abs_issues}"

        # Standardized evidence classification
        ev_issues = audit_unit_evidence_classification(data, draft_id, is_pilot=True)
        assert ev_issues == [], f"Draft pilot {draft_id} failed evidence audit: {ev_issues}"

        # Required 5 sections in content
        content = str(data.get("content") or "")
        for sec in REQUIRED_PILOT_SECTIONS:
            assert sec.lower() in content.lower(), f"Draft pilot {draft_id} missing section '{sec}'"

        # Topic-relevant citations
        refs = [str(r) for r in data["evidence"]["references"]]
        joined_refs = " | ".join(refs)
        for kw in EXPECTED_PILOT_RELEVANCE_KEYWORDS[draft_id]:
            assert kw.lower() in joined_refs.lower(), (
                f"Draft pilot {draft_id} missing expected citation keyword '{kw}'"
            )

        # Standard 7-tier classification tags present
        present_tags = [tag for tag in SOURCE_CLASS_TAGS if any(r.startswith(tag) for r in refs)]
        assert len(present_tags) >= 2, f"Draft pilot {draft_id} must use at least 2 distinct classification tiers"


def test_six_frozen_proposal_artifacts_structure_and_quality() -> None:
    """Verify that the 6 Frozen pilot proposals meet governance requirements and proposed_version > current_version."""
    assert len(FROZEN_PILOT_IDS) == 6
    proposals_dir = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units"
    assert proposals_dir.exists(), f"Proposals directory missing: {proposals_dir}"

    for frozen_id in FROZEN_PILOT_IDS:
        matches = list(proposals_dir.glob(f"{frozen_id}*.yaml"))
        assert matches, f"Proposal artifact for {frozen_id} missing in {proposals_dir}"
        prop_path = matches[0]
        prop = yaml.load(prop_path.read_text(encoding="utf-8"), Loader=YAML_LOADER)

        # Required governance fields
        assert prop.get("unit_id") == frozen_id
        assert prop.get("status") == "ready_for_review", "Proposal status must be 'ready_for_review'"
        assert prop.get("base_commit") == "27a34bc"
        assert prop.get("canonical_path")
        assert prop.get("current_version")
        assert prop.get("proposed_version")
        assert prop.get("evidence_before")
        assert prop.get("evidence_proposed")
        assert prop.get("rationale")
        assert prop.get("impact")
        assert prop.get("source_classification")

        # Mandatory semver progression: proposed_version > current_version
        cur_ver = prop.get("current_version")
        prop_ver = prop.get("proposed_version")
        c_parts = tuple(map(int, cur_ver.split(".")))
        p_parts = tuple(map(int, prop_ver.split(".")))
        assert p_parts > c_parts, (
            f"Proposal {frozen_id} proposed_version '{prop_ver}' must be strictly > current_version '{cur_ver}'"
        )

        # Proposed unit data audit
        proposed_unit = prop.get("proposed_unit") or {}
        assert proposed_unit.get("status") == "frozen"
        assert proposed_unit.get("version") == prop_ver, (
            f"Proposal {frozen_id} proposed_unit.version must match proposed_version"
        )

        # Special check for NT-MODEL-2101
        if frozen_id == "NT-MODEL-2101":
            assert proposed_unit["evidence"]["level"] == "provisional", (
                "NT-MODEL-2101 is an editorial model and its evidence level must strictly remain 'provisional'"
            )

        abs_issues = audit_unit_absolutism(proposed_unit, prop_path)
        assert abs_issues == [], f"Proposal {frozen_id} contains absolutist phrasing: {abs_issues}"

        ev_issues = audit_unit_evidence_classification(proposed_unit, prop_path, is_pilot=True)
        assert ev_issues == [], f"Proposal {frozen_id} failed evidence classification: {ev_issues}"

        # Topic-relevant citations
        refs = [str(r) for r in proposed_unit["evidence"]["references"]]
        joined_refs = " | ".join(refs)
        for kw in EXPECTED_PILOT_RELEVANCE_KEYWORDS[frozen_id]:
            assert kw.lower() in joined_refs.lower(), (
                f"Proposal {frozen_id} missing expected citation keyword '{kw}'"
            )


def test_canonical_frozen_units_unmodified_vs_base() -> None:
    """Verify that canonical Frozen units in knowledge/units remain 100% identical to base commit 27a34bc."""
    base_files = load_base_commit_files(ROOT, "27a34bc")
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((ROOT / "knowledge" / "units").rglob(f"{frozen_id}*.yaml"))
        assert matches, f"Canonical unit {frozen_id} not found"
        p = matches[0]
        rel = p.relative_to(ROOT).as_posix()
        assert rel in base_files, f"{rel} not in base_files"

        base_hash = sha256_bytes(base_files[rel])
        cur_hash = sha256_bytes(p.read_bytes())
        assert cur_hash == base_hash, (
            f"Governance violation: canonical frozen unit {rel} was modified without approved CR!"
        )


def test_manifest_target_paths_exist_and_use_slugs() -> None:
    """Verify that every target_path in the manifest exists on disk and proposal paths include slugs."""
    manifest_path = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    assert manifest_path.exists(), f"Manifest file missing: {manifest_path}"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Base commit must be full 40-character commit hash
    full_hash = resolve_full_commit_hash(ROOT, "27a34bc")
    assert manifest["base_commit"] == full_hash
    assert len(manifest["base_commit"]) == 40

    missing_paths: list[str] = []
    proposal_count = 0
    for entry in manifest["entries"]:
        tpath = ROOT / entry["target_path"]
        if not tpath.exists():
            missing_paths.append(entry["target_path"])
        if entry["target_type"] == "proposal":
            proposal_count += 1
            assert entry.get("sha256_proposal"), f"Proposal entry {entry['id']} missing sha256_proposal"
            assert len(entry["sha256_proposal"]) == 64
            assert len(entry["sha256_base"]) == 64

    assert missing_paths == [], f"Found non-existent target paths in manifest: {missing_paths}"
    assert proposal_count == 6, f"Expected exactly 6 proposal entries, found {proposal_count}"


def test_audit_frozen_restore_177_artifact_integrity() -> None:
    """Verify that the immutable audit artifact for 177 Frozen units exists, is non-empty, and verifies clean restore."""
    audit_path = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "audit_frozen_restore_177_manifest.json"
    assert audit_path.exists(), f"Audit artifact missing: {audit_path}"
    data = json.loads(audit_path.read_text(encoding="utf-8"))

    assert data["total_frozen_units_restored"] == 177
    assert len(data["entries"]) == 177, "Audit artifact must not be empty"
    assert data["immutable"] is True
    assert len(data["base_commit"]) == 40

    # Verify permanent git evidence anchor
    assert data.get("pre_restore_git_tag") == "evidence/pre-restore-177-frozen"
    assert len(data.get("pre_restore_commit", "")) == 40

    for entry in data["entries"]:
        assert entry["path"].endswith(".yaml")
        assert len(entry["pre_restore_sha256"]) == 64
        assert len(entry["base_sha256"]) == 64
        assert entry["base_sha256"] == entry["current_canonical_sha256"], (
            f"Unit {entry['id']} base SHA != current canonical SHA"
        )
        # Canonical file on disk must match base SHA
        canon_path = ROOT / entry["path"]
        assert canon_path.exists()
        disk_sha = sha256_bytes(canon_path.read_bytes())
        assert disk_sha == entry["base_sha256"], f"File on disk {entry['path']} does not match base SHA"


def test_structural_cr_parsing_and_no_prose_substring() -> None:
    """Verify Change Request is parsed strictly by YAML frontmatter without prose matching."""
    cr_path = ROOT / "governance" / "change-requests" / "CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md"
    meta = parse_change_request_metadata(cr_path)
    assert meta["id"] == "CR-2026-10-19-KNOWLEDGE-CONTENT-V1"
    assert meta["schema_version"] == "1.0.0"
    assert meta["status"] == "ready_for_review"
    assert meta["approval"]["approval_id"] is None
    assert meta["approval"]["approved_by"] is None
    assert meta["approval"]["approved_at"] is None
    assert meta["approval"]["approved_scope"] is None
    assert meta["approval"]["approved_base_commit_sha"] is None
    assert meta["approval"]["approved_review_commit_sha"] is None
    assert meta["approval"]["approved_manifest_sha256"] is None


def test_generator_fail_closed_and_governance_safety(tmp_path: Path) -> None:
    """Verify that --apply-frozen and --rollback fail closed under improper governance states."""
    manifest_path = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    assert manifest_path.exists()

    # 1. --apply-frozen without manifest fails closed
    ret = execute_apply_frozen(ROOT, po_approval_id="PO-TEST-001", manifest_path=None)
    assert ret == 1

    # 2. --apply-frozen without PO approval id fails closed
    ret = execute_apply_frozen(ROOT, po_approval_id=None, manifest_path=manifest_path)
    assert ret == 1

    # 3. --apply-frozen with empty string PO approval id fails closed
    ret = execute_apply_frozen(ROOT, po_approval_id="   ", manifest_path=manifest_path)
    assert ret == 1

    # 4. Mandatory reproduction test: Passing --po-approval-id "Product Owner" on CR in ready_for_review MUST exit 1
    ret = execute_apply_frozen(ROOT, po_approval_id="Product Owner", manifest_path=manifest_path)
    assert ret == 1

    # 5. Manifest missing sha256_base or sha256_proposal must exit 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Missing sha256_base
    m_no_base = dict(manifest)
    m_no_base["entries"] = [dict(e) for e in manifest["entries"]]
    for e in m_no_base["entries"]:
        if e["id"] in FROZEN_PILOT_IDS:
            e["sha256_base"] = ""  # empty / invalid
            break
    p_no_base = tmp_path / "manifest_no_base.json"
    p_no_base.write_text(json.dumps(m_no_base), encoding="utf-8")
    assert execute_apply_frozen(ROOT, po_approval_id="PO-TEST", manifest_path=p_no_base) == 1

    # Missing sha256_proposal
    m_no_prop = dict(manifest)
    m_no_prop["entries"] = [dict(e) for e in manifest["entries"]]
    for e in m_no_prop["entries"]:
        if e["id"] in FROZEN_PILOT_IDS:
            del e["sha256_proposal"]  # missing
            break
    p_no_prop = tmp_path / "manifest_no_prop.json"
    p_no_prop.write_text(json.dumps(m_no_prop), encoding="utf-8")
    assert execute_apply_frozen(ROOT, po_approval_id="PO-TEST", manifest_path=p_no_prop) == 1

    # Invalid non-64 hex hash
    m_bad_hex = dict(manifest)
    m_bad_hex["entries"] = [dict(e) for e in manifest["entries"]]
    for e in m_bad_hex["entries"]:
        if e["id"] in FROZEN_PILOT_IDS:
            e["sha256_proposal"] = "abc123not64hex"
            break
    p_bad_hex = tmp_path / "manifest_bad_hex.json"
    p_bad_hex.write_text(json.dumps(m_bad_hex), encoding="utf-8")
    assert execute_apply_frozen(ROOT, po_approval_id="PO-TEST", manifest_path=p_bad_hex) == 1

    # 6. --rollback without manifest fails closed
    ret = execute_rollback(ROOT, manifest_path=None)
    assert ret == 1

    # 7. Dry-run rollback with valid manifest succeeds and does not modify disk
    ret = execute_rollback(ROOT, manifest_path=manifest_path, dry_run=True)
    assert ret == 0

    # 8. Manifest hash integrity test: tampered manifest fails
    tampered_manifest = dict(manifest)
    tampered_manifest["entries"] = list(manifest["entries"])
    tampered_manifest["entries"][0] = dict(tampered_manifest["entries"][0])
    tampered_manifest["entries"][0]["sha256_base"] = "0" * 64
    tampered_path = tmp_path / "tampered_manifest.json"
    tampered_path.write_text(json.dumps(tampered_manifest), encoding="utf-8")
    assert execute_rollback(ROOT, manifest_path=tampered_path) == 1


def make_approved_cr_fixture(
    dest_path: Path,
    approval_id: str = "PO-APPROVED-2026-10-21-FIX-001",
    base_commit_sha: str = "27a34bcd840713df1817517066b4cf1a9b1623a3",
    review_commit_sha: str = "27a34bcd840713df1817517066b4cf1a9b1623a3",
    manifest_sha: str = "0" * 64,
    scope: str = "pilot_batch_6_frozen",
    schema_version: str = "1.0.0",
) -> Path:
    cr_content = f"""---
id: CR-2026-10-19-KNOWLEDGE-CONTENT-V1
schema_version: {schema_version}
status: APPROVED_BY_PRODUCT_OWNER
created_at: '2026-10-19'
approval:
  approval_id: {approval_id}
  approved_by: "Product Owner"
  approved_at: '2026-10-21T11:00:00Z'
  approved_scope: "{scope}"
  approved_base_commit_sha: "{base_commit_sha}"
  approved_review_commit_sha: "{review_commit_sha}"
  approved_manifest_sha256: "{manifest_sha}"
---

# Formal Approval Document
This document is approved by Product Owner.
"""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(cr_content, encoding="utf-8")
    return dest_path


def create_isolated_fixture_repository(tmp_path: Path) -> tuple[Path, str, str, Path, Path]:
    """Create a fully isolated temporary Git repository fixture for write and fault tests.

    Returns (repo_dir, base_commit_hash, review_commit_hash, manifest_path, approved_cr_path).
    Never touches D:\\NhanThuat.
    """
    repo_dir = tmp_path / "test_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # 1. Create directory structure
    for sub in ("laws", "models", "principles", "anti-patterns"):
        (repo_dir / "knowledge" / "units" / sub).mkdir(parents=True, exist_ok=True)
    (repo_dir / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units").mkdir(parents=True, exist_ok=True)
    (repo_dir / "governance" / "change-requests").mkdir(parents=True, exist_ok=True)
    (repo_dir / "schemas").mkdir(parents=True, exist_ok=True)

    # 2. Copy schema
    (repo_dir / "schemas" / "knowledge-unit.schema.json").write_bytes(
        (ROOT / "schemas" / "knowledge-unit.schema.json").read_bytes()
    )

    # 3. Copy canonical 6 Frozen units from base
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((ROOT / "knowledge" / "units").rglob(f"{frozen_id}*.yaml"))
        assert len(matches) == 1
        src = matches[0]
        rel = src.relative_to(ROOT)
        dst = repo_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    # 4. Initialize isolated Git repository and create Commit 1: Base Commit
    subprocess.run(["git", "init"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test Runner"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@runner.local"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Base commit for isolated test repo"], cwd=str(repo_dir), check=True, capture_output=True)

    base_commit_hash = resolve_full_commit_hash(repo_dir, "HEAD")

    # 5. Copy 6 proposal files
    proposals_dir = repo_dir / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units"
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units").glob(f"{frozen_id}*.yaml"))
        assert len(matches) == 1
        src = matches[0]
        rel = src.relative_to(ROOT)
        dst = repo_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    # 6. Generate manifest in repo_dir
    manifest_entries: list[dict[str, Any]] = []
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((repo_dir / "knowledge" / "units").rglob(f"{frozen_id}*.yaml"))
        cf = matches[0]
        canon_rel = cf.relative_to(repo_dir).as_posix()
        sha_b = sha256_bytes(cf.read_bytes())

        prop_matches = list(proposals_dir.glob(f"{frozen_id}*.yaml"))
        pf = prop_matches[0]
        prop_rel = pf.relative_to(repo_dir).as_posix()
        sha_p = sha256_bytes(pf.read_bytes())

        manifest_entries.append({
            "id": frozen_id,
            "canonical_path": canon_rel,
            "governance_status": "frozen",
            "target_type": "proposal",
            "target_path": prop_rel,
            "sha256_base": sha_b,
            "sha256_current": sha_b,
            "sha256_proposal": sha_p,
            "action": "pilot_proposal_ready_for_review",
            "applied_to_canonical": False,
        })

    manifest_data = {
        "snapshot_id": "MANIFEST-TEST-ISOLATED",
        "generated_at": "2026-10-22T00:00:00Z",
        "base_commit": base_commit_hash,
        "base_commit_short": base_commit_hash[:7],
        "total_target_units": len(manifest_entries),
        "frozen_count": len(manifest_entries),
        "draft_count": 0,
        "pilot_count": len(manifest_entries),
        "entries": manifest_entries,
    }
    manifest_path = repo_dir / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    manifest_raw = json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n"
    manifest_path.write_text(manifest_raw, encoding="utf-8")
    manifest_sha = sha256_bytes(manifest_path.read_bytes())

    # 7. Commit proposals and manifest to Git as Commit 2: Review Commit
    subprocess.run(["git", "add", "specs"], cwd=str(repo_dir), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Review commit with proposals and manifest"], cwd=str(repo_dir), check=True, capture_output=True)
    review_commit_hash = resolve_full_commit_hash(repo_dir, "HEAD")

    assert review_commit_hash != base_commit_hash

    # 8. Materialize the approved review commit as a real detached linked worktree.
    worktree_dir = tmp_path / "promotion_worktree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree_dir), review_commit_hash],
        cwd=str(repo_dir),
        check=True,
        capture_output=True,
    )

    # 9. Create approved Change Request fixture inside the promotion worktree ONLY.
    approved_id = "PO-APPROVED-TEST-ISOLATED"
    approved_cr_path = worktree_dir / "governance" / "change-requests" / "CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md"
    make_approved_cr_fixture(
        approved_cr_path,
        approval_id=approved_id,
        base_commit_sha=base_commit_hash,
        review_commit_sha=review_commit_hash,
        manifest_sha=manifest_sha,
    )

    manifest_path = worktree_dir / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    return worktree_dir, base_commit_hash, review_commit_hash, manifest_path, approved_cr_path


def test_positive_path_with_valid_approved_cr_fixture(tmp_path: Path) -> None:
    """Verify that when a valid approved Change Request fixture is present, apply-frozen dry-run succeeds."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    # In dry-run mode with valid approved CR fixture, execute_apply_frozen must succeed (exit code 0)
    ret = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=True,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
    )
    assert ret == 0, f"Expected execute_apply_frozen dry-run to succeed on valid approved CR fixture, got {ret}"


def test_production_repo_guard_blocks_live_apply(tmp_path: Path) -> None:
    """Verify that hard production guard blocks any dry_run=False execution without isolated_worktree=True."""
    manifest_path = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "inventory_352_units.json"
    approved_id = "PO-APPROVED-TEST-GUARD"

    # dry_run=False without isolated_worktree=True MUST return 1 and not touch disk
    ret = execute_apply_frozen(
        ROOT,
        po_approval_id=approved_id,
        manifest_path=manifest_path,
        dry_run=False,
        isolated_worktree=False,
    )
    assert ret == 1, "Production guard failed to block live apply without isolated_worktree=True!"

    worktree_ok, _ = verify_promotion_worktree(ROOT, resolve_full_commit_hash(ROOT, "HEAD"))
    assert worktree_ok is False, "Primary repository must not be accepted as a promotion worktree"


def test_approved_manifest_sha256_tampered_fails(tmp_path: Path) -> None:
    """Verify that tampering approved_manifest_sha256 by even one character halts apply-frozen."""
    test_repo, base_hash, review_hash, manifest_path, _ = create_isolated_fixture_repository(tmp_path)
    real_sha = sha256_bytes(manifest_path.read_bytes())
    # Flip the last character
    bad_sha = real_sha[:-1] + ("0" if real_sha[-1] != "0" else "1")

    approved_id = "PO-TEST-TAMPER-MANIFEST-SHA"
    approved_cr = test_repo / "governance" / "change-requests" / "CR-TAMPER-MANIFEST.md"
    make_approved_cr_fixture(
        approved_cr,
        approval_id=approved_id,
        base_commit_sha=base_hash,
        review_commit_sha=review_hash,
        manifest_sha=bad_sha,
    )

    ret = execute_apply_frozen(
        test_repo,
        po_approval_id=approved_id,
        base_ref=base_hash,
        manifest_path=manifest_path,
        dry_run=True,
        cr_path_override=approved_cr,
    )
    assert ret == 1, "Expected apply-frozen to fail when approved_manifest_sha256 is tampered."


def test_proposal_changed_after_approval_fails(tmp_path: Path) -> None:
    """Verify that modifying a proposal artifact after approval halts execution."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    # Modify proposal file on disk after review commit was created
    prop_matches = list((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units").glob("NT-LAW-2101*.yaml"))
    assert prop_matches
    p_orig = prop_matches[0]
    p_orig.write_text(p_orig.read_text(encoding="utf-8") + "\n# tampered post-approval\n", encoding="utf-8")

    ret = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        manifest_path=manifest_path,
        dry_run=True,
        cr_path_override=approved_cr,
    )
    assert ret == 1, "Expected apply-frozen to fail when proposal content does not match approved manifest hash."


def test_manifest_regenerated_after_approval_fails(tmp_path: Path) -> None:
    """Verify that regenerating manifest after approval invalidates approved_manifest_sha256."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    # Simulate manifest regeneration (e.g. timestamp updated)
    m_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    m_data["generated_at"] = "2026-10-25T12:00:00Z"
    regen_manifest_path = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "regenerated_manifest.json"
    regen_manifest_path.write_text(json.dumps(m_data, indent=2) + "\n", encoding="utf-8")

    # The CR was approved for original manifest, but user runs with regenerated manifest
    ret = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        manifest_path=regen_manifest_path,
        dry_run=True,
        cr_path_override=approved_cr,
    )
    assert ret == 1, "Expected apply-frozen to fail when manifest is regenerated after CR approval."


def test_invalid_and_injected_paths_fail_under_approved_cr(tmp_path: Path) -> None:
    """Verify that path traversal, absolute paths, non-canonical destinations, and symlinks fail."""
    test_repo, base_hash, review_hash, manifest_path, _ = create_isolated_fixture_repository(tmp_path)
    base_m_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Test 1: canonical_path="README.md"
    m1 = json.loads(json.dumps(base_m_data))
    for e in m1["entries"]:
        if e["id"] == "NT-LAW-2101":
            e["canonical_path"] = "README.md"
            break
    p1 = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m1_readme.json"
    p1.write_text(json.dumps(m1), encoding="utf-8")
    cr1 = test_repo / "governance" / "change-requests" / "CR1.md"
    make_approved_cr_fixture(cr1, approval_id="PO-TEST-README", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p1.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-README", base_ref=base_hash, manifest_path=p1, dry_run=True, cr_path_override=cr1) == 1

    # Test 2: absolute canonical path
    m2 = json.loads(json.dumps(base_m_data))
    for e in m2["entries"]:
        if e["id"] == "NT-LAW-2101":
            e["canonical_path"] = "C:/absolute/path/file.yaml" if os.name == "nt" else "/tmp/absolute/file.yaml"
            break
    p2 = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m2_abs.json"
    p2.write_text(json.dumps(m2), encoding="utf-8")
    cr2 = test_repo / "governance" / "change-requests" / "CR2.md"
    make_approved_cr_fixture(cr2, approval_id="PO-TEST-ABS", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p2.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-ABS", base_ref=base_hash, manifest_path=p2, dry_run=True, cr_path_override=cr2) == 1

    # Test 3: directory traversal ".."
    m3 = json.loads(json.dumps(base_m_data))
    for e in m3["entries"]:
        if e["id"] == "NT-LAW-2101":
            e["canonical_path"] = "knowledge/units/../../escape.yaml"
            break
    p3 = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m3_dotdot.json"
    p3.write_text(json.dumps(m3), encoding="utf-8")
    cr3 = test_repo / "governance" / "change-requests" / "CR3.md"
    make_approved_cr_fixture(cr3, approval_id="PO-TEST-DOTDOT", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p3.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-DOTDOT", base_ref=base_hash, manifest_path=p3, dry_run=True, cr_path_override=cr3) == 1

    # Test 4: duplicate destination canonical paths
    m4 = json.loads(json.dumps(base_m_data))
    law_entry = next(e for e in m4["entries"] if e["id"] == "NT-LAW-2101")
    for e in m4["entries"]:
        if e["id"] == "NT-MODEL-2101":
            e["canonical_path"] = law_entry["canonical_path"]
            break
    p4 = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m4_dup.json"
    p4.write_text(json.dumps(m4), encoding="utf-8")
    cr4 = test_repo / "governance" / "change-requests" / "CR4.md"
    make_approved_cr_fixture(cr4, approval_id="PO-TEST-DUP", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p4.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-DUP", base_ref=base_hash, manifest_path=p4, dry_run=True, cr_path_override=cr4) == 1


def test_missing_hash_fails_after_cr_approved(tmp_path: Path) -> None:
    """Verify that missing sha256_base or sha256_proposal halts execution even after CR approval passes."""
    test_repo, base_hash, review_hash, manifest_path, _ = create_isolated_fixture_repository(tmp_path)
    base_m_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    # Missing sha256_base
    m_no_base = json.loads(json.dumps(base_m_data))
    for e in m_no_base["entries"]:
        if e["id"] == "NT-LAW-2101":
            del e["sha256_base"]
            break
    p_no_base = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m_no_base_approved.json"
    p_no_base.write_text(json.dumps(m_no_base), encoding="utf-8")
    cr_no_base = test_repo / "governance" / "change-requests" / "CR_NO_BASE.md"
    make_approved_cr_fixture(cr_no_base, approval_id="PO-NO-BASE", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p_no_base.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-NO-BASE", base_ref=base_hash, manifest_path=p_no_base, dry_run=True, cr_path_override=cr_no_base) == 1

    # Missing sha256_proposal
    m_no_prop = json.loads(json.dumps(base_m_data))
    for e in m_no_prop["entries"]:
        if e["id"] == "NT-LAW-2101":
            del e["sha256_proposal"]
            break
    p_no_prop = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "m_no_prop_approved.json"
    p_no_prop.write_text(json.dumps(m_no_prop), encoding="utf-8")
    cr_no_prop = test_repo / "governance" / "change-requests" / "CR_NO_PROP.md"
    make_approved_cr_fixture(cr_no_prop, approval_id="PO-NO-PROP", base_commit_sha=base_hash, review_commit_sha=review_hash, manifest_sha=sha256_bytes(p_no_prop.read_bytes()))
    assert execute_apply_frozen(test_repo, po_approval_id="PO-NO-PROP", base_ref=base_hash, manifest_path=p_no_prop, dry_run=True, cr_path_override=cr_no_prop) == 1


def test_invalid_type_and_schema_fail_under_approved_cr() -> None:
    """Verify that proposals with missing/invalid type or schema violations fail validation."""
    proposals_dir = ROOT / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units"
    p_orig = next(iter(proposals_dir.glob("NT-LAW-2101*.yaml")))
    p_data = yaml.load(p_orig.read_text(encoding="utf-8"), Loader=YAML_LOADER)

    # 1. Missing type
    bad_data = yaml.load(yaml.dump(p_data), Loader=YAML_LOADER)
    del bad_data["proposed_unit"]["type"]
    issues = validate_proposed_unit_schema(bad_data["proposed_unit"], "knowledge/units/laws/NT-LAW-2101.yaml")
    assert any("type" in str(iss).lower() for iss in issues)

    # 2. Invalid type enum
    bad_data2 = yaml.load(yaml.dump(p_data), Loader=YAML_LOADER)
    bad_data2["proposed_unit"]["type"] = "invalid_not_a_type"
    issues2 = validate_proposed_unit_schema(bad_data2["proposed_unit"], "knowledge/units/laws/NT-LAW-2101.yaml")
    assert any("type" in str(iss).lower() for iss in issues2)

    # 3. ID and type prefix mismatch (NT-LAW-2101 with type: model)
    bad_data3 = yaml.load(yaml.dump(p_data), Loader=YAML_LOADER)
    bad_data3["proposed_unit"]["type"] = "model"
    issues3 = validate_proposed_unit_schema(bad_data3["proposed_unit"], "knowledge/units/laws/NT-LAW-2101.yaml")
    assert any("mismatch" in str(iss).lower() for iss in issues3)


def test_isolated_live_apply_success(tmp_path: Path) -> None:
    """Verify that execute_apply_frozen dry_run=False succeeds cleanly inside an isolated fixture repository."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    ret = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=False,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
        isolated_worktree=True,
    )
    assert ret == 0, f"Expected successful apply in isolated fixture repo, got {ret}"

    # Verify that all 6 units in test_repo have been replaced and match proposed versions
    for fid in FROZEN_PILOT_IDS:
        cf = next(iter((test_repo / "knowledge" / "units").rglob(f"{fid}*.yaml")))
        data = yaml.load(cf.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        assert data["status"] == "frozen"
        assert tuple(map(int, data["version"].split("."))) >= (1, 0, 0)

    # Verify no journal left behind on success
    journals = list((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert journals == []


def test_isolated_fault_injections_before_and_after_replace(tmp_path: Path) -> None:
    """Verify that failures before/after each replace in isolated repo restore all 6 canonicals."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    # Record initial hashes in test_repo
    initial_shas: dict[str, str] = {}
    for fid in FROZEN_PILOT_IDS:
        cf = next(iter((test_repo / "knowledge" / "units").rglob(f"{fid}*.yaml")))
        initial_shas[fid] = sha256_bytes(cf.read_bytes())

    # Test failure before and after replace for each of the 6 files (indices 0..5)
    for idx in range(6):
        # Fail before replace
        ret_before = execute_apply_frozen(
            test_repo,
            po_approval_id="PO-APPROVED-TEST-ISOLATED",
            base_ref=base_hash,
            dry_run=False,
            manifest_path=manifest_path,
            cr_path_override=approved_cr,
            isolated_worktree=True,
            _fault_injection={"fail_before_replace_idx": idx},
        )
        assert ret_before == 1

        for fid in FROZEN_PILOT_IDS:
            cf = next(iter((test_repo / "knowledge" / "units").rglob(f"{fid}*.yaml")))
            assert sha256_bytes(cf.read_bytes()) == initial_shas[fid]

        # Fail after replace
        ret_after = execute_apply_frozen(
            test_repo,
            po_approval_id="PO-APPROVED-TEST-ISOLATED",
            base_ref=base_hash,
            dry_run=False,
            manifest_path=manifest_path,
            cr_path_override=approved_cr,
            isolated_worktree=True,
            _fault_injection={"fail_after_replace_idx": idx},
        )
        assert ret_after == 1

        for fid in FROZEN_PILOT_IDS:
            cf = next(iter((test_repo / "knowledge" / "units").rglob(f"{fid}*.yaml")))
            assert sha256_bytes(cf.read_bytes()) == initial_shas[fid]


def test_isolated_fault_injections_journal_restore_hash_cleanup(tmp_path: Path) -> None:
    """Verify failure during journal write, restore, hash verification (ROLLBACK_FAILED), and cleanup."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    # 1. Fail at journal write
    ret_jw = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=False,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
        isolated_worktree=True,
        _fault_injection={"fail_at_journal_write": True},
    )
    assert ret_jw == 1

    # 2. Fail at restore during rollback -> MUST enter ROLLBACK_FAILED and keep assets
    ret_res = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=False,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
        isolated_worktree=True,
        _fault_injection={"fail_after_replace_idx": 2, "fail_at_restore_idx": 0},
    )
    assert ret_res == 1
    # Check journal is ROLLBACK_FAILED
    j_files = list((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert len(j_files) == 1
    j_data = json.loads(j_files[0].read_text(encoding="utf-8"))
    assert j_data["state"] == "ROLLBACK_FAILED"
    # Check backup files are preserved
    bak_files = list((test_repo / "knowledge" / "units").rglob("*.bak_apply_*"))
    assert len(bak_files) > 0

    # Test crash recovery recovering from ROLLBACK_FAILED
    ok, msg = recover_from_pending_journals(test_repo)
    assert ok is True, f"Crash recovery failed: {msg}"
    assert not list((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))

    # 3. Fail at hash verification during rollback -> MUST enter ROLLBACK_FAILED and keep assets
    ret_hash = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=False,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
        isolated_worktree=True,
        _fault_injection={"fail_after_replace_idx": 1, "fail_at_hash_verification": True},
    )
    assert ret_hash == 1
    j_files = list((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert len(j_files) == 1
    assert json.loads(j_files[0].read_text(encoding="utf-8"))["state"] == "ROLLBACK_FAILED"

    # Recover again
    ok, _ = recover_from_pending_journals(test_repo)
    assert ok is True


def test_isolated_crash_recovery(tmp_path: Path) -> None:
    """Verify idempotent recovery for STAGED, REPLACING, ROLLING_BACK, and ROLLBACK_FAILED journals."""
    test_repo, _base_hash, _review_hash, _manifest_path, _approved_cr = create_isolated_fixture_repository(tmp_path)
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"

    # 1. STAGED crash recovery
    j_staged = j_dir / ".apply_journal_99991.json"
    tmp_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml.tmp_apply_99991"
    bak_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml.bak_apply_99991"
    canon_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml"
    j_staged.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(tmp_file),
            "backup_path": str(bak_file),
            "sha256_base": sha256_bytes(canon_file.read_bytes()),
            "status": "staged",
        }],
    }), encoding="utf-8")
    tmp_file.write_text("temp", encoding="utf-8")

    ok, _msg = recover_from_pending_journals(test_repo)
    assert ok is True
    assert not j_staged.exists()
    assert not tmp_file.exists()


def test_malicious_journal_path_escape_and_traversal(tmp_path: Path) -> None:
    """Verify that malicious journals containing path traversals, escapes, and bad names fail confinement."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path)
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    journal_pid = 99990
    j_path = j_dir / f".apply_journal_{journal_pid}.json"

    outside_victim = tmp_path / "outside_victim.txt"
    outside_victim.write_text("critical external data", encoding="utf-8")

    # 1. Directory traversal in canonical_path
    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "../../outside_victim.txt",
            "staging_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.tmp_apply_{journal_pid}"),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "staged",
        }],
    }), encoding="utf-8")
    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False
    assert "confinement" in err.lower() or "traversal" in err.lower() or "canonical" in err.lower()
    assert outside_victim.exists()

    # 2. Absolute path outside repo in canonical_path
    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": str(outside_victim),
            "staging_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.tmp_apply_{journal_pid}"),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "staged",
        }],
    }), encoding="utf-8")
    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False
    assert outside_victim.exists()

    # 3. Path traversal in staging_path attempting to delete outside file
    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(outside_victim),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "staged",
        }],
    }), encoding="utf-8")
    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False
    assert outside_victim.exists()

    # 4. Invalid staging naming convention (missing .tmp_apply_ or .tmp_rollback_)
    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(test_repo / "knowledge/units/laws/arbitrary_file.txt"),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "staged",
        }],
    }), encoding="utf-8")
    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False

    # 5. Null byte in path
    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml\x00.evil",
            "staging_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.tmp_apply_{journal_pid}"),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-2101.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "staged",
        }],
    }), encoding="utf-8")
    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False

    j_path.unlink(missing_ok=True)


def test_relative_journal_paths_are_rejected_independently_of_cwd(tmp_path: Path, monkeypatch) -> None:
    """A relative auxiliary path must never be re-resolved against the process working directory."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path / "fixture")
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    journal_pid = 99988
    j_path = j_dir / f".apply_journal_{journal_pid}.json"
    canon_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml"
    relative_staging = f"knowledge/units/laws/{canon_file.name}.tmp_apply_{journal_pid}"
    relative_backup = f"knowledge/units/laws/{canon_file.name}.bak_apply_{journal_pid}"

    unrelated_cwd = tmp_path / "unrelated_cwd"
    victim = unrelated_cwd / relative_staging
    victim.parent.mkdir(parents=True)
    victim.write_text("must survive", encoding="utf-8")

    j_path.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": relative_staging,
            "backup_path": relative_backup,
            "sha256_base": sha256_bytes(canon_file.read_bytes()),
            "status": "staged",
        }],
    }), encoding="utf-8")

    monkeypatch.chdir(unrelated_cwd)
    ok, message = recover_from_pending_journals(test_repo)
    assert ok is False
    assert "absolute" in message.lower() or "confinement" in message.lower()
    assert victim.read_text(encoding="utf-8") == "must survive"
    assert j_path.exists()


def test_missing_canonical_fails_closed(tmp_path: Path) -> None:
    """Verify that recovery fails closed when a canonical file is missing from disk."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path)
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    journal_pid = 99989
    j_path = j_dir / f".apply_journal_{journal_pid}.json"

    j_path.write_text(json.dumps({
        "state": "ROLLED_BACK",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-NONEXISTENT.yaml",
            "staging_path": str(test_repo / f"knowledge/units/laws/NT-LAW-NONEXISTENT.yaml.tmp_apply_{journal_pid}"),
            "backup_path": str(test_repo / f"knowledge/units/laws/NT-LAW-NONEXISTENT.yaml.bak_apply_{journal_pid}"),
            "sha256_base": "0" * 64,
            "status": "restored",
        }],
    }), encoding="utf-8")

    ok, err = recover_from_pending_journals(test_repo)
    assert ok is False
    assert "missing" in err.lower() or "recovery failed" in err.lower()
    # Journal must not be deleted on failure
    assert j_path.exists()
    j_path.unlink(missing_ok=True)


def test_committed_cleanup(tmp_path: Path) -> None:
    """Verify that recovery from COMMITTED state validates sha256_target and cleans up temp assets."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path)
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    journal_pid = 888
    j_path = j_dir / f".apply_journal_{journal_pid}.json"

    canon_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml"
    tmp_file = canon_file.with_name(f"{canon_file.name}.tmp_apply_{journal_pid}")
    bak_file = canon_file.with_name(f"{canon_file.name}.bak_apply_{journal_pid}")
    tmp_file.write_text("staging content", encoding="utf-8")
    bak_file.write_text("backup content", encoding="utf-8")

    target_sha = sha256_bytes(canon_file.read_bytes())

    # Case 1: Canonical matches sha256_target -> cleans up and deletes journal
    j_path.write_text(json.dumps({
        "state": "COMMITTED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(tmp_file),
            "backup_path": str(bak_file),
            "sha256_base": "0" * 64,
            "sha256_target": target_sha,
            "status": "replaced",
        }],
    }), encoding="utf-8")

    ok, _msg = recover_from_pending_journals(test_repo)
    assert ok is True
    assert not j_path.exists()
    assert not tmp_file.exists()
    assert not bak_file.exists()

    # Case 2: Canonical hash mismatch in COMMITTED state -> fails closed
    tmp_file.write_text("staging content 2", encoding="utf-8")
    j_path.write_text(json.dumps({
        "state": "COMMITTED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(tmp_file),
            "backup_path": str(bak_file),
            "sha256_base": "0" * 64,
            "sha256_target": "1" * 64,  # mismatched target hash
            "status": "replaced",
        }],
    }), encoding="utf-8")

    ok2, err2 = recover_from_pending_journals(test_repo)
    assert ok2 is False
    assert "mismatch" in err2.lower()
    assert j_path.exists()
    j_path.unlink(missing_ok=True)
    tmp_file.unlink(missing_ok=True)


def test_all_journal_states_recovery(tmp_path: Path) -> None:
    """Verify crash recovery handles all recognized journal states properly."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path)
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    canon_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml"
    base_sha = sha256_bytes(canon_file.read_bytes())

    # Pre-replace states
    pre_replace_states = [
        "INIT",
        "PREPARING_STAGING",
        "STAGED",
        "ABORTED_INVALID_OVERLAY",
        "ABORTED_DUPLICATE_STAGED_IDS",
        "ABORTED_STAGING_ERROR",
    ]
    for state_index, st in enumerate(pre_replace_states, start=91000):
        j_p = j_dir / f".apply_journal_{state_index}.json"
        tmp_p = canon_file.with_name(f"{canon_file.name}.tmp_apply_{state_index}")
        bak_p = canon_file.with_name(f"{canon_file.name}.bak_apply_{state_index}")
        tmp_p.write_text("temp", encoding="utf-8")
        bak_p.write_text("backup", encoding="utf-8")
        j_p.write_text(json.dumps({
            "state": st,
            "entries": [{
                "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
                "staging_path": str(tmp_p),
                "backup_path": str(bak_p),
                "sha256_base": base_sha,
                "status": "staged",
            }],
        }), encoding="utf-8")

        ok, msg = recover_from_pending_journals(test_repo)
        assert ok is True, f"Recovery failed for state {st}: {msg}"
        assert not j_p.exists()
        assert not tmp_p.exists()
        assert not bak_p.exists()
        assert sha256_bytes(canon_file.read_bytes()) == base_sha

    # Active / replace states: REPLACING, COMMITTING, ROLLING_BACK, ROLLBACK_FAILED
    replace_states = ["REPLACING", "COMMITTING", "ROLLING_BACK", "ROLLBACK_FAILED"]
    for state_index, st in enumerate(replace_states, start=92000):
        j_p = j_dir / f".apply_journal_{state_index}.json"
        tmp_p = canon_file.with_name(f"{canon_file.name}.tmp_apply_{state_index}")
        bak_p = canon_file.with_name(f"{canon_file.name}.bak_apply_{state_index}")
        tmp_p.write_text("temp", encoding="utf-8")
        # Backup has the original base bytes
        bak_p.write_bytes(canon_file.read_bytes())
        # Canonical is modified
        canon_file.write_text("# modified during test\n", encoding="utf-8")

        j_p.write_text(json.dumps({
            "state": st,
            "entries": [{
                "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
                "staging_path": str(tmp_p),
                "backup_path": str(bak_p),
                "sha256_base": base_sha,
                "status": "replaced",
            }],
        }), encoding="utf-8")

        ok, msg = recover_from_pending_journals(test_repo)
        assert ok is True, f"Recovery failed for active state {st}: {msg}"
        assert not j_p.exists()
        assert not tmp_p.exists()
        assert not bak_p.exists()
        assert sha256_bytes(canon_file.read_bytes()) == base_sha


def test_subprocess_hard_kill_durability_boundaries(tmp_path: Path) -> None:
    """Verify that hard exit/crash during transaction leaves durable journals recovered idempotently."""
    tool_path = ROOT / "scripts" / "knowledge_content_pilot_tool.py"

    # Case A: Hard exit after STAGED (before replacing any canonical file)
    test_repo_a, base_hash_a, _review_hash_a, manifest_p_a, cr_p_a = create_isolated_fixture_repository(tmp_path / "case_a")
    proc_a = subprocess.run(
        [
            sys.executable,
            str(tool_path),
            "--repo-root", str(test_repo_a),
            "--cr-path", str(cr_p_a),
            "--apply-frozen",
            "--po-approval-id", "PO-APPROVED-TEST-ISOLATED",
            "--base-ref", base_hash_a,
            "--manifest", str(manifest_p_a),
            "--isolated-worktree",
            "--fault-injection-json", json.dumps({"hard_exit_after_staged": True}),
        ],
        capture_output=True,
        check=False,
    )
    assert proc_a.returncode != 0
    journals_a = list((test_repo_a / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert len(journals_a) == 1
    j_data_a = json.loads(journals_a[0].read_text(encoding="utf-8"))
    assert j_data_a["state"] == "STAGED"
    ok_a, msg_a = recover_from_pending_journals(test_repo_a)
    assert ok_a is True, f"Recovery failed: {msg_a}"
    assert not list((test_repo_a / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))

    # Case B: Hard exit during replacement (after replacing file index 2)
    test_repo_b, base_hash_b, _review_hash_b, manifest_p_b, cr_p_b = create_isolated_fixture_repository(tmp_path / "case_b")
    proc_b = subprocess.run(
        [
            sys.executable,
            str(tool_path),
            "--repo-root", str(test_repo_b),
            "--cr-path", str(cr_p_b),
            "--apply-frozen",
            "--po-approval-id", "PO-APPROVED-TEST-ISOLATED",
            "--base-ref", base_hash_b,
            "--manifest", str(manifest_p_b),
            "--isolated-worktree",
            "--fault-injection-json", json.dumps({"hard_exit_after_replace_idx": 2}),
        ],
        capture_output=True,
        check=False,
    )
    assert proc_b.returncode != 0
    journals_b = list((test_repo_b / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert len(journals_b) == 1
    assert json.loads(journals_b[0].read_text(encoding="utf-8"))["state"] == "REPLACING"
    ok_b, msg_b = recover_from_pending_journals(test_repo_b)
    assert ok_b is True, f"Recovery failed: {msg_b}"
    assert not list((test_repo_b / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    for fid in FROZEN_PILOT_IDS:
        cf = next(iter((test_repo_b / "knowledge" / "units").rglob(f"{fid}*.yaml")))
        canon_data = yaml.load(cf.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        assert canon_data["status"] == "frozen"
        assert canon_data["version"] in ("1.0.0", "0.2.0")

    # Case C: Hard exit after COMMITTED (before journal cleanup)
    test_repo_c, base_hash_c, _review_hash_c, manifest_p_c, cr_p_c = create_isolated_fixture_repository(tmp_path / "case_c")
    proc_c = subprocess.run(
        [
            sys.executable,
            str(tool_path),
            "--repo-root", str(test_repo_c),
            "--cr-path", str(cr_p_c),
            "--apply-frozen",
            "--po-approval-id", "PO-APPROVED-TEST-ISOLATED",
            "--base-ref", base_hash_c,
            "--manifest", str(manifest_p_c),
            "--isolated-worktree",
            "--fault-injection-json", json.dumps({"hard_exit_after_committed": True}),
        ],
        capture_output=True,
        check=False,
    )
    assert proc_c.returncode != 0
    journals_c = list((test_repo_c / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    assert len(journals_c) == 1
    assert json.loads(journals_c[0].read_text(encoding="utf-8"))["state"] == "COMMITTED"
    ok_c, msg_c = recover_from_pending_journals(test_repo_c)
    assert ok_c is True, f"Recovery failed: {msg_c}"
    assert not list((test_repo_c / "specs" / "REMEDIATION-CONTROLLED-RECOVERY").glob(".apply_journal_*.json"))
    for fid in FROZEN_PILOT_IDS:
        cf = next(iter((test_repo_c / "knowledge" / "units").rglob(f"{fid}*.yaml")))
        canon_data = yaml.load(cf.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        assert tuple(map(int, canon_data["version"].split("."))) >= (1, 0, 0)


def test_concurrent_apply_exclusive_lock(tmp_path: Path) -> None:
    """Verify ExclusiveTransactionLock provides concurrency exclusion and reclaims stale locks."""
    test_repo, _, _, _, _ = create_isolated_fixture_repository(tmp_path)

    lock1 = ExclusiveTransactionLock(test_repo)
    lock2 = ExclusiveTransactionLock(test_repo)

    assert lock1.acquire() is True
    # Second acquisition fails
    assert lock2.acquire() is False

    # Recovery must honor the same lock and leave an active transaction untouched.
    j_dir = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    canon_file = test_repo / "knowledge" / "units" / "laws" / "NT-LAW-2101.yaml"
    journal_pid = 99987
    tmp_file = canon_file.with_name(f"{canon_file.name}.tmp_apply_{journal_pid}")
    bak_file = canon_file.with_name(f"{canon_file.name}.bak_apply_{journal_pid}")
    tmp_file.write_text("active staging", encoding="utf-8")
    journal_file = j_dir / f".apply_journal_{journal_pid}.json"
    journal_file.write_text(json.dumps({
        "state": "STAGED",
        "entries": [{
            "canonical_path": "knowledge/units/laws/NT-LAW-2101.yaml",
            "staging_path": str(tmp_file),
            "backup_path": str(bak_file),
            "sha256_base": sha256_bytes(canon_file.read_bytes()),
            "status": "staged",
        }],
    }), encoding="utf-8")
    recovered, message = recover_from_pending_journals(test_repo)
    assert recovered is False
    assert "active" in message.lower()
    assert journal_file.exists()
    assert tmp_file.exists()

    lock1.release()

    recovered, message = recover_from_pending_journals(test_repo)
    assert recovered is True, message
    assert not journal_file.exists()
    assert not tmp_file.exists()

    # Now second acquisition succeeds
    assert lock2.acquire() is True
    lock2.release()

    # Stale lock test: write lock file with dead PID
    dead_pid = 99999999  # Non-existent PID
    lock_file = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / ".apply_transaction.lock"
    lock_file.write_text(json.dumps({"pid": dead_pid, "acquired_at": "2026-10-01T00:00:00Z"}), encoding="utf-8")

    lock3 = ExclusiveTransactionLock(test_repo)
    assert lock3.acquire() is True
    lock3.release()


def test_transaction_lock_detects_exited_process() -> None:
    """An exited process must not keep a crash-recovery lock alive on Windows."""
    proc = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        assert ExclusiveTransactionLock._is_pid_alive(proc.pid) is True
    finally:
        proc.terminate()
        proc.wait(timeout=10)

    assert ExclusiveTransactionLock._is_pid_alive(proc.pid) is False


def test_rollback_fails_closed_when_manifest_canonical_is_missing(tmp_path: Path) -> None:
    """Rollback must not silently skip a missing canonical file."""
    test_repo, base_hash, _review_hash, manifest_path, _approved_cr = create_isolated_fixture_repository(tmp_path)
    missing_file = next(iter((test_repo / "knowledge" / "units").rglob("NT-LAW-2101*.yaml")))
    missing_file.unlink()

    ret = execute_rollback(test_repo, base_ref=base_hash, dry_run=True, manifest_path=manifest_path)
    assert ret == 1


def test_dry_run_zero_write_assertion(tmp_path: Path) -> None:
    """Verify that dry-run is strictly read-only: zero file modifications and blocks on pending journals."""
    test_repo, base_hash, _review_hash, manifest_path, approved_cr = create_isolated_fixture_repository(tmp_path)

    def snapshot_repo(repo: Path) -> dict[str, str]:
        files: dict[str, str] = {}
        for p in repo.rglob("*"):
            if p.is_file() and not p.name.endswith(".lock"):
                files[p.relative_to(repo).as_posix()] = sha256_bytes(p.read_bytes())
        return files

    before = snapshot_repo(test_repo)

    # 1. Apply dry-run
    ret_apply = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=True,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
    )
    assert ret_apply == 0
    after_apply = snapshot_repo(test_repo)
    assert before == after_apply, "execute_apply_frozen --dry-run modified files on disk!"

    # 2. Rollback dry-run
    ret_rb = execute_rollback(test_repo, base_ref=base_hash, dry_run=True, manifest_path=manifest_path)
    assert ret_rb == 0
    after_rb = snapshot_repo(test_repo)
    assert before == after_rb, "execute_rollback --dry-run modified files on disk!"

    # 3. Dry-run blocks if pending journal exists without auto-recovering
    j_file = test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / ".apply_journal_pending.json"
    j_file.write_text(json.dumps({"state": "STAGED", "entries": []}), encoding="utf-8")

    ret_blocked = execute_apply_frozen(
        test_repo,
        po_approval_id="PO-APPROVED-TEST-ISOLATED",
        base_ref=base_hash,
        dry_run=True,
        manifest_path=manifest_path,
        cr_path_override=approved_cr,
    )
    assert ret_blocked == 1
    assert j_file.exists(), "Dry-run must not delete or modify pending journals!"
    j_file.unlink(missing_ok=True)


def test_review_commit_nonexistent_or_tampered(tmp_path: Path) -> None:
    """Verify that approval binding strictly verifies review commit existence and content hashes."""
    test_repo, base_hash, _review_hash, manifest_path, _ = create_isolated_fixture_repository(tmp_path)
    manifest_sha = sha256_bytes(manifest_path.read_bytes())

    # 1. approved_review_commit_sha does not exist in Git
    non_existent_commit = "f" * 40
    cr1 = test_repo / "governance" / "change-requests" / "CR_NONEXISTENT.md"
    make_approved_cr_fixture(
        cr1,
        approval_id="PO-TEST-NONEXISTENT",
        base_commit_sha=base_hash,
        review_commit_sha=non_existent_commit,
        manifest_sha=manifest_sha,
    )
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-NONEXISTENT", base_ref=base_hash, manifest_path=manifest_path, dry_run=True, cr_path_override=cr1) == 1

    # 2. approved_review_commit_sha exists (base_hash), but manifest is missing from that commit
    cr2 = test_repo / "governance" / "change-requests" / "CR_BASE_AS_REVIEW.md"
    make_approved_cr_fixture(
        cr2,
        approval_id="PO-TEST-BASE-AS-REVIEW",
        base_commit_sha=base_hash,
        review_commit_sha=base_hash,
        manifest_sha=manifest_sha,
    )
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-BASE-AS-REVIEW", base_ref=base_hash, manifest_path=manifest_path, dry_run=True, cr_path_override=cr2) == 1

    # 3. Create a commit 3 with tampered proposal content, but set manifest sha256_proposal to old hash
    prop_file = next(iter((test_repo / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units").glob("NT-LAW-2101*.yaml")))
    prop_file.write_text(prop_file.read_text(encoding="utf-8") + "\n# tampered in git\n", encoding="utf-8")
    subprocess.run(["git", "add", "specs"], cwd=str(test_repo), check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Commit with tampered proposal"], cwd=str(test_repo), check=True, capture_output=True)
    tampered_commit = resolve_full_commit_hash(test_repo, "HEAD")

    cr3 = test_repo / "governance" / "change-requests" / "CR_TAMPERED_COMMIT.md"
    make_approved_cr_fixture(
        cr3,
        approval_id="PO-TEST-TAMPERED-COMMIT",
        base_commit_sha=base_hash,
        review_commit_sha=tampered_commit,
        manifest_sha=manifest_sha,
    )
    assert execute_apply_frozen(test_repo, po_approval_id="PO-TEST-TAMPERED-COMMIT", base_ref=base_hash, manifest_path=manifest_path, dry_run=True, cr_path_override=cr3) == 1


def test_real_repo_frozen_canonical_hashes_snapshot() -> None:
    """Verify that all 6 canonical Frozen units on ROOT (D:\\NhanThuat) maintain 100% hash parity with base commit."""
    base_files = load_base_commit_files(ROOT, DEFAULT_BASE_REF)
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((ROOT / "knowledge" / "units").rglob(f"{frozen_id}*.yaml"))
        assert len(matches) == 1, f"Expected exactly 1 match for {frozen_id} in {ROOT}"
        cf = matches[0]
        rel = cf.relative_to(ROOT).as_posix()
        assert rel in base_files, f"{rel} not in base files"
        expected_sha = sha256_bytes(base_files[rel])
        current_sha = sha256_bytes(cf.read_bytes())
        assert current_sha == expected_sha, (
            f"CRITICAL: Real canonical unit {rel} differs from base commit! current {current_sha} != expected {expected_sha}"
        )


def test_execute_audit_full_pilot_set() -> None:
    """Verify that the repository-level execute_audit passes with 0 strict issues."""
    strict_issues, telemetry_notes = execute_audit(ROOT)
    assert strict_issues == [], f"Strict audit failed with issues: {strict_issues}"
    assert isinstance(telemetry_notes, list)


def test_placeholder_reference_detection() -> None:
    """Verify placeholder reference helper correctly classifies sources."""
    assert is_placeholder_reference("EV-REQ-0001-01") is True
    assert is_placeholder_reference("ev-req-9999-99") is True
    assert is_placeholder_reference("Placeholder source reference") is True
    assert is_placeholder_reference("[Empirical Study] Kahneman & Tversky (1979)") is False
