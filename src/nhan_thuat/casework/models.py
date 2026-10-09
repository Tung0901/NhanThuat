"""Contracts for an operational case file.

Case files are live work records. They deliberately remain separate from the
historical ``CaseStudy`` model and from canonical knowledge content.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

CASE_STATUSES = frozenset({"open", "review", "decided", "closed", "archived"})
EPISTEMIC_STATUSES = frozenset(
    {"observed_fact", "user_claim", "assumption", "engine_inference", "simulation", "recommendation"}
)
ARTIFACT_TYPES = frozenset({"analysis", "diagnostic", "recommendation", "simulation", "decision"})


def utcnow_iso() -> str:
    return datetime.now(UTC).replace(tzinfo=None).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


@dataclass(frozen=True)
class EpistemicClaim:
    """A statement with an explicit epistemic status."""

    claim_id: str
    statement: str
    status: str
    source: str = "user"
    confidence: float | None = None
    knowledge_refs: tuple[str, ...] = ()

    VALID_STATUSES: ClassVar[frozenset[str]] = EPISTEMIC_STATUSES

    def __post_init__(self) -> None:
        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Unsupported epistemic status: {self.status}")
        if not self.statement.strip():
            raise ValueError("Claim statement must not be empty")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("Claim confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseFile:
    schema_version: str
    case_id: str
    revision: int
    title: str
    situation_statement: str
    objective: str
    status: str
    owner_user_id: str
    org_id: str
    sensitivity: str = "internal"
    domain_tags: list[str] = field(default_factory=list)
    stakeholders: list[str] = field(default_factory=list)
    known_facts: list[EpistemicClaim] = field(default_factory=list)
    assumptions: list[EpistemicClaim] = field(default_factory=list)
    unknowns: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    risk_if_wrong: str = ""
    observation_signals: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow_iso)
    updated_at: str = field(default_factory=utcnow_iso)

    def __post_init__(self) -> None:
        if self.status not in CASE_STATUSES:
            raise ValueError(f"Unsupported case status: {self.status}")
        if self.revision < 1:
            raise ValueError("Case revision must be at least 1")
        for name in ("case_id", "title", "owner_user_id", "org_id"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must not be empty")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["known_facts"] = [claim.to_dict() for claim in self.known_facts]
        result["assumptions"] = [claim.to_dict() for claim in self.assumptions]
        return result


@dataclass
class CaseArtifact:
    artifact_id: str
    case_id: str
    case_revision: int
    artifact_type: str
    source_module: str
    module_version: str
    payload_schema_version: str
    input_hash: str
    summary: str
    payload: dict[str, Any] = field(default_factory=dict)
    knowledge_refs: list[str] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None
    limitations: list[str] = field(default_factory=list)
    created_by: str = "system"
    created_at: str = field(default_factory=utcnow_iso)
    stale: bool = False

    def __post_init__(self) -> None:
        if self.artifact_type not in ARTIFACT_TYPES:
            raise ValueError(f"Unsupported artifact type: {self.artifact_type}")
        if self.case_revision < 1:
            raise ValueError("Artifact case revision must be at least 1")
        if self.confidence is not None and not 0 <= self.confidence <= 1:
            raise ValueError("Artifact confidence must be between 0 and 1")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def claim_from_dict(value: dict[str, Any]) -> EpistemicClaim:
    return EpistemicClaim(
        claim_id=str(value["claim_id"]),
        statement=str(value["statement"]),
        status=str(value["status"]),
        source=str(value.get("source", "user")),
        confidence=value.get("confidence"),
        knowledge_refs=tuple(value.get("knowledge_refs", ())),
    )
