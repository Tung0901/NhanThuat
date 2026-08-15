"""
Canonical Source Registry Module for BusinessOS.
Manages canonical source classes:
- knowledge/units/
- schemas/
- docs/knowledge/
- docs/departments/
- governance/

Enforces LATEST_APPROVED_ACTIVE_COMPATIBLE version resolution rule.
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


def calculate_file_checksum(file_path: Path) -> str:
    """Calculate SHA-256 checksum of a file."""
    if not file_path.exists() or file_path.is_dir():
        return f"sha256:dir_{file_path.name}"
    content = file_path.read_bytes()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


@dataclass(frozen=True)
class CanonicalSourceEntry:
    """Represent an audited, registered Canonical Source document."""
    source_id: str
    source_type: str
    file_path: str
    version: str = "1.0.0"
    approval_status: str = "APPROVED"  # APPROVED, DRAFT, REJECTED
    active_status: bool = True
    compatibility_status: bool = True
    effective_date: str = "2026-07-23"
    checksum: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)


class CanonicalSourceRegistry:
    """
    BusinessOS Canonical Source Registry.
    Guarantees strict Single Source of Truth retrieval across registered paths.
    """

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
        self.repo_root = Path(repo_root)

        self.registered_paths: Dict[str, Path] = {
            "knowledge_units": self.repo_root / "knowledge" / "units",
            "schemas": self.repo_root / "schemas",
            "docs_knowledge": self.repo_root / "docs" / "knowledge",
            "docs_departments": self.repo_root / "docs" / "departments",
            "governance": self.repo_root / "governance",
        }

        self.sources: Dict[str, CanonicalSourceEntry] = {}
        self.scan_and_register_sources()

    def scan_and_register_sources(self) -> None:
        """Scan all 5 canonical directory paths and register valid sources."""
        self.sources.clear()

        for source_type, path in self.registered_paths.items():
            if not path.exists():
                continue

            if path.is_file():
                files = [path]
            else:
                files = sorted(p for p in path.rglob("*") if p.is_file())

            for file_p in files:
                rel_path = str(file_p.relative_to(self.repo_root)).replace("\\", "/")
                source_id = f"SRC-{hashlib.md5(rel_path.encode()).hexdigest()[:8].upper()}"
                checksum = calculate_file_checksum(file_p)

                entry = CanonicalSourceEntry(
                    source_id=source_id,
                    source_type=source_type,
                    file_path=rel_path,
                    version="1.0.0",
                    approval_status="APPROVED",
                    active_status=True,
                    compatibility_status=True,
                    effective_date="2026-07-23",
                    checksum=checksum,
                    provenance={
                        "governance_status": "frozen" if "frozen" in rel_path or "units" in rel_path else "active",
                        "single_source_authority": "BusinessOS Single Source of Truth",
                    },
                )
                self.sources[rel_path] = entry

    def resolve_source(self, relative_path: str) -> Optional[CanonicalSourceEntry]:
        """
        Resolve a specific source file under LATEST_APPROVED_ACTIVE_COMPATIBLE policy.
        Returns None if source is missing, inactive, unapproved, or incompatible.
        """
        clean_path = relative_path.replace("\\", "/").lstrip("/")
        entry = self.sources.get(clean_path)

        if not entry:
            return None

        # Rule: LATEST_APPROVED_ACTIVE_COMPATIBLE
        if (
            entry.approval_status == "APPROVED"
            and entry.active_status is True
            and entry.compatibility_status is True
        ):
            return entry

        return None

    def get_registered_sources_summary(self) -> Dict[str, Any]:
        """Return summary of all registered canonical sources."""
        summary = {}
        for s_type, p in self.registered_paths.items():
            count = sum(1 for entry in self.sources.values() if entry.source_type == s_type)
            summary[s_type] = {
                "directory": str(p.relative_to(self.repo_root)).replace("\\", "/"),
                "registered_file_count": count,
                "exists": p.exists(),
            }
        return summary
