"""Deterministic pilot content generator, recovery tool, and anti-boilerplate validator.

This module provides a repository-resident, deterministic CLI tool that:
1. Determines target units deterministically using a fixed base commit (default: 27a34bcd840713df1817517066b4cf1a9b1623a3)
   or explicit manifest, remaining invariant to future HEAD movements.
2. Supports ``--audit-only``, ``--dry-run``, ``--manifest <path>``, ``--base-ref <ref>``,
   ``--apply-draft``, ``--apply-frozen``, and ``--rollback``.
3. Strictly protects Frozen governance: ``--apply-frozen`` fails-closed unless:
   - ``--manifest`` is provided and valid;
   - all units exist in manifest with valid 64-hex SHA-256 for both base and proposal;
   - full 40-character base commit hash matches repository commit;
   - structured Change Request frontmatter has status 'APPROVED_BY_PRODUCT_OWNER'
     with matching approval_id, non-empty approved_by, approved_at, approved_scope,
      approved_review_commit_sha, approved_base_commit_sha, and approved_manifest_sha256 (no prose matching);
   - manifest SHA-256 matches approved_manifest_sha256;
   - canonical paths derived from immutable base tree match manifest (manifest path cross-check);
   - canonical current SHA matches manifest base SHA;
   - proposal SHA matches manifest proposal SHA;
   - proposed_unit passes canonical schema, naming, and absolutism audits;
   - any discrepancy halts execution before writing any file.
4. Strictly controls rollback:
   - ``--manifest`` is required;
   - only rolls back entries explicitly listed in the manifest (no implicit fallback to 352 units);
   - requires ``--confirm-rollback`` for live changes.
5. Implements rollback-assisted replacement with durable transaction journaling, staging overlay
   verification, and automatic inverse-order rollback upon any error or fault injection.
6. Enforces the 7-tier standardized academic source classification system:
   [Empirical Study], [Theoretical Model], [Review/Meta-analysis],
   [Academic Monograph], [Popular Synthesis], [Classical Analogy], [Editorial Inference].
7. Enforces comprehensive anti-absolutist and anti-boilerplate audits across all fields.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any, Self

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DEFAULT_BASE_REF = "27a34bcd840713df1817517066b4cf1a9b1623a3"
DEFAULT_BASE_REF_SHORT = "27a34bc"

HEX40_REGEX = re.compile(r"^[0-9a-f]{40}$")
HEX64_REGEX = re.compile(r"^[0-9a-f]{64}$")
KU_SCHEMA_PATH = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"

BANNED_BOILERPLATE_PHRASES: tuple[str, ...] = (
    "mọi thất bại trong việc xử lý",
    "Chúng ta không đánh cược vận mệnh dự án",
    "Trong một phiên họp quyết định nhân sự",
    "con người luôn vận hành trên hai tầng sóng",
    "cửa sổ duy nhất phơi bày cấu trúc nhân cách thật sự",
    "chân lý bất biến",
)

ABSOLUTIST_PATTERNS: tuple[tuple[str, str], ...] = (
    ("luôn lớn gấp đôi", "Định lượng hệ số tuyệt đối hóa không có căn cứ biên độ"),
    ("áp dụng hiệu quả cho mọi", "Khẳng định phổ quát không có điều kiện biên"),
    ("áp dụng cho mọi", "Khẳng định phổ quát thiếu phạm vi giới hạn"),
    ("chân lý bất biến", "Tuyên bố chắc chắn vĩnh cửu về hành vi con người"),
    ("không bao giờ", "Tuyệt đối hóa hành vi hoặc kết quả"),
)

REQUIRED_PILOT_SECTIONS: tuple[str, ...] = (
    "Điều kiện áp dụng",
    "Ngoại lệ",
    "Mức bất định",
    "Rủi ro diễn giải sai",
    "Nguồn truy nguyên",
)

SOURCE_CLASS_TAGS: tuple[str, ...] = (
    "[Empirical Study]",
    "[Theoretical Model]",
    "[Review/Meta-analysis]",
    "[Academic Monograph]",
    "[Popular Synthesis]",
    "[Classical Analogy]",
    "[Editorial Inference]",
)

DRAFT_PILOT_IDS: tuple[str, ...] = (
    "NT-LAW-3201",
    "NT-LAW-4102",
    "NT-PRINCIPLE-4101",
    "NT-PHENOMENON-4101",
    "NT-PHENOMENON-4102",
    "NT-PHENOMENON-4103",
)

FROZEN_PILOT_IDS: tuple[str, ...] = (
    "NT-LAW-2101",
    "NT-MODEL-2101",
    "NT-MODEL-2201",
    "NT-PRINCIPLE-0063",
    "NT-ANTI-PATTERN-0012",
    "NT-ANTI-PATTERN-0013",
)

ALL_PILOT_IDS: tuple[str, ...] = DRAFT_PILOT_IDS + FROZEN_PILOT_IDS


def sha256_bytes(b: bytes) -> str:
    normalized = b.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def resolve_full_commit_hash(repo_root: Path, ref: str) -> str:
    """Resolve any git ref to its full 40-character hexadecimal commit hash."""
    return subprocess.check_output(
        ["git", "rev-parse", f"{ref}^{{commit}}"],
        cwd=str(repo_root),
        text=True,
    ).strip()


def verify_promotion_worktree(repo_root: Path, review_commit_sha: str) -> tuple[bool, str]:
    """Verify that live promotion runs from a detached linked Git worktree at the approved commit."""
    repo_res = repo_root.resolve()
    git_marker = repo_res / ".git"
    if not git_marker.is_file():
        return False, "repository is not a linked Git worktree (.git must be a worktree pointer file)"

    try:
        top_level = Path(
            subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(repo_res),
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
        ).resolve()
        head_sha = resolve_full_commit_hash(repo_res, "HEAD")
        symbolic_ref = subprocess.run(
            ["git", "symbolic-ref", "-q", "HEAD"],
            cwd=str(repo_res),
            capture_output=True,
            check=False,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        return False, f"unable to verify promotion worktree: {exc}"

    if top_level != repo_res:
        return False, f"Git top-level '{top_level}' does not match repo_root '{repo_res}'"
    if head_sha != review_commit_sha:
        return False, f"worktree HEAD '{head_sha}' does not match approved review commit '{review_commit_sha}'"
    if symbolic_ref.returncode == 0:
        return False, "promotion worktree must use detached HEAD at the approved review commit"
    return True, "Detached linked promotion worktree verified."


def parse_change_request_metadata(cr_path: Path) -> dict[str, Any]:
    """Parse structured metadata strictly from Change Request YAML frontmatter.

    Does NOT perform substring or prose searches. Only reads the official
    frontmatter metadata block between '---' delimiters.
    """
    if not cr_path.exists():
        raise FileNotFoundError(f"Change Request file '{cr_path}' not found.")

    text = cr_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"Change Request '{cr_path.name}' lacks required YAML frontmatter delimiter '---'.")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Change Request '{cr_path.name}' has malformed frontmatter delimiter.")

    frontmatter_raw = parts[1]
    data = yaml.load(frontmatter_raw, Loader=YAML_LOADER)
    if not isinstance(data, dict):
        raise TypeError(f"Change Request '{cr_path.name}' frontmatter is not a dictionary.")

    return data


def load_knowledge_unit_schema() -> dict[str, Any]:
    """Load canonical JSON schema for knowledge units."""
    if not KU_SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Knowledge unit schema missing at {KU_SCHEMA_PATH}")
    return json.loads(KU_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_proposed_unit_schema(
    unit_data: dict[str, Any],
    canonical_path: Path | str,
    schema: dict[str, Any] | None = None,
) -> list[str]:
    """Validate proposed unit dictionary against canonical JSON schema, naming conventions, and required types."""
    from jsonschema import Draft202012Validator, FormatChecker

    from nhan_thuat.naming import (
        validate_filename_contains_id,
        validate_unit_identifier_matches_type,
    )

    errors: list[str] = []
    if schema is None:
        schema = load_knowledge_unit_schema()

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for err in sorted(validator.iter_errors(unit_data), key=lambda e: list(e.path)):
        loc = ".".join(str(p) for p in err.path) if err.path else "root"
        errors.append(f"Schema error at '{loc}': {err.message}")

    unit_id = unit_data.get("id")
    unit_type = unit_data.get("type")
    unit_status = unit_data.get("status")

    if not unit_id or not isinstance(unit_id, str):
        errors.append("Missing or invalid 'id' string")
    if not unit_type or not isinstance(unit_type, str):
        errors.append("Missing or invalid 'type' string")

    if unit_id and unit_type:
        match_issue = validate_unit_identifier_matches_type(unit_id, unit_type)
        if match_issue:
            errors.append(f"Identifier/type mismatch: {match_issue}")

        fn_issue = validate_filename_contains_id(Path(canonical_path), unit_id)
        if fn_issue:
            errors.append(f"Filename/id mismatch: {fn_issue}")

    if unit_status != "frozen":
        errors.append(f"Proposed unit status must be 'frozen', got '{unit_status}'")

    return errors


def load_base_unit_registry(repo_root: Path, base_ref: str = DEFAULT_BASE_REF) -> dict[str, dict[str, Any]]:
    """Derive mapping of unit_id -> canonical_path and metadata strictly from immutable base tree."""
    base_files = load_base_commit_files(repo_root, base_ref)
    registry: dict[str, dict[str, Any]] = {}
    for rel_path, raw_bytes in base_files.items():
        try:
            data = yaml.load(raw_bytes.decode("utf-8"), Loader=YAML_LOADER)
            if not isinstance(data, dict):
                continue
            uid = data.get("id")
            if uid and isinstance(uid, str):
                registry[uid] = {
                    "id": uid,
                    "canonical_path": rel_path.replace("\\", "/"),
                    "type": data.get("type"),
                    "status": data.get("status"),
                    "version": data.get("version"),
                    "data": data,
                    "sha256": sha256_bytes(raw_bytes),
                }
        except (yaml.YAMLError, UnicodeDecodeError):
            continue
    return registry


def sanitize_and_resolve_paths(
    repo_root: Path,
    frozen_id: str,
    m_entry: dict[str, Any],
    base_unit_registry: dict[str, dict[str, Any]],
    seen_destinations: set[str],
) -> tuple[Path, Path, str, str]:
    """Sanitize and resolve canonical and proposal paths without trusting manifest paths.

    Returns (canon_path, prop_path, derived_canon_rel, prop_rel).
    Raises ValueError or FileNotFoundError on any safety violation.
    """
    # 1. Look up unit in immutable base tree
    if frozen_id not in base_unit_registry:
        raise ValueError(f"Unit '{frozen_id}' not found in immutable base commit tree.")
    base_entry = base_unit_registry[frozen_id]

    derived_canon_rel = base_entry["canonical_path"]

    # 2. Check base file invariants
    if base_entry["id"] != frozen_id:
        raise ValueError(f"Base tree entry id mismatch for '{frozen_id}': found '{base_entry['id']}'")
    if base_entry["status"] != "frozen":
        raise ValueError(f"Base tree entry '{frozen_id}' is not 'frozen': found '{base_entry['status']}'")
    if base_entry["type"] not in ("law", "principle", "model", "phenomenon", "anti-pattern", "strategy"):
        raise ValueError(f"Base tree entry '{frozen_id}' has invalid type: found '{base_entry['type']}'")

    # 3. Cross-check manifest canonical path against immutable derived path
    manifest_canon_rel = m_entry.get("canonical_path")
    if not manifest_canon_rel or manifest_canon_rel != derived_canon_rel:
        raise ValueError(
            f"Manifest canonical_path '{manifest_canon_rel}' does not match immutable base tree path '{derived_canon_rel}' for {frozen_id}"
        )

    # 4. Canonical path sanitization
    if Path(derived_canon_rel).is_absolute() or os.path.isabs(derived_canon_rel):
        raise ValueError(f"Absolute path rejected for canonical unit: {derived_canon_rel}")
    if ".." in Path(derived_canon_rel).parts:
        raise ValueError(f"Directory traversal '..' rejected for canonical unit: {derived_canon_rel}")
    if not derived_canon_rel.startswith("knowledge/units/"):
        raise ValueError(f"Canonical path must be within knowledge/units/: {derived_canon_rel}")
    if not derived_canon_rel.endswith(".yaml"):
        raise ValueError(f"Canonical path must have .yaml extension: {derived_canon_rel}")

    # Duplicate destination check
    if derived_canon_rel in seen_destinations:
        raise ValueError(f"Duplicate destination canonical path detected: {derived_canon_rel}")
    seen_destinations.add(derived_canon_rel)

    canon_path = repo_root / derived_canon_rel
    if not canon_path.exists():
        raise FileNotFoundError(f"Canonical file {canon_path} does not exist on disk.")
    if canon_path.is_symlink():
        raise ValueError(f"Symlink rejected for canonical file: {canon_path}")

    # 5. Proposal path sanitization
    prop_rel = m_entry.get("target_path")
    if not prop_rel:
        raise ValueError(f"Manifest entry {frozen_id} missing target_path.")
    if Path(prop_rel).is_absolute() or os.path.isabs(prop_rel):
        raise ValueError(f"Absolute path rejected for proposal: {prop_rel}")
    if ".." in Path(prop_rel).parts:
        raise ValueError(f"Directory traversal '..' rejected for proposal: {prop_rel}")
    if not prop_rel.startswith("specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/"):
        raise ValueError(f"Proposal path must be inside specs/REMEDIATION-CONTROLLED-RECOVERY/pilot_units/: {prop_rel}")
    if not prop_rel.endswith(".yaml"):
        raise ValueError(f"Proposal path must have .yaml extension: {prop_rel}")
    if not Path(prop_rel).name.startswith(frozen_id):
        raise ValueError(f"Proposal file {prop_rel} must start with unit id {frozen_id}")

    prop_path = repo_root / prop_rel
    if not prop_path.exists():
        raise FileNotFoundError(f"Proposal artifact for {frozen_id} missing at {prop_path}")
    if prop_path.is_symlink():
        raise ValueError(f"Symlink rejected for proposal file: {prop_path}")

    return canon_path, prop_path, derived_canon_rel, prop_rel


def load_base_commit_files(repo_root: Path, base_ref: str = DEFAULT_BASE_REF) -> dict[str, bytes]:
    """Load raw bytes of all units in base_ref deterministically."""
    full_hash = resolve_full_commit_hash(repo_root, base_ref)
    tar_bytes = subprocess.check_output(
        ["git", "archive", full_hash, "knowledge/units"],
        cwd=str(repo_root),
    )
    base_raw: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as archive:
        for member in archive.getmembers():
            if member.isfile() and member.name.endswith(".yaml"):
                extracted = archive.extractfile(member)
                if extracted is not None:
                    base_raw[member.name.replace("\\", "/")] = extracted.read()
    return base_raw


def get_target_352_paths(repo_root: Path, base_ref: str = DEFAULT_BASE_REF) -> list[str]:
    """Deterministically determine the 352 target units using base commit 27a34bc.

    In commit 27a34bc, exactly 27 units belonged to Wave 1. The remaining 352 units
    form the immutable target set regardless of future repository commits.
    """
    base_files = load_base_commit_files(repo_root, base_ref)
    full_hash = resolve_full_commit_hash(repo_root, base_ref)
    wave1_files = set(
        subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", full_hash, "--", "knowledge/units/"],
            cwd=str(repo_root),
            text=True,
        ).splitlines()
    )
    target = sorted(f.replace("\\", "/") for f in base_files if f not in wave1_files)
    if len(target) != 352:
        raise RuntimeError(f"Expected exactly 352 target units from base {base_ref}, found {len(target)}")
    return target


def is_placeholder_reference(ref: str) -> bool:
    clean = ref.strip().lower()
    return bool(re.search(r"ev-req-\d{4}-\d{2}", clean)) or "placeholder" in clean


def audit_unit_absolutism(data: dict[str, Any], path: Path | str) -> list[str]:
    """Scan all text fields in a knowledge unit for absolutist phrasing."""
    issues: list[str] = []
    unit_id = str(data.get("id", path))

    fields_to_check: list[tuple[str, str]] = []
    for key in ("title", "summary", "definition", "content"):
        val = data.get(key)
        if isinstance(val, str):
            fields_to_check.append((key, val))

    for list_key in ("mechanism", "conditions", "exceptions", "risks"):
        items = data.get(list_key)
        if isinstance(items, list):
            for idx, item in enumerate(items):
                if isinstance(item, str):
                    fields_to_check.append((f"{list_key}[{idx}]", item))

    apps = data.get("applications")
    if isinstance(apps, dict):
        for k, v in apps.items():
            if isinstance(v, list):
                for idx, item in enumerate(v):
                    if isinstance(item, str):
                        fields_to_check.append((f"applications.{k}[{idx}]", item))

    for field_name, text in fields_to_check:
        for phrase in BANNED_BOILERPLATE_PHRASES:
            if phrase.lower() in text.lower():
                issues.append(f"[{unit_id}] Banned boilerplate in '{field_name}': '{phrase}'")

        for pattern, rationale in ABSOLUTIST_PATTERNS:
            if pattern.lower() in text.lower():
                issues.append(f"[{unit_id}] Absolutist phrasing in '{field_name}': '{pattern}' ({rationale})")

    return issues


def audit_unit_evidence_classification(data: dict[str, Any], path: Path | str, is_pilot: bool) -> list[str]:
    """Verify that pilot units use the 7 standardized source classifications and honest evidence levels."""
    issues: list[str] = []
    unit_id = str(data.get("id", path))
    evidence = data.get("evidence") or {}
    level = evidence.get("level")
    refs = evidence.get("references") or []

    # Model specific check
    if unit_id == "NT-MODEL-2101" and level != "provisional":
        issues.append(f"[{unit_id}] NT-MODEL-2101 is an editorial synthesis and must remain 'provisional'.")

    # If it is one of the 12 pilot units (canonical draft or proposal artifact)
    if is_pilot:
        if level in ("supported", "strong"):
            if not refs:
                issues.append(f"[{unit_id}] Evidence level '{level}' with empty references.")
            elif all(is_placeholder_reference(str(r)) for r in refs):
                issues.append(f"[{unit_id}] Evidence level '{level}' based solely on placeholder references.")

        if not refs:
            issues.append(f"[{unit_id}] Pilot unit must have references.")
        for r in refs:
            r_str = str(r).strip()
            if not any(r_str.startswith(tag) for tag in SOURCE_CLASS_TAGS):
                issues.append(
                    f"[{unit_id}] Reference missing standardized 7-tier classification tag: {r_str[:60]}..."
                )

        # Check required sections in content
        content = str(data.get("content") or "")
        for sec in REQUIRED_PILOT_SECTIONS:
            if sec.lower() not in content.lower():
                issues.append(f"[{unit_id}] Pilot content missing required section '{sec}'")

    return issues


def execute_audit(repo_root: Path) -> tuple[list[str], list[str]]:
    """Audit pilot units (strict pass/fail) and scan repository-wide telemetry."""
    strict_issues: list[str] = []
    telemetry_notes: list[str] = []

    # 1. Audit the 6 canonical Draft pilot units
    for draft_id in DRAFT_PILOT_IDS:
        matches = list((repo_root / "knowledge" / "units").rglob(f"{draft_id}*.yaml"))
        if not matches:
            strict_issues.append(f"Draft pilot unit file for {draft_id} not found in canonical knowledge/units")
            continue
        p = matches[0]
        data = yaml.load(p.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        strict_issues.extend(audit_unit_absolutism(data, p))
        strict_issues.extend(audit_unit_evidence_classification(data, p, is_pilot=True))

    # 2. Audit the 6 Frozen proposal artifacts
    proposals_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units"
    if not proposals_dir.exists():
        strict_issues.append(f"Proposals directory not found: {proposals_dir}")
    else:
        for frozen_id in FROZEN_PILOT_IDS:
            matches = list(proposals_dir.glob(f"{frozen_id}*.yaml"))
            if not matches:
                strict_issues.append(f"Proposal artifact for {frozen_id} not found in {proposals_dir}")
                continue
            p = matches[0]
            proposal = yaml.load(p.read_text(encoding="utf-8"), Loader=YAML_LOADER)
            unit_data = proposal.get("proposed_unit") or {}
            strict_issues.extend(audit_unit_absolutism(unit_data, p))
            strict_issues.extend(audit_unit_evidence_classification(unit_data, p, is_pilot=True))

            # Audit version progression: proposed_version > current_version
            cur_ver = proposal.get("current_version")
            prop_ver = proposal.get("proposed_version")
            if cur_ver and prop_ver:
                try:
                    c_parts = tuple(map(int, cur_ver.split(".")))
                    p_parts = tuple(map(int, prop_ver.split(".")))
                    if p_parts <= c_parts:
                        strict_issues.append(
                            f"[{frozen_id}] proposed_version '{prop_ver}' must be strictly greater than current_version '{cur_ver}'"
                        )
                except ValueError:
                    strict_issues.append(f"[{frozen_id}] Invalid semver '{cur_ver}' or '{prop_ver}'")

    # 3. Governance check: canonical Frozen units must NOT be modified in working tree vs base commit
    base_files = load_base_commit_files(repo_root, DEFAULT_BASE_REF)
    for frozen_id in FROZEN_PILOT_IDS:
        matches = list((repo_root / "knowledge" / "units").rglob(f"{frozen_id}*.yaml"))
        if matches:
            p = matches[0]
            rel = p.relative_to(repo_root).as_posix()
            if rel in base_files:
                base_raw = base_files[rel]
                cur_raw = p.read_bytes()
                if sha256_bytes(cur_raw) != sha256_bytes(base_raw):
                    strict_issues.append(
                        f"Governance violation: canonical frozen unit {rel} differs from base commit {DEFAULT_BASE_REF_SHORT}. "
                        "Frozen units must not be modified directly before PO approval."
                    )

    # 4. Repository-wide scan for telemetry / change request documentation (excluding pilot units)
    for path in sorted((repo_root / "knowledge" / "units").rglob("*.yaml")):
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=YAML_LOADER)
        uid = str(data.get("id"))
        if uid not in ALL_PILOT_IDS:
            abs_issues = audit_unit_absolutism(data, path)
            telemetry_notes.extend(abs_issues)

    return strict_issues, telemetry_notes


def generate_manifest(
    repo_root: Path,
    base_ref: str = DEFAULT_BASE_REF,
) -> dict[str, Any]:
    """Generate the official change-control manifest for the 352 target units."""
    target_paths = get_target_352_paths(repo_root, base_ref)
    base_files = load_base_commit_files(repo_root, base_ref)
    full_base_commit = resolve_full_commit_hash(repo_root, base_ref)

    entries: list[dict[str, Any]] = []
    frozen_count = 0
    draft_count = 0

    proposals_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY" / "pilot_units"

    for rel_path in target_paths:
        base_raw = base_files[rel_path]
        base_data = yaml.load(base_raw.decode("utf-8"), Loader=YAML_LOADER)
        unit_id = str(base_data.get("id"))
        status = str(base_data.get("status"))

        file_path = repo_root / rel_path
        current_raw = file_path.read_bytes() if file_path.exists() else b""
        sha_base = sha256_bytes(base_raw)
        sha_current = sha256_bytes(current_raw)
        sha_proposal: str | None = None

        if status == "frozen":
            frozen_count += 1
            if unit_id in FROZEN_PILOT_IDS:
                target_type = "proposal"
                # Locate proposal artifact with slug on disk
                prop_matches = list(proposals_dir.glob(f"{unit_id}*.yaml"))
                if not prop_matches:
                    raise FileNotFoundError(f"Proposal artifact for {unit_id} missing in {proposals_dir}")
                target_file = prop_matches[0]
                target_path = target_file.relative_to(repo_root).as_posix()
                prop_bytes = target_file.read_bytes()
                sha_proposal = sha256_bytes(prop_bytes)
                action = "pilot_proposal_ready_for_review"

                # Validate proposed_unit against canonical schema during review manifest generation
                prop_data = yaml.load(prop_bytes.decode("utf-8"), Loader=YAML_LOADER)
                unit_data = prop_data.get("proposed_unit") or {}
                schema_issues = validate_proposed_unit_schema(unit_data, rel_path)
                if schema_issues:
                    raise ValueError(f"Proposal {unit_id} failed canonical schema validation during review manifest generation: {schema_issues}")
            else:
                target_type = "canonical"
                target_path = rel_path
                head_ev = base_data.get("evidence") or {}
                head_refs = head_ev.get("references") or []
                head_level = head_ev.get("level")
                if head_level in ("supported", "strong") and (
                    not head_refs or all(is_placeholder_reference(str(r)) for r in head_refs)
                ):
                    action = "maintain_base_telemetry_flagged_for_dedicated_cr"
                else:
                    action = "maintain_base"
        else:
            draft_count += 1
            target_type = "canonical"
            target_path = rel_path
            action = "pilot_draft_canonical_upgrade" if unit_id in DRAFT_PILOT_IDS else "maintain_base"

        entry: dict[str, Any] = {
            "id": unit_id,
            "canonical_path": rel_path,
            "governance_status": status,
            "target_type": target_type,
            "target_path": target_path,
            "sha256_base": sha_base,
            "sha256_current": sha_current,
            "action": action,
            "applied_to_canonical": sha_current != sha_base if status == "frozen" else True,
        }
        if sha_proposal is not None:
            entry["sha256_proposal"] = sha_proposal

        entries.append(entry)

    # Compute working tree fingerprint
    hasher = hashlib.sha256()
    for e in entries:
        hasher.update(e["sha256_current"].encode("ascii"))
    fingerprint = hasher.hexdigest()

    manifest = {
        "snapshot_id": "MANIFEST-REMEDIATION-CONTROLLED-RECOVERY",
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "base_commit": full_base_commit,
        "base_commit_short": full_base_commit[:7],
        "working_tree_fingerprint": fingerprint,
        "total_target_units": len(target_paths),
        "frozen_count": frozen_count,
        "draft_count": draft_count,
        "pilot_count": len(ALL_PILOT_IDS),
        "draft_pilot_count": len(DRAFT_PILOT_IDS),
        "frozen_pilot_count": len(FROZEN_PILOT_IDS),
        "entries": entries,
    }
    return manifest


def execute_rollback(
    repo_root: Path,
    base_ref: str = DEFAULT_BASE_REF,
    dry_run: bool = False,
    manifest_path: Path | None = None,
    _lock_held: bool = False,
) -> int:
    """Safely roll back modified canonical units using staged, journaled, hash-verified transactions.

    Strict rules:
    - manifest is REQUIRED.
    - only rolls back entries explicitly listed in the manifest (no implicit 352-unit fallback).
    - fails-closed if manifest missing or hash mismatch.
    - dry-run is strictly read-only (zero writes).
    - live rollback uses exclusive lock, staging overlay, durable journal, and hash verification.
    """
    if not manifest_path:
        print("ERROR: --rollback rejected: missing required --manifest <path>.", file=sys.stderr)
        print("Governance rule: Rollback must be scoped strictly to an explicit verified manifest.", file=sys.stderr)
        return 1

    if not manifest_path.exists():
        print(f"ERROR: Specified rollback manifest '{manifest_path}' does not exist.", file=sys.stderr)
        return 1

    if not dry_run and not _lock_held:
        outer_lock = ExclusiveTransactionLock(repo_root)
        if not outer_lock.acquire():
            print("ERROR: Another transaction is currently active. Rollback was not started.", file=sys.stderr)
            return 1
        try:
            return execute_rollback(
                repo_root,
                base_ref=base_ref,
                dry_run=False,
                manifest_path=manifest_path,
                _lock_held=True,
            )
        finally:
            outer_lock.release()

    journal_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    pending_journals = list(journal_dir.glob(".apply_journal_*.json")) if journal_dir.exists() else []
    if pending_journals:
        if dry_run:
            print(
                f"ERROR: Cannot execute rollback dry-run with {len(pending_journals)} pending journal(s).\n"
                "Dry-run is strictly read-only. Please run --recover-crash first.",
                file=sys.stderr,
            )
            return 1
        ok, msg = recover_from_pending_journals(repo_root, _lock_held=True)
        if not ok:
            print(f"CRITICAL: Crash recovery blocked rollback transaction: {msg}", file=sys.stderr)
            return 1

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: Invalid rollback manifest: {exc}", file=sys.stderr)
        return 1
    entries = manifest_data.get("entries", [])
    if not entries:
        print("ERROR: Specified rollback manifest contains no entries.", file=sys.stderr)
        return 1

    base_files = load_base_commit_files(repo_root, base_ref)
    to_rollback: list[tuple[Path, bytes, str, str]] = []

    seen_paths: set[Path] = set()
    repo_res = repo_root.resolve()
    for entry in entries:
        if not isinstance(entry, dict):
            print("ERROR: Rollback manifest contains a non-object entry.", file=sys.stderr)
            return 1
        rel_path = entry.get("canonical_path") or entry.get("path")
        if not isinstance(rel_path, str) or not rel_path or "\x00" in rel_path:
            print("ERROR: Rollback manifest entry has a missing or invalid canonical path.", file=sys.stderr)
            return 1
        rel_obj = Path(rel_path)
        if rel_obj.is_absolute() or ".." in rel_obj.parts:
            print(f"ERROR: Rollback canonical path is not confined: {rel_path}", file=sys.stderr)
            return 1
        file_path = (repo_root / rel_obj).resolve()
        file_rel = file_path.relative_to(repo_res).as_posix() if file_path.is_relative_to(repo_res) else ""
        if not file_rel.startswith("knowledge/units/"):
            print(f"ERROR: Rollback canonical path escapes knowledge/units: {rel_path}", file=sys.stderr)
            return 1
        if file_path.is_symlink() or file_path in seen_paths:
            print(f"ERROR: Rollback canonical path is a symlink or duplicate: {rel_path}", file=sys.stderr)
            return 1
        seen_paths.add(file_path)
        if not file_path.is_file():
            print(f"ERROR: Rollback canonical file is missing: {rel_path}", file=sys.stderr)
            return 1

        if rel_path not in base_files:
            print(f"ERROR: File {rel_path} not found in base commit {base_ref}.", file=sys.stderr)
            return 1

        base_raw = base_files[rel_path]
        sha_base = sha256_bytes(base_raw)
        expected_base = entry.get("base_sha256") or entry.get("sha256_base")
        if expected_base and expected_base != sha_base:
            print(
                f"ERROR: Manifest base hash mismatch for {rel_path}: expected {expected_base}, found {sha_base}",
                file=sys.stderr,
            )
            return 1

        cur_raw = file_path.read_bytes()
        cur_sha = sha256_bytes(cur_raw)
        if cur_sha != sha_base:
            to_rollback.append((file_path, base_raw, sha_base, rel_path))

    if not to_rollback:
        print(f"Rollback check: all {len(entries)} manifest units already match base commit hashes.")
        return 0

    print(f"Found {len(to_rollback)} unit(s) differing from base commit:")
    if dry_run:
        for _, _, sha, rel in to_rollback:
            print(f"  [DRY-RUN] Would restore: {rel} -> {sha[:12]}")
        return 0

    # Live Rollback Transaction
    pid = os.getpid()
    lock: ExclusiveTransactionLock | None = None

    try:
        journal_dir.mkdir(parents=True, exist_ok=True)
        journal_path = journal_dir / f".apply_journal_{pid}.json"

        journal_data: dict[str, Any] = {
            "transaction_id": f"TXN-ROLLBACK-{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d%H%M%S')}-{pid}",
            "state": "INIT",
            "base_commit": resolve_full_commit_hash(repo_root, base_ref),
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "entries": [],
        }

        staging_items: list[tuple[Path, Path, Path, bytes, str, str]] = []
        for file_path, base_raw, sha_b, rel_path in to_rollback:
            tmp_path = file_path.with_name(f"{file_path.name}.tmp_rollback_{pid}")
            bak_path = file_path.with_name(f"{file_path.name}.bak_rollback_{pid}")
            content_to_write = base_raw.replace(b"\r\n", b"\n")
            if os.name == "nt":
                content_to_write = content_to_write.replace(b"\n", b"\r\n")
            sha_target = sha256_bytes(content_to_write)
            staging_items.append((file_path, tmp_path, bak_path, content_to_write, sha_b, sha_target))
            journal_data["entries"].append({
                "canonical_path": rel_path,
                "staging_path": str(tmp_path),
                "backup_path": str(bak_path),
                "sha256_base": sha_b,
                "sha256_target": sha_target,
                "status": "planned",
            })

        def write_rb_journal(state_str: str) -> None:
            journal_data["state"] = state_str
            journal_data["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
            durable_write_journal(journal_path, journal_data)

        write_rb_journal("PREPARING_STAGING")
        for fpath, tmp_p, bak_p, data, sha_b, sha_t in staging_items:
            durable_write_bytes(tmp_p, data)
            for e in journal_data["entries"]:
                if e["canonical_path"] == fpath.relative_to(repo_root).as_posix():
                    e["status"] = "staged"
        write_rb_journal("STAGED")

        write_rb_journal("REPLACING")
        backups: list[tuple[Path, Path, str]] = []
        try:
            for fpath, tmp_p, bak_p, data, sha_b, sha_t in staging_items:
                durable_write_bytes(bak_p, fpath.read_bytes())
                backups.append((fpath, bak_p, sha_b))
                durable_replace(tmp_p, fpath)
                verified_sha = sha256_bytes(fpath.read_bytes())
                if verified_sha != sha_b:
                    raise OSError(f"Post-rollback hash mismatch for {fpath.name}: {verified_sha} != {sha_b}")
                for e in journal_data["entries"]:
                    if e["canonical_path"] == fpath.relative_to(repo_root).as_posix():
                        e["status"] = "replaced"
        except (OSError, Exception) as exc:  # noqa: BLE001
            print(f"CRITICAL ERROR during rollback replacement: {exc}. Restoring backups...", file=sys.stderr)
            try:
                write_rb_journal("ROLLING_BACK")
            except OSError:
                pass
            rb_failed = False
            for c_p, b_p, s_b in reversed(backups):
                try:
                    durable_replace(b_p, c_p)
                except OSError:
                    rb_failed = True
            if rb_failed:
                try:
                    write_rb_journal("ROLLBACK_FAILED")
                except OSError:
                    pass
                return 1
            try:
                write_rb_journal("ROLLED_BACK")
            except OSError:
                pass
            return 1

        write_rb_journal("COMMITTED")
        for fpath, tmp_p, bak_p, _, _, _ in staging_items:
            bak_p.unlink(missing_ok=True)
            tmp_p.unlink(missing_ok=True)
        journal_path.unlink(missing_ok=True)
        print(f"Successfully rolled back {len(staging_items)} unit(s) via verified transaction.")
        return 0
    finally:
        if lock is not None:
            lock.release()


class ExclusiveTransactionLock:
    """Exclusive filesystem lock for repository apply and rollback transactions.

    Prevents concurrent modification within the same repository.
    Records PID and timestamp in lock file. Reclaims stale locks if holding process is dead.
    """

    def __init__(self, repo_root: Path, lock_name: str = ".apply_transaction.lock") -> None:
        self.repo_root = repo_root
        self.lock_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
        self.lock_file = self.lock_dir / lock_name
        self.lock_fd: int | None = None
        self.is_acquired = False

    def acquire(self) -> bool:
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            payload = json.dumps({
                "pid": os.getpid(),
                "acquired_at": datetime.datetime.now(datetime.UTC).isoformat(),
            }).encode("utf-8")
            os.write(fd, payload)
            self.lock_fd = fd
            self.is_acquired = True
            return True
        except FileExistsError:
            try:
                data = json.loads(self.lock_file.read_text(encoding="utf-8"))
                holding_pid = data.get("pid")
                if holding_pid and isinstance(holding_pid, int) and not self._is_pid_alive(holding_pid):
                    self.lock_file.unlink(missing_ok=True)
                    fd = os.open(str(self.lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                    payload = json.dumps({
                        "pid": os.getpid(),
                        "acquired_at": datetime.datetime.now(datetime.UTC).isoformat(),
                        "reclaimed_from_stale_pid": holding_pid,
                    }).encode("utf-8")
                    os.write(fd, payload)
                    self.lock_fd = fd
                    self.is_acquired = True
                    return True
            except (OSError, json.JSONDecodeError):
                pass
            return False

    @staticmethod
    def _is_pid_alive(pid: int) -> bool:
        if pid <= 0:
            return False
        if os.name == "nt":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            process_query_limited_info = 0x1000
            h_proc = kernel32.OpenProcess(process_query_limited_info, False, pid)
            if h_proc == 0:
                return False
            try:
                exit_code = ctypes.c_ulong()
                if not kernel32.GetExitCodeProcess(h_proc, ctypes.byref(exit_code)):
                    return False
                return exit_code.value == 259  # STILL_ACTIVE
            finally:
                kernel32.CloseHandle(h_proc)
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False

    def release(self) -> None:
        if self.lock_fd is not None:
            try:
                os.close(self.lock_fd)
            except OSError:
                pass
            self.lock_fd = None
        if self.is_acquired:
            self.lock_file.unlink(missing_ok=True)
            self.is_acquired = False

    def __enter__(self) -> Self:
        if not self.acquire():
            raise RuntimeError(f"Could not acquire exclusive transaction lock at {self.lock_file}")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        self.release()


def fsync_file_and_dir(target_path: Path) -> None:
    """Flush and fsync a directory entry where supported by the operating system."""
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            flags |= os.O_DIRECTORY
        fd = os.open(str(target_path.parent), flags)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError:
        pass


def durable_write_bytes(dest_path: Path, data: bytes) -> None:
    """Write data to a file with explicit flush and os.fsync."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def durable_write_text(dest_path: Path, text: str, encoding: str = "utf-8") -> None:
    """Write text to a file with explicit flush and os.fsync."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, "w", encoding=encoding, newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())


def durable_replace(src: Path, dst: Path) -> None:
    """Replace dst with src atomically and fsync parent directory."""
    os.replace(src, dst)
    fsync_file_and_dir(dst)


def durable_write_journal(journal_path: Path, data: dict[str, Any]) -> None:
    """Write journal file durably using temporary file, fsync, atomic replace, and dir fsync."""
    temp_journal = journal_path.with_name(f"{journal_path.name}.tmp_{os.getpid()}")
    raw_json = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    durable_write_text(temp_journal, raw_json)
    durable_replace(temp_journal, journal_path)


def verify_same_filesystem(*paths: Path) -> bool:
    """Verify that all given paths reside on the same filesystem/volume."""
    if not paths:
        return True
    first = paths[0].resolve()
    first_anchor = first.anchor.lower()
    for p in paths[1:]:
        p_res = p.resolve()
        if p_res.anchor.lower() != first_anchor:
            return False
        try:
            st1 = os.stat(first.parent if first.parent.exists() else first)
            st2 = os.stat(p_res.parent if p_res.parent.exists() else p_res)
            if (
                getattr(st1, "st_dev", 0) != 0
                and getattr(st2, "st_dev", 0) != 0
                and st1.st_dev != st2.st_dev
            ):
                return False
        except OSError:
            pass
    return True


def validate_journal_confinement(
    repo_root: Path,
    j_data: dict[str, Any],
    expected_pid: int,
) -> tuple[bool, str]:
    """Strictly validate path confinement and transaction conventions for a journal prior to touching filesystem.

    Rejects:
    - empty paths
    - absolute paths outside repo_root
    - '..' traversal or null bytes
    - symlinks or junctions
    - paths violating transaction naming conventions:
      - canonical_path must be relative, under knowledge/units/, ending in .yaml
      - staging_path must be <canon_file>.tmp_apply_<pid> or .tmp_rollback_<pid> in same parent directory
      - backup_path must be <canon_file>.bak_apply_<pid> or .bak_rollback_<pid> in same parent directory
    - missing or non-hex64 hashes
    """
    entries = j_data.get("entries")
    if not isinstance(entries, list) or not entries:
        return False, "Journal contains no valid entries list."

    repo_res = repo_root.resolve()
    seen_canons: set[Path] = set()

    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            return False, f"Journal entry #{idx} is not a dictionary."

        canon_raw = e.get("canonical_path")
        if not canon_raw or not isinstance(canon_raw, str):
            return False, f"Entry #{idx} has missing or empty 'canonical_path'."

        if ".." in canon_raw or "\x00" in canon_raw:
            return False, f"Entry #{idx} 'canonical_path' contains traversal or invalid characters: '{canon_raw}'"

        canon_p = Path(canon_raw)
        if canon_p.is_absolute():
            return False, f"Entry #{idx} 'canonical_path' must be relative to repo root, got absolute: '{canon_raw}'"

        canon_full = repo_root / canon_p
        try:
            canon_res = canon_full.resolve()
        except OSError as exc:
            return False, f"Entry #{idx} canonical path resolution error: {exc}"

        if not canon_res.is_relative_to(repo_res):
            return False, f"Entry #{idx} canonical path escapes repository root: '{canon_raw}'"

        canon_rel = canon_res.relative_to(repo_res).as_posix()
        if not canon_rel.startswith("knowledge/units/"):
            return False, f"Entry #{idx} canonical path is not under 'knowledge/units/': '{canon_rel}'"
        if not canon_rel.endswith(".yaml"):
            return False, f"Entry #{idx} canonical path does not end with '.yaml': '{canon_rel}'"

        if canon_full.is_symlink():
            return False, f"Entry #{idx} canonical path is a symlink: '{canon_raw}'"

        if canon_res in seen_canons:
            return False, f"Duplicate canonical path detected in journal entry #{idx}: '{canon_rel}'"
        seen_canons.add(canon_res)

        sha_b = e.get("sha256_base")
        if not sha_b or not HEX64_REGEX.match(str(sha_b)):
            return False, f"Entry #{idx} missing or invalid sha256_base: '{sha_b}'"

        stg_raw = e.get("staging_path")
        if not stg_raw or not isinstance(stg_raw, str):
            return False, f"Entry #{idx} missing or empty 'staging_path'."
        if ".." in stg_raw or "\x00" in stg_raw:
            return False, f"Entry #{idx} 'staging_path' contains traversal or invalid characters: '{stg_raw}'"
        stg_p = Path(stg_raw)
        if not stg_p.is_absolute():
            return False, f"Entry #{idx} staging path must be absolute: '{stg_raw}'"
        stg_full = stg_p
        try:
            stg_res = stg_full.resolve()
        except OSError as exc:
            return False, f"Entry #{idx} staging path resolution error: {exc}"
        if not stg_res.is_relative_to(repo_res):
            return False, f"Entry #{idx} staging path escapes repository root: '{stg_raw}'"
        if stg_full.is_symlink():
            return False, f"Entry #{idx} staging path is a symlink: '{stg_raw}'"
        if stg_res.parent != canon_res.parent:
            return False, f"Entry #{idx} staging path parent directory does not match canonical parent."
        stg_match = re.fullmatch(rf"{re.escape(canon_res.name)}\.tmp_(apply|rollback)_(\d+)", stg_res.name)
        if stg_match is None or int(stg_match.group(2)) != expected_pid:
            return False, f"Entry #{idx} staging path does not match transaction naming convention: '{stg_res.name}'"

        bak_raw = e.get("backup_path")
        if not bak_raw or not isinstance(bak_raw, str):
            return False, f"Entry #{idx} missing or empty 'backup_path'."
        if ".." in bak_raw or "\x00" in bak_raw:
            return False, f"Entry #{idx} backup path contains traversal or invalid characters: '{bak_raw}'"
        bak_p = Path(bak_raw)
        if not bak_p.is_absolute():
            return False, f"Entry #{idx} backup path must be absolute: '{bak_raw}'"
        bak_full = bak_p
        try:
            bak_res = bak_full.resolve()
        except OSError as exc:
            return False, f"Entry #{idx} backup path resolution error: {exc}"
        if not bak_res.is_relative_to(repo_res):
            return False, f"Entry #{idx} backup path escapes repository root: '{bak_raw}'"
        if bak_full.is_symlink():
            return False, f"Entry #{idx} backup path is a symlink: '{bak_raw}'"
        if bak_res.parent != canon_res.parent:
            return False, f"Entry #{idx} backup path parent directory does not match canonical parent."
        bak_match = re.fullmatch(rf"{re.escape(canon_res.name)}\.bak_(apply|rollback)_(\d+)", bak_res.name)
        if bak_match is None or int(bak_match.group(2)) != expected_pid:
            return False, f"Entry #{idx} backup path does not match transaction naming convention: '{bak_res.name}'"
        if stg_match.group(1) != bak_match.group(1):
            return False, f"Entry #{idx} staging and backup transaction types do not match."

        if j_data.get("state") == "COMMITTED":
            sha_t = e.get("sha256_target")
            if not sha_t or not HEX64_REGEX.match(str(sha_t)):
                return False, f"Entry #{idx} missing or invalid sha256_target in COMMITTED state: '{sha_t}'"

    return True, "Path confinement verified."


def recover_from_pending_journals(repo_root: Path, _lock_held: bool = False) -> tuple[bool, str]:
    """Idempotently recover from any unfinished transactions recorded in journals.

    Handles states: INIT, PREPARING_STAGING, STAGED, REPLACING, COMMITTING, ROLLING_BACK, ROLLBACK_FAILED, COMMITTED.
    Enforces strict path confinement across all entries before any filesystem modification.
    Fails closed if any canonical file is missing or hash check fails.
    """
    if not _lock_held:
        outer_lock = ExclusiveTransactionLock(repo_root)
        if not outer_lock.acquire():
            return False, "Another transaction is active; crash recovery refused to touch its journal."
        try:
            return recover_from_pending_journals(repo_root, _lock_held=True)
        finally:
            outer_lock.release()

    journal_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    if not journal_dir.exists():
        return True, "No journal directory found."

    pending = sorted(journal_dir.glob(".apply_journal_*.json"))
    if not pending:
        return True, "No pending journals found."

    for j_path in pending:
        journal_match = re.fullmatch(r"\.apply_journal_(\d+)\.json", j_path.name)
        if journal_match is None:
            return False, f"Security confinement failed for journal '{j_path.name}': invalid journal filename"
        expected_pid = int(journal_match.group(1))
        try:
            j_data = json.loads(j_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return False, f"Corrupted journal file '{j_path.name}': {exc}"

        confinement_ok, confinement_msg = validate_journal_confinement(repo_root, j_data, expected_pid)
        if not confinement_ok:
            return False, f"Security confinement failed for journal '{j_path.name}': {confinement_msg}"

        state = j_data.get("state")
        entries = j_data["entries"]

        if state == "COMMITTED":
            for e in entries:
                canon_p = (repo_root / e["canonical_path"]).resolve()
                if not canon_p.is_file():
                    return False, f"Canonical file missing for COMMITTED state: {e['canonical_path']}"
                if sha256_bytes(canon_p.read_bytes()) != e["sha256_target"]:
                    return False, f"Target hash mismatch on canonical {canon_p.name} for COMMITTED state"

            for e in entries:
                tmp_p = Path(e["staging_path"]).resolve()
                bak_p = Path(e["backup_path"]).resolve()
                if tmp_p.is_file():
                    tmp_p.unlink(missing_ok=True)
                if bak_p.is_file():
                    bak_p.unlink(missing_ok=True)
            j_path.unlink(missing_ok=True)
            continue

        if state == "ROLLED_BACK":
            all_match = True
            for e in entries:
                canon_p = (repo_root / e["canonical_path"]).resolve()
                if not canon_p.is_file() or sha256_bytes(canon_p.read_bytes()) != e["sha256_base"]:
                    all_match = False
                    break

            if all_match:
                for e in entries:
                    tmp_p = Path(e["staging_path"]).resolve()
                    bak_p = Path(e["backup_path"]).resolve()
                    if tmp_p.is_file():
                        tmp_p.unlink(missing_ok=True)
                    if bak_p.is_file():
                        bak_p.unlink(missing_ok=True)
                j_path.unlink(missing_ok=True)
                continue
            else:
                state = "ROLLING_BACK"

        if state in (
            "INIT",
            "PREPARING_STAGING",
            "STAGED",
            "ABORTED_INVALID_OVERLAY",
            "ABORTED_DUPLICATE_STAGED_IDS",
            "ABORTED_STAGING_ERROR",
        ):
            for e in entries:
                canon_p = (repo_root / e["canonical_path"]).resolve()
                if not canon_p.is_file():
                    return False, f"Canonical file missing during pre-replace recovery: {e['canonical_path']}"
                if sha256_bytes(canon_p.read_bytes()) != e["sha256_base"]:
                    return False, f"Unexpected hash mismatch on canonical {canon_p.name} during pre-replace recovery"

            for e in entries:
                tmp_p = Path(e["staging_path"]).resolve()
                bak_p = Path(e["backup_path"]).resolve()
                if tmp_p.is_file():
                    tmp_p.unlink(missing_ok=True)
                if bak_p.is_file():
                    bak_p.unlink(missing_ok=True)
            j_path.unlink(missing_ok=True)
            continue

        if state in ("REPLACING", "COMMITTING", "ROLLING_BACK", "ROLLBACK_FAILED"):
            recovery_failed = False
            for e in entries:
                canon_p = (repo_root / e["canonical_path"]).resolve()
                bak_p = Path(e["backup_path"]).resolve()
                tmp_p = Path(e["staging_path"]).resolve()
                expected_sha = e["sha256_base"]

                if tmp_p.is_file():
                    tmp_p.unlink(missing_ok=True)

                if canon_p.is_file() and sha256_bytes(canon_p.read_bytes()) == expected_sha:
                    if bak_p.is_file():
                        bak_p.unlink(missing_ok=True)
                    continue

                if bak_p.is_file():
                    try:
                        durable_replace(bak_p, canon_p)
                        if not canon_p.is_file() or sha256_bytes(canon_p.read_bytes()) != expected_sha:
                            recovery_failed = True
                    except OSError:
                        recovery_failed = True
                else:
                    recovery_failed = True

            if recovery_failed:
                return False, f"Recovery failed for journal '{j_path.name}': one or more files could not be restored to sha256_base"

            for e in entries:
                canon_p = (repo_root / e["canonical_path"]).resolve()
                if not canon_p.is_file() or sha256_bytes(canon_p.read_bytes()) != e["sha256_base"]:
                    return False, f"Post-recovery verification failed for {e['canonical_path']}"

            j_path.unlink(missing_ok=True)
            continue

        return False, f"Unrecognized journal state '{state}' in '{j_path.name}'"

    return True, "All pending journals recovered successfully."

def execute_apply_frozen(
    repo_root: Path,
    po_approval_id: str | None,
    base_ref: str = DEFAULT_BASE_REF,
    dry_run: bool = False,
    manifest_path: Path | None = None,
    cr_path_override: Path | None = None,
    expected_scope: str = "pilot_batch_6_frozen",
    isolated_worktree: bool = False,
    _fault_injection: dict[str, Any] | None = None,
    _fault_injection_fail_at_index: int | None = None,
    _lock_held: bool = False,
) -> int:
    """Apply frozen proposals to canonical units with absolute fail-closed governance enforcement.

    Strict verification sequence:
    1. PRODUCTION PROMOTION WORKFLOW GUARD: Refuses live application (dry_run=False) outside an isolated worktree.
    2. Crash recovery check: detects and idempotently recovers from any unfinished transactions.
    3. --manifest is mandatory.
    4. po_approval_id is mandatory.
    5. full 40-character base commit hash verified against repository.
    6. Structured CR frontmatter must have:
       - schema_version == '1.0.0'
       - status == 'APPROVED_BY_PRODUCT_OWNER'
       - matching approval_id, non-empty approved_by, approved_at
       - approved_scope matching expected_scope
       - approved_base_commit_sha matching repository base commit
       - approved_review_commit_sha matching existing 40-hex Git commit in repository
       - approved_manifest_sha256 matching computed manifest hash and review commit content.
    7. Review commit tree verification: manifest and proposal contents read from approved_review_commit_sha
       via Git must match approved hashes bit-for-bit.
    8. Paths derived from immutable base tree: manifest paths used strictly for cross-validation;
       absolute paths, '..', symlinks, and duplicate destinations are strictly rejected;
       base tree files verified for matching id, type, and status 'frozen'.
    9. Staging and backup files verified on same filesystem/volume as canonical units.
    10. Each proposal validated using canonical schema (JSON Schema, naming, absolutism, evidence).
    11. Whole staging overlay validated prior to replacement.
    12. Rollback-assisted replacement with exclusive locking, early journaling, explicit fsync,
        and automatic rollback upon error. If rollback fails, sets state ROLLBACK_FAILED
        and preserves all recovery assets for forensic investigation.
    """
    # 1. PRODUCTION PROMOTION WORKFLOW GUARD
    if not dry_run and not isolated_worktree:
        print(
            "CRITICAL GOVERNANCE GUARD: Direct live apply (dry_run=False) is only permitted within an isolated Git worktree\n"
            "dedicated to the Product Owner Promotion Workflow:\n"
            "  1. Review commit: create review commit on feature branch\n"
            "  2. PO approval: PO reviews commit, signs off approved_review_commit_sha and approved_manifest_sha256\n"
            "  3. Worktree: git worktree add <temp_worktree> <approved_review_commit_sha>\n"
            "  4. Apply: python scripts/knowledge_content_pilot_tool.py --apply-frozen --isolated-worktree ...\n"
            "  5. Gates: run full test suite and validators\n"
            "  6. Promotion commit: commit verified changes in worktree\n"
            "  7. PO merge: PO merges promotion commit to primary branch.",
            file=sys.stderr,
        )
        return 1

    if not dry_run and not _lock_held:
        outer_lock = ExclusiveTransactionLock(repo_root)
        if not outer_lock.acquire():
            print("ERROR: Another transaction is currently active. Apply was not started.", file=sys.stderr)
            return 1
        try:
            return execute_apply_frozen(
                repo_root,
                po_approval_id=po_approval_id,
                base_ref=base_ref,
                dry_run=False,
                manifest_path=manifest_path,
                cr_path_override=cr_path_override,
                expected_scope=expected_scope,
                isolated_worktree=isolated_worktree,
                _fault_injection=_fault_injection,
                _fault_injection_fail_at_index=_fault_injection_fail_at_index,
                _lock_held=True,
            )
        finally:
            outer_lock.release()

    # 2. Crash recovery check before starting any transaction
    journal_dir = repo_root / "specs" / "REMEDIATION-CONTROLLED-RECOVERY"
    pending_journals = list(journal_dir.glob(".apply_journal_*.json")) if journal_dir.exists() else []
    if pending_journals:
        if dry_run:
            print(
                f"ERROR: Cannot execute dry-run with {len(pending_journals)} pending journal(s) in repository.\n"
                "Dry-run is strictly read-only and will not auto-recover, modify, or unlink any files.\n"
                "Please run 'python scripts/knowledge_content_pilot_tool.py --recover-crash' first.",
                file=sys.stderr,
            )
            return 1
        print(f"ATTENTION: Found {len(pending_journals)} pending journal(s). Running crash recovery...", file=sys.stderr)
        ok, msg = recover_from_pending_journals(repo_root, _lock_held=True)
        if not ok:
            print(f"CRITICAL: Crash recovery blocked new transaction: {msg}", file=sys.stderr)
            return 1
        print(f"Crash recovery completed: {msg}", file=sys.stderr)

    # 3. Require manifest
    if not manifest_path:
        print("ERROR: --apply-frozen rejected: missing required --manifest <path>.", file=sys.stderr)
        print("Governance rule: Applying frozen proposals requires an explicit verified manifest.", file=sys.stderr)
        return 1

    if not manifest_path.exists():
        print(f"ERROR: Manifest file '{manifest_path}' does not exist.", file=sys.stderr)
        return 1

    manifest_bytes = manifest_path.read_bytes()
    computed_manifest_sha = sha256_bytes(manifest_bytes)
    try:
        manifest_data = json.loads(manifest_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Failed to parse manifest JSON: {exc}", file=sys.stderr)
        return 1

    manifest_entries_by_id = {e["id"]: e for e in manifest_data.get("entries", []) if isinstance(e, dict) and "id" in e}

    # 4. Require PO approval ID
    if not po_approval_id or not po_approval_id.strip():
        print("ERROR: --apply-frozen rejected: missing required --po-approval-id.", file=sys.stderr)
        print("Governance rule: Frozen canonical units cannot be modified without explicit Product Owner approval.", file=sys.stderr)
        return 1

    # 5. Check full 40-character base commit
    repo_full_base = resolve_full_commit_hash(repo_root, base_ref)
    man_base = manifest_data.get("base_commit", "")
    if len(man_base) != 40:
        print(
            f"ERROR: Manifest base_commit '{man_base}' is not a full 40-character commit hash.",
            file=sys.stderr,
        )
        return 1
    if man_base != repo_full_base:
        print(
            f"ERROR: Manifest base_commit '{man_base}' does not match repository commit '{repo_full_base}'.",
            file=sys.stderr,
        )
        return 1

    # 6. Check Change Request structured metadata and review-tree integrity bindings.
    cr_path = cr_path_override or (repo_root / "governance" / "change-requests" / "CR-2026-10-19-KNOWLEDGE-CONTENT-V1.md")
    try:
        cr_meta = parse_change_request_metadata(cr_path)
    except (ValueError, TypeError, yaml.YAMLError, OSError) as exc:
        print(f"ERROR: Failed to parse Change Request structured metadata: {exc}", file=sys.stderr)
        return 1

    cr_schema_version = cr_meta.get("schema_version")
    if cr_schema_version != "1.0.0":
        print(
            f"ERROR: Change Request 'schema_version' must be '1.0.0', got '{cr_schema_version}'.",
            file=sys.stderr,
        )
        return 1

    cr_status = cr_meta.get("status")
    if cr_status != "APPROVED_BY_PRODUCT_OWNER":
        print(
            f"ERROR: Change Request status '{cr_status}' is invalid. "
            "Governance rule: Status must be strictly 'APPROVED_BY_PRODUCT_OWNER'.",
            file=sys.stderr,
        )
        return 1

    approval = cr_meta.get("approval")
    if not isinstance(approval, dict):
        print("ERROR: Change Request missing structured 'approval' metadata block.", file=sys.stderr)
        return 1

    parsed_approval_id = approval.get("approval_id")
    approved_by = approval.get("approved_by")
    approved_at = approval.get("approved_at")
    approved_scope = approval.get("approved_scope")
    approved_base_commit_sha = approval.get("approved_base_commit_sha") or approval.get("approved_commit_sha")
    approved_review_commit_sha = approval.get("approved_review_commit_sha")
    approved_manifest_sha256 = approval.get("approved_manifest_sha256")

    if not parsed_approval_id or not str(parsed_approval_id).strip():
        print("ERROR: Change Request 'approval.approval_id' is missing or empty.", file=sys.stderr)
        return 1
    if not approved_by or not str(approved_by).strip():
        print("ERROR: Change Request 'approval.approved_by' is missing or empty.", file=sys.stderr)
        return 1
    if not approved_at or not str(approved_at).strip():
        print("ERROR: Change Request 'approval.approved_at' is missing or empty.", file=sys.stderr)
        return 1

    if str(parsed_approval_id).strip() != po_approval_id.strip():
        print(
            f"ERROR: Provided --po-approval-id '{po_approval_id.strip()}' does not match "
            f"CR approval.approval_id '{str(parsed_approval_id).strip()}'.",
            file=sys.stderr,
        )
        return 1

    if not approved_scope or approved_scope != expected_scope:
        print(
            f"ERROR: Change Request 'approval.approved_scope' is '{approved_scope}', "
            f"expected '{expected_scope}'.",
            file=sys.stderr,
        )
        return 1

    if not approved_base_commit_sha or not HEX40_REGEX.match(str(approved_base_commit_sha)):
        print(
            f"ERROR: Change Request 'approval.approved_base_commit_sha' must be 40 hex chars: '{approved_base_commit_sha}'",
            file=sys.stderr,
        )
        return 1
    if str(approved_base_commit_sha) != repo_full_base:
        print(
            f"ERROR: Change Request approved_base_commit_sha '{approved_base_commit_sha}' does not match "
            f"repository base commit '{repo_full_base}'.",
            file=sys.stderr,
        )
        return 1

    if not approved_review_commit_sha or not HEX40_REGEX.match(str(approved_review_commit_sha)):
        print(
            f"ERROR: Change Request 'approval.approved_review_commit_sha' must be a valid 40 hex commit hash: '{approved_review_commit_sha}'",
            file=sys.stderr,
        )
        return 1

    try:
        subprocess.run(
            ["git", "cat-file", "-e", f"{approved_review_commit_sha}^{{commit}}"],
            cwd=str(repo_root),
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            f"ERROR: approved_review_commit_sha '{approved_review_commit_sha}' does not exist as a Git commit in repository.",
            file=sys.stderr,
        )
        return 1

    if not dry_run:
        worktree_ok, worktree_msg = verify_promotion_worktree(repo_root, str(approved_review_commit_sha))
        if not worktree_ok:
            print(f"ERROR: Invalid promotion worktree: {worktree_msg}", file=sys.stderr)
            return 1

    if not approved_manifest_sha256 or not HEX64_REGEX.match(str(approved_manifest_sha256)):
        print(
            f"ERROR: Change Request 'approval.approved_manifest_sha256' must be 64 hex chars: '{approved_manifest_sha256}'",
            file=sys.stderr,
        )
        return 1

    if computed_manifest_sha != str(approved_manifest_sha256):
        print(
            f"ERROR: Manifest SHA-256 mismatch with Change Request approval!\n"
            f"  Computed manifest hash: {computed_manifest_sha}\n"
            f"  Approved in CR frontmatter: {approved_manifest_sha256}\n"
            "Governance violation: Manifest was regenerated or modified after Product Owner approval.",
            file=sys.stderr,
        )
        return 1

    # Verify manifest content inside approved review commit
    manifest_rel = manifest_path.relative_to(repo_root).as_posix()
    try:
        res_m = subprocess.run(
            ["git", "show", f"{approved_review_commit_sha}:{manifest_rel}"],
            cwd=str(repo_root),
            capture_output=True,
            check=True,
        )
        review_manifest_sha = sha256_bytes(res_m.stdout)
    except subprocess.CalledProcessError:
        print(
            f"ERROR: Manifest file '{manifest_rel}' not found in approved review commit {approved_review_commit_sha}.",
            file=sys.stderr,
        )
        return 1

    if review_manifest_sha != str(approved_manifest_sha256):
        print(
            f"ERROR: Manifest inside approved review commit {approved_review_commit_sha} has hash {review_manifest_sha}, "
            f"differing from approved_manifest_sha256 {approved_manifest_sha256}.",
            file=sys.stderr,
        )
        return 1

    # 7. Derive canonical paths from immutable base tree and verify against manifest and schema
    base_unit_registry = load_base_unit_registry(repo_root, base_ref)
    seen_destinations: set[str] = set()
    ku_schema = load_knowledge_unit_schema()

    staging_plans: list[tuple[Path, Path, str, str, str, str, str]] = []
    # (prop_path, canon_path, content_to_write, derived_canon_rel, sha_base, sha_prop, sha_target)

    for frozen_id in FROZEN_PILOT_IDS:
        if frozen_id not in manifest_entries_by_id:
            print(f"ERROR: Frozen pilot unit '{frozen_id}' is missing from manifest entries.", file=sys.stderr)
            return 1
        m_entry = manifest_entries_by_id[frozen_id]

        sha_base = m_entry.get("sha256_base")
        sha_prop = m_entry.get("sha256_proposal")
        if not sha_base or not HEX64_REGEX.match(str(sha_base)):
            print(f"ERROR: Manifest entry {frozen_id} missing or invalid 64-hex sha256_base: {sha_base}", file=sys.stderr)
            return 1
        if not sha_prop or not HEX64_REGEX.match(str(sha_prop)):
            print(f"ERROR: Manifest entry {frozen_id} missing or invalid 64-hex sha256_proposal: {sha_prop}", file=sys.stderr)
            return 1

        if m_entry.get("target_type") != "proposal":
            print(f"ERROR: Manifest entry {frozen_id} target_type is not 'proposal'.", file=sys.stderr)
            return 1
        if m_entry.get("governance_status") != "frozen":
            print(f"ERROR: Manifest entry {frozen_id} governance_status is not 'frozen'.", file=sys.stderr)
            return 1

        # Verify proposal content directly from approved review commit
        prop_rel_target = m_entry["target_path"]
        try:
            res_p = subprocess.run(
                ["git", "show", f"{approved_review_commit_sha}:{prop_rel_target}"],
                cwd=str(repo_root),
                capture_output=True,
                check=True,
            )
            review_prop_sha = sha256_bytes(res_p.stdout)
        except subprocess.CalledProcessError:
            print(
                f"ERROR: Proposal file '{prop_rel_target}' not found in approved review commit {approved_review_commit_sha}.",
                file=sys.stderr,
            )
            return 1

        if review_prop_sha != sha_prop:
            print(
                f"ERROR: Proposal content for '{prop_rel_target}' inside review commit {approved_review_commit_sha} has hash "
                f"{review_prop_sha}, differing from manifest proposal hash {sha_prop}.",
                file=sys.stderr,
            )
            return 1

        try:
            canon_path, prop_path, derived_canon_rel, _ = sanitize_and_resolve_paths(
                repo_root, frozen_id, m_entry, base_unit_registry, seen_destinations
            )
        except (ValueError, FileNotFoundError) as p_exc:
            print(f"ERROR: Path verification failed for {frozen_id}: {p_exc}", file=sys.stderr)
            return 1

        canon_bytes = canon_path.read_bytes()
        cur_canon_sha = sha256_bytes(canon_bytes)
        if cur_canon_sha != sha_base or cur_canon_sha != base_unit_registry[frozen_id]["sha256"]:
            print(
                f"ERROR: Canonical current SHA mismatch for {frozen_id}: current {cur_canon_sha} != base {sha_base}. "
                "Canonical frozen unit was unexpectedly modified!",
                file=sys.stderr,
            )
            return 1

        prop_bytes = prop_path.read_bytes()
        cur_prop_sha = sha256_bytes(prop_bytes)
        if cur_prop_sha != sha_prop:
            print(
                f"ERROR: Proposal SHA mismatch for {frozen_id}: expected {sha_prop}, found {cur_prop_sha}",
                file=sys.stderr,
            )
            return 1

        try:
            prop_data = yaml.load(prop_bytes.decode("utf-8"), Loader=YAML_LOADER)
        except yaml.YAMLError as y_exc:
            print(f"ERROR: Failed to parse proposal YAML for {frozen_id}: {y_exc}", file=sys.stderr)
            return 1

        if prop_data.get("unit_id") != frozen_id:
            print(f"ERROR: Proposal unit_id mismatch: {prop_data.get('unit_id')} != {frozen_id}", file=sys.stderr)
            return 1
        if prop_data.get("canonical_path") != derived_canon_rel:
            print(f"ERROR: Proposal canonical_path mismatch in {frozen_id}: {prop_data.get('canonical_path')} != {derived_canon_rel}", file=sys.stderr)
            return 1
        if prop_data.get("status") != "ready_for_review":
            print(f"ERROR: Proposal status must be 'ready_for_review' in {frozen_id}", file=sys.stderr)
            return 1

        cur_v = prop_data.get("current_version")
        prop_v = prop_data.get("proposed_version")
        if not cur_v or not prop_v or tuple(map(int, prop_v.split("."))) <= tuple(map(int, cur_v.split("."))):
            print(f"ERROR: Proposal {frozen_id} proposed_version '{prop_v}' must be > current_version '{cur_v}'", file=sys.stderr)
            return 1

        unit_data = prop_data.get("proposed_unit") or {}
        if unit_data.get("id") != frozen_id:
            print(f"ERROR: Proposed unit id mismatch in {frozen_id}", file=sys.stderr)
            return 1
        if unit_data.get("version") != prop_v:
            print(f"ERROR: Proposed unit version mismatch in {frozen_id}", file=sys.stderr)
            return 1
        if unit_data.get("status") != "frozen":
            print(f"ERROR: Proposed unit status must be 'frozen' in {frozen_id}", file=sys.stderr)
            return 1

        schema_errors = validate_proposed_unit_schema(unit_data, canon_path, ku_schema)
        if schema_errors:
            print(f"ERROR: Proposed unit {frozen_id} failed canonical schema validation: {schema_errors}", file=sys.stderr)
            return 1

        abs_issues = audit_unit_absolutism(unit_data, prop_path)
        class_issues = audit_unit_evidence_classification(unit_data, prop_path, is_pilot=True)
        if abs_issues or class_issues:
            print(f"ERROR: Proposal {frozen_id} failed audit: {abs_issues + class_issues}", file=sys.stderr)
            return 1

        new_yaml = yaml.dump(unit_data, allow_unicode=True, sort_keys=False)
        content_to_write = new_yaml
        if os.name == "nt":
            content_to_write = content_to_write.replace("\r\n", "\n").replace("\n", "\r\n")
        sha_target = sha256_bytes(content_to_write.encode("utf-8"))

        staging_plans.append((prop_path, canon_path, content_to_write, derived_canon_rel, str(sha_base), str(sha_prop), sha_target))

    # 8. Filesystem check
    pid = os.getpid()
    for _, canon_p, _, _, _, _, _ in staging_plans:
        tmp_p = canon_p.with_name(f"{canon_p.name}.tmp_apply_{pid}")
        bak_p = canon_p.with_name(f"{canon_p.name}.bak_apply_{pid}")
        if not verify_same_filesystem(canon_p, tmp_p, bak_p):
            print(f"ERROR: Filesystem mismatch: {canon_p} and staging/backup reside on different filesystems.", file=sys.stderr)
            return 1

    if dry_run:
        print(f"[DRY-RUN] Pre-validation passed for all {len(staging_plans)} frozen proposals. Ready to execute rollback-assisted replacement.")
        return 0

    # 9. Exclusive Lock & Durable Early Journaling
    lock: ExclusiveTransactionLock | None = None

    try:
        journal_dir.mkdir(parents=True, exist_ok=True)
        journal_path = journal_dir / f".apply_journal_{pid}.json"

        journal_data: dict[str, Any] = {
            "transaction_id": f"TXN-APPLY-{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d%H%M%S')}-{pid}",
            "state": "INIT",
            "po_approval_id": po_approval_id,
            "base_commit": repo_full_base,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "entries": [],
        }

        staging_temp_files: list[tuple[Path, Path, Path, Path, str, str, str]] = []
        for prop_path, canon_path, content, rel_canon, sha_b, sha_p, sha_t in staging_plans:
            tmp_path = canon_path.with_name(f"{canon_path.name}.tmp_apply_{pid}")
            bak_path = canon_path.with_name(f"{canon_path.name}.bak_apply_{pid}")
            staging_temp_files.append((prop_path, canon_path, tmp_path, bak_path, sha_b, sha_p, sha_t))
            journal_data["entries"].append({
                "canonical_path": rel_canon,
                "staging_path": str(tmp_path),
                "backup_path": str(bak_path),
                "sha256_base": sha_b,
                "sha256_proposal": sha_p,
                "sha256_target": sha_t,
                "status": "planned",
            })

        def write_journal(state: str) -> None:
            journal_data["state"] = state
            journal_data["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()
            if _fault_injection and _fault_injection.get("fail_at_journal_write"):
                raise OSError("Simulated fault injection: failure writing journal")
            durable_write_journal(journal_path, journal_data)

        # Early journaling before any temp files are written
        try:
            write_journal("PREPARING_STAGING")
            for idx, (prop_path, canon_path, tmp_path, bak_path, sha_b, sha_p, sha_t) in enumerate(staging_temp_files):
                content = staging_plans[idx][2]
                durable_write_text(tmp_path, content)
                for e in journal_data["entries"]:
                    if e["canonical_path"] == canon_path.relative_to(repo_root).as_posix():
                        e["status"] = "staged"
            write_journal("STAGED")
            if _fault_injection and _fault_injection.get("hard_exit_after_staged"):
                os._exit(42)

            # 10. Validate whole staging overlay prior to replacing any canonical file
            staged_ids: set[str] = set()
            for _, canon_p, tmp_p, _, _, _, _ in staging_temp_files:
                staged_data = yaml.load(tmp_p.read_text(encoding="utf-8"), Loader=YAML_LOADER)
                overlay_errors = validate_proposed_unit_schema(staged_data, canon_p, ku_schema)
                if overlay_errors:
                    print(f"ERROR: Staged overlay validation failed for {canon_p.name}: {overlay_errors}", file=sys.stderr)
                    write_journal("ABORTED_INVALID_OVERLAY")
                    for _, _, t_p, _, _, _, _ in staging_temp_files:
                        t_p.unlink(missing_ok=True)
                    journal_path.unlink(missing_ok=True)
                    return 1
                staged_ids.add(staged_data["id"])

            if len(staged_ids) != len(staging_temp_files):
                print("ERROR: Staged overlay contains duplicate unit IDs.", file=sys.stderr)
                write_journal("ABORTED_DUPLICATE_STAGED_IDS")
                for _, _, t_p, _, _, _, _ in staging_temp_files:
                    t_p.unlink(missing_ok=True)
                journal_path.unlink(missing_ok=True)
                return 1

        except (yaml.YAMLError, OSError) as exc:
            print(f"ERROR: Staging preparation failed: {exc}. Aborting with 0 files modified.", file=sys.stderr)
            try:
                write_journal("ABORTED_STAGING_ERROR")
            except OSError:
                pass
            for _, _, tmp_p, _, _, _, _ in staging_temp_files:
                tmp_p.unlink(missing_ok=True)
            journal_path.unlink(missing_ok=True)
            return 1

        # 11. Rollback-assisted replacement with durable transactions and fault injection hooks
        write_journal("REPLACING")
        backups: list[tuple[Path, Path, str]] = []
        try:
            for idx, (prop_path, canon_path, tmp_path, bak_path, sha_b, sha_p, sha_t) in enumerate(staging_temp_files):
                if _fault_injection and _fault_injection.get("fail_before_replace_idx") == idx:
                    raise OSError(f"Simulated fault injection before replace of index {idx} ({canon_path.name})")
                if _fault_injection_fail_at_index is not None and idx == _fault_injection_fail_at_index:
                    raise OSError(f"Simulated fault injection at step {idx} ({canon_path.name})")

                durable_write_bytes(bak_path, canon_path.read_bytes())
                backups.append((canon_path, bak_path, sha_b))
                durable_replace(tmp_path, canon_path)

                for e in journal_data["entries"]:
                    if e["canonical_path"] == canon_path.relative_to(repo_root).as_posix():
                        e["status"] = "replaced"
                write_journal("REPLACING")

                if _fault_injection and _fault_injection.get("fail_after_replace_idx") == idx:
                    raise OSError(f"Simulated fault injection after replace of index {idx} ({canon_path.name})")
                if _fault_injection and _fault_injection.get("hard_exit_after_replace_idx") == idx:
                    os._exit(42)

                yaml.load(canon_path.read_text(encoding="utf-8"), Loader=YAML_LOADER)

        except (yaml.YAMLError, OSError, Exception) as exc:  # noqa: BLE001
            print(f"CRITICAL ERROR during rollback-assisted replacement: {exc}. Rolling back all applied files...", file=sys.stderr)
            try:
                write_journal("ROLLING_BACK")
            except OSError:
                pass
            rollback_failed = False

            for r_idx, (c_path, b_path, orig_sha) in enumerate(reversed(backups)):
                try:
                    if not b_path.exists():
                        print(f"FATAL: Backup file missing for {c_path}: {b_path}", file=sys.stderr)
                        rollback_failed = True
                        continue

                    if _fault_injection and _fault_injection.get("fail_at_restore_idx") == r_idx:
                        raise OSError(f"Simulated fault injection during restore of {b_path.name}")

                    durable_replace(b_path, c_path)
                    restored_sha = sha256_bytes(c_path.read_bytes())

                    if _fault_injection and _fault_injection.get("fail_at_hash_verification"):
                        restored_sha = "0" * 64

                    if restored_sha != orig_sha:
                        print(f"FATAL: Post-rollback hash mismatch for {c_path}: {restored_sha} != {orig_sha}", file=sys.stderr)
                        rollback_failed = True
                    else:
                        for e in journal_data["entries"]:
                            if e["canonical_path"] == c_path.relative_to(repo_root).as_posix():
                                e["status"] = "restored"
                except OSError as rb_exc:
                    print(f"FATAL: Rollback failed for {c_path}: {rb_exc}", file=sys.stderr)
                    rollback_failed = True

            if rollback_failed:
                try:
                    write_journal("ROLLBACK_FAILED")
                except OSError:
                    pass
                print(
                    "CRITICAL: Rollback failed to restore clean base state! "
                    "Preserving all journal, backup, and staging files for manual forensic inspection.",
                    file=sys.stderr,
                )
                return 1

            try:
                write_journal("ROLLED_BACK")
            except OSError:
                pass
            for _, _, tmp_p, bak_p, _, _, _ in staging_temp_files:
                tmp_p.unlink(missing_ok=True)
                bak_p.unlink(missing_ok=True)
            return 1

        # Phase C: Success cleanup
        write_journal("COMMITTED")
        if _fault_injection and _fault_injection.get("hard_exit_after_committed"):
            os._exit(42)
        if _fault_injection and _fault_injection.get("fail_at_cleanup"):
            print("ERROR: Simulated cleanup failure after commit.", file=sys.stderr)
            return 1

        for _, _, _, bak_path, _, _, _ in staging_temp_files:
            bak_path.unlink(missing_ok=True)
        for _, _, tmp_p, _, _, _, _ in staging_temp_files:
            tmp_p.unlink(missing_ok=True)
        journal_path.unlink(missing_ok=True)

        print(f"Successfully applied all {len(staging_plans)} approved frozen proposals via rollback-assisted replacement.")
        return 0
    finally:
        if lock is not None:
            lock.release()


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT, help="Target repository root path.")
    parser.add_argument("--cr-path", type=Path, default=None, help="Override Change Request path.")
    parser.add_argument("--audit-only", action="store_true", help="Audit repository against banned and absolutist phrases.")
    parser.add_argument("--dry-run", action="store_true", help="Compute manifest and planned actions without touching disk.")
    parser.add_argument("--manifest", type=Path, default=None, help="Path to write or read change-control manifest JSON.")
    parser.add_argument("--base-ref", default=DEFAULT_BASE_REF, help="Base commit reference (default: full 40-char commit hash of 27a34bc).")
    parser.add_argument("--apply-draft", action="store_true", help="Verify and apply draft pilots to canonical units.")
    parser.add_argument("--apply-frozen", action="store_true", help="Apply frozen proposals to canonical units (fails closed without PO approval).")
    parser.add_argument("--po-approval-id", default=None, help="Explicit PO approval ID required for --apply-frozen.")
    parser.add_argument("--rollback", action="store_true", help="Rollback canonical units to base commit using manifest hashes.")
    parser.add_argument("--confirm-rollback", action="store_true", help="Required confirmation flag to execute live rollback.")
    parser.add_argument("--recover-crash", action="store_true", help="Idempotently recover from any unfinished transactions recorded in journals.")
    parser.add_argument("--isolated-worktree", action="store_true", help="Required flag acknowledging execution in an isolated PO Promotion Workflow worktree.")
    parser.add_argument("--fault-injection-json", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    target_root = args.repo_root

    if args.recover_crash:
        ok, msg = recover_from_pending_journals(target_root)
        if not ok:
            print(f"CRITICAL: Crash recovery failed: {msg}", file=sys.stderr)
            return 1
        print(f"Crash recovery successful: {msg}")
        return 0

    if args.audit_only:
        strict_issues, telemetry_notes = execute_audit(target_root)
        if strict_issues:
            for issue in strict_issues:
                print(f"- [STRICT-FAIL] {issue}", file=sys.stderr)
            print(f"\nAudit failed with {len(strict_issues)} strict issue(s).", file=sys.stderr)
            return 1
        print("Audit passed: all 12 pilot units (6 draft canonical + 6 frozen proposals) and evidence levels are valid.")
        if telemetry_notes:
            print(f"(Informational: repository contains {len(telemetry_notes)} non-pilot telemetry note(s) recorded in CR inventory)")
        return 0

    if args.rollback:
        if not args.confirm_rollback and not args.dry_run:
            print("ERROR: --rollback requires --confirm-rollback or --dry-run flag.", file=sys.stderr)
            return 1
        return execute_rollback(
            target_root,
            base_ref=args.base_ref,
            dry_run=args.dry_run,
            manifest_path=args.manifest,
        )

    if args.apply_frozen:
        _fault_injection = json.loads(args.fault_injection_json) if args.fault_injection_json else None
        return execute_apply_frozen(
            target_root,
            po_approval_id=args.po_approval_id,
            base_ref=args.base_ref,
            dry_run=args.dry_run,
            manifest_path=args.manifest,
            cr_path_override=args.cr_path,
            isolated_worktree=args.isolated_worktree,
            _fault_injection=_fault_injection,
        )

    manifest = generate_manifest(target_root, args.base_ref)

    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Manifest written: {args.manifest}")

    print(
        json.dumps(
            {
                "snapshot_id": manifest["snapshot_id"],
                "base_commit": manifest["base_commit"],
                "total_target_units": manifest["total_target_units"],
                "frozen_count": manifest["frozen_count"],
                "draft_count": manifest["draft_count"],
                "pilot_count": manifest["pilot_count"],
                "draft_pilot_count": manifest["draft_pilot_count"],
                "frozen_pilot_count": manifest["frozen_pilot_count"],
                "working_tree_fingerprint": manifest["working_tree_fingerprint"][:16] + "...",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
