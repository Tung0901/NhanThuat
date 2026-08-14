"""
Executable NhanThuat Knowledge Engine.
Single Source of Truth loader, RAG scanner, and graph traverser for 274 Knowledge Units and Custom Company Documents.
"""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from nhan_thuat.loader import iter_documents, load_document
from nhan_thuat.validator import validate_document

FALLBACK_INSUFFICIENT_KNOWLEDGE = "INSUFFICIENT_VERIFIED_KNOWLEDGE"


def calculate_unit_checksum(data: Dict[str, Any]) -> str:
    """Calculate SHA-256 checksum for a knowledge unit payload."""
    serialized = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


@dataclass
class IndexedUnit:
    """Indexed Knowledge Unit with metadata, raw payload, and dependency pointers."""

    unit_id: str
    unit_type: str
    title: str
    domain: str
    version: str
    status: str
    tags: List[str]
    raw_data: Dict[str, Any]
    file_path: str
    checksum: str
    direct_dependencies: List[str] = field(default_factory=list)


@dataclass
class CustomDocUnit:
    """Indexed Custom Company Document (RAG Document)."""

    doc_id: str
    title: str
    file_path: str
    content: str
    checksum: str


class KnowledgeEngine:
    """
    Executable NhanThuat Knowledge Engine.
    Single Source of Truth loader and graph traverser for 274 Knowledge Units + Custom RAG Pipeline.
    """

    def __init__(self, root_dir: Optional[str | Path] = None, schema_path: Optional[str | Path] = None) -> None:
        repo_root = Path(__file__).resolve().parent.parent.parent
        if root_dir is None:
            root_dir = repo_root / "knowledge" / "units"
        if schema_path is None:
            schema_path = repo_root / "schemas" / "knowledge-unit.schema.json"

        self.repo_root = repo_root
        self.root_dir = Path(root_dir)
        self.schema_path = Path(schema_path)

        # Load Schema
        if self.schema_path.exists():
            self.unit_schema = load_document(self.schema_path)
        else:
            self.unit_schema = {}

        # Primary Index Maps
        self.units_by_id: Dict[str, IndexedUnit] = {}
        self.units_by_type: Dict[str, List[IndexedUnit]] = {}
        self.units_by_domain: Dict[str, List[IndexedUnit]] = {}
        self.units_by_tag: Dict[str, List[IndexedUnit]] = {}
        self.units_by_status: Dict[str, List[IndexedUnit]] = {}

        # Custom RAG Docs Index Map
        self.custom_docs: Dict[str, CustomDocUnit] = {}

        # Load and Index Knowledge Base + Custom Docs
        self.reload()

    def get_unit(self, unit_id: str) -> Optional[IndexedUnit]:
        """Fetch IndexedUnit by ID."""
        return self.units_by_id.get(unit_id)

    def scan_custom_documents(self) -> None:
        """Scan docs/knowledge/custom_docs/ and docs/departments/templates/ for RAG ingestion."""
        self.custom_docs.clear()

        custom_dirs = [
            self.repo_root / "docs" / "knowledge" / "custom_docs",
            self.repo_root / "docs" / "departments" / "templates",
        ]

        for cdir in custom_dirs:
            if not cdir.exists():
                continue
            for ext in ("*.md", "*.txt", "*.yaml", "*.yml", "*.json"):
                for p in cdir.rglob(ext):
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        doc_id = p.stem.upper()
                        checksum = f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"
                        title = p.name.replace("_", " ").replace("-", " ")
                        if text.startswith("# "):
                            title = text.splitlines()[0].replace("# ", "").strip()

                        self.custom_docs[doc_id] = CustomDocUnit(
                            doc_id=doc_id,
                            title=title,
                            file_path=str(p),
                            content=text,
                            checksum=checksum,
                        )
                    except Exception:
                        pass

    def reload(self) -> None:
        """Load, validate, and index all knowledge units from root_dir and custom docs."""
        self.units_by_id.clear()
        self.units_by_type.clear()
        self.units_by_domain.clear()
        self.units_by_tag.clear()
        self.units_by_status.clear()

        doc_paths = iter_documents(self.root_dir)
        if doc_paths:
            for path in doc_paths:
                # 1. Load YAML/JSON document
                data = load_document(path)

                # 2. Strict Schema Validation (No silent skipping!)
                if self.unit_schema:
                    errors = validate_document(data, self.unit_schema)
                    if errors:
                        errors_str = "; ".join(errors)
                        raise ValueError(f"Schema validation failed for '{path}': {errors_str}")

                unit_id = data.get("id")
                if not unit_id:
                    raise ValueError(f"Missing required 'id' in document '{path}'")

                # 3. Duplicate ID Rejection
                if unit_id in self.units_by_id:
                    existing_file = self.units_by_id[unit_id].file_path
                    raise ValueError(
                        f"Duplicate Knowledge Unit ID '{unit_id}' found in '{path}' (Already registered in '{existing_file}')"
                    )

                # Extract fields
                unit_type = data.get("type", "unknown")
                title = data.get("title", "")
                domain = data.get("primary_domain") or data.get("domain", "unassigned")
                version = str(data.get("version", "1.0.0"))
                status = data.get("status", "draft")
                tags = [str(t) for t in data.get("tags", [])]

                # Extract direct dependencies
                direct_deps = self._extract_direct_dependencies(data)

                # Calculate SHA-256 Checksum
                checksum = calculate_unit_checksum(data)

                indexed_unit = IndexedUnit(
                    unit_id=unit_id,
                    unit_type=unit_type,
                    title=title,
                    domain=domain,
                    version=version,
                    status=status,
                    tags=tags,
                    raw_data=data,
                    file_path=str(path),
                    checksum=checksum,
                    direct_dependencies=direct_deps,
                )

                # Register in primary index
                self.units_by_id[unit_id] = indexed_unit

                # Register in auxiliary indexes
                self.units_by_type.setdefault(unit_type, []).append(indexed_unit)
                self.units_by_domain.setdefault(domain, []).append(indexed_unit)
                self.units_by_status.setdefault(status, []).append(indexed_unit)
                for tag in tags:
                    self.units_by_tag.setdefault(tag.lower(), []).append(indexed_unit)

            # Verify graph integrity
            self.detect_missing_references()
            self.detect_circular_dependencies()

        # Scan Custom Company RAG Documents
        self.scan_custom_documents()

    def query_custom_documents(self, query_text: str, top_k: int = 2) -> List[CustomDocUnit]:
        """Search company custom documents/contracts/SOPs matching query keywords."""
        if not self.custom_docs:
            return []

        text_lower = query_text.lower()
        tokens = [t.strip() for t in text_lower.split() if len(t.strip()) > 1]

        scores: List[Tuple[int, CustomDocUnit]] = []
        for doc in self.custom_docs.values():
            score = 0
            doc_text = f"{doc.title} {doc.content}".lower()
            for token in tokens:
                if token in doc_text:
                    score += 2
                if token in doc.title.lower():
                    score += 5
            if score > 0:
                scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scores[:top_k]]

    def _extract_direct_dependencies(self, data: Dict[str, Any]) -> List[str]:
        """Extract referenced unit IDs from relationships, related_units, depends_on, prerequisites."""
        deps: Set[str] = set()

        for rel in data.get("related_units", []):
            if isinstance(rel, str):
                deps.add(rel)
            elif isinstance(rel, dict) and "id" in rel:
                deps.add(rel["id"])

        for dep in data.get("depends_on", []):
            if isinstance(dep, str):
                deps.add(dep)

        for req in data.get("prerequisites", []):
            if isinstance(req, str):
                deps.add(req)

        relationships = data.get("relationships", {})
        if isinstance(relationships, dict):
            for rel_type, rel_target in relationships.items():
                if isinstance(rel_target, list):
                    for item in rel_target:
                        if isinstance(item, str):
                            deps.add(item)
                        elif isinstance(item, dict) and "id" in item:
                            deps.add(item["id"])
                elif isinstance(rel_target, str):
                    deps.add(rel_target)

        return sorted(list(deps))

    def detect_missing_references(self) -> List[str]:
        """Verify all direct dependencies exist in units_by_id."""
        missing = []
        for unit_id, unit in self.units_by_id.items():
            for dep_id in unit.direct_dependencies:
                if dep_id not in self.units_by_id:
                    missing.append(f"Unit '{unit_id}' references missing unit '{dep_id}'")
        return missing

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Verify graph has no circular dependency cycles."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(curr_id: str, path: List[str]):
            visited.add(curr_id)
            rec_stack.add(curr_id)

            unit = self.units_by_id.get(curr_id)
            if unit:
                for neighbor in unit.direct_dependencies:
                    if neighbor not in self.units_by_id:
                        continue
                    if neighbor not in visited:
                        dfs(neighbor, path + [neighbor])
                    elif neighbor in rec_stack:
                        cycle_path = path[path.index(neighbor):] + [neighbor]
                        cycles.append(cycle_path)

            rec_stack.remove(curr_id)

        for uid in self.units_by_id:
            if uid not in visited:
                dfs(uid, [uid])

        if cycles:
            cycles_str = " | ".join([" -> ".join(c) for c in cycles])
            raise ValueError(f"Circular dependency detected in knowledge graph: {cycles_str}")

        return cycles

    def get_transitive_dependencies(self, unit_id: str, max_depth: int = 10) -> List[str]:
        """Resolve all transitive dependencies using DFS up to max_depth."""
        if unit_id not in self.units_by_id:
            return []

        visited: Set[str] = set()

        def dfs(curr_id: str, depth: int):
            if depth > max_depth or curr_id in visited:
                return
            visited.add(curr_id)
            unit = self.units_by_id.get(curr_id)
            if unit:
                for dep in unit.direct_dependencies:
                    if dep in self.units_by_id:
                        dfs(dep, depth + 1)

        unit = self.units_by_id[unit_id]
        for direct in unit.direct_dependencies:
            if direct in self.units_by_id:
                dfs(direct, 1)

        return sorted(list(visited))

    def query(
        self,
        domain: Optional[str] = None,
        unit_type: Optional[str] = None,
        tag: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[IndexedUnit]:
        """Query knowledge units matching filters."""
        candidates = list(self.units_by_id.values())

        if domain:
            candidates = [u for u in candidates if u.domain.lower() == domain.lower()]
        if unit_type:
            candidates = [u for u in candidates if u.unit_type.lower() == unit_type.lower()]
        if status:
            candidates = [u for u in candidates if u.status.lower() == status.lower()]
        if tag:
            candidates = [u for u in candidates if tag.lower() in [t.lower() for t in u.tags]]

        return candidates

    def resolve_latest_active_unit(self, unit_id: str) -> Dict[str, Any]:
        """Resolve unit obeying LATESTAT_APPROVED_ACTIVE_COMPATIBLE rules."""
        unit = self.units_by_id.get(unit_id)
        if not unit:
            return {
                "status": "error",
                "fallback_code": FALLBACK_INSUFFICIENT_KNOWLEDGE,
                "message": f"Knowledge Unit '{unit_id}' not found in active registry.",
            }

        if unit.status.lower() not in ("approved", "active", "frozen"):
            return {
                "status": "error",
                "fallback_code": FALLBACK_INSUFFICIENT_KNOWLEDGE,
                "message": f"Knowledge Unit '{unit_id}' has unverified status '{unit.status}'.",
            }

        return {
            "status": "success",
            "unit": unit,
            "provenance_checksum": unit.checksum,
        }
