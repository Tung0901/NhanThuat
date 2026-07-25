"""
SalesOS Domain Contracts and Payload Schemas.
Defines immutable/strongly validated domain contracts for Lead Intake and Assignment.
Every governed object contains object_id, version, status, created_at, updated_at, source, and checksum.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def generate_checksum(payload_dict: Dict[str, Any]) -> str:
    """Generate deterministic SHA-256 integrity checksum for a payload dictionary."""
    clean_dict = {k: v for k, v in payload_dict.items() if k != "checksum"}
    encoded = json.dumps(clean_dict, sort_keys=True, default=str).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Lead:
    object_id: str
    customer_name: str
    normalized_phone: str
    raw_phone: str
    lead_source: str
    product_interest: str
    notes: Optional[str] = ""
    status: str = "NEW"  # NEW, ASSIGNED, DUPLICATE, QUALIFIED
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    source: str = "salesos_lead_intake"
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            data = asdict(self)
            data["checksum"] = ""
            calc_checksum = generate_checksum(data)
            object.__setattr__(self, "checksum", calc_checksum)


@dataclass(frozen=True)
class Customer:
    object_id: str
    name: str
    phone: str
    status: str = "ACTIVE"
    email: Optional[str] = None
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    source: str = "salesos_lead_intake"
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            data = asdict(self)
            data["checksum"] = ""
            calc_checksum = generate_checksum(data)
            object.__setattr__(self, "checksum", calc_checksum)


@dataclass(frozen=True)
class SalesUser:
    object_id: str
    name: str
    role: str = "sales_representative"
    status: str = "ACTIVE"
    assigned_lead_count: int = 0
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class Assignment:
    object_id: str
    lead_id: str
    assigned_to_user_id: str
    assigned_to_user_name: str
    policy_applied: str = "DETERMINISTIC_ROUND_ROBIN"
    status: str = "ASSIGNED"
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    source: str = "salesos_assignment_policy"
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            data = asdict(self)
            data["checksum"] = ""
            calc_checksum = generate_checksum(data)
            object.__setattr__(self, "checksum", calc_checksum)


@dataclass(frozen=True)
class NextAction:
    object_id: str
    lead_id: str
    action_type: str
    description: str
    priority: str = "HIGH"
    due_hours: int = 24
    backed_by_knowledge_units: List[str] = field(default_factory=lambda: ["NT-LAW-0054", "NT-PRINCIPLE-0086"])
    status: str = "PENDING"
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)


@dataclass(frozen=True)
class AuditEvent:
    object_id: str
    event_type: str
    aggregate_id: str
    payload: Dict[str, Any]
    actor_id: str = "SALESOS-PERSONA-001"
    status: str = "PUBLISHED"
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    source: str = "salesos_audit"
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            data = asdict(self)
            data["checksum"] = ""
            calc_checksum = generate_checksum(data)
            object.__setattr__(self, "checksum", calc_checksum)


@dataclass(frozen=True)
class ProvenanceTrace:
    object_id: str
    workflow_id: str
    capability_id: str = "SALESOS-CAP-001"
    persona_id: str = "SALESOS-PERSONA-001"
    knowledge_citations: List[str] = field(default_factory=lambda: ["NT-LAW-0054", "NT-PRINCIPLE-0086"])
    skill_pipeline: List[str] = field(default_factory=lambda: [
        "SALESOS-SKILL-001",
        "SALESOS-SKILL-002",
        "SALESOS-SKILL-003",
        "SALESOS-SKILL-004",
        "SALESOS-SKILL-005",
        "SALESOS-SKILL-006",
        "SALESOS-SKILL-007",
    ])
    lenses_applied: List[str] = field(default_factory=lambda: ["LENS-RHETORIC", "LENS-CONFUCIAN"])
    confidence_score: float = 0.95
    status: str = "RECORDED"
    version: str = "v1.0"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    source: str = "salesos_provenance"
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            data = asdict(self)
            data["checksum"] = ""
            calc_checksum = generate_checksum(data)
            object.__setattr__(self, "checksum", calc_checksum)


@dataclass(frozen=True)
class WorkflowResult:
    status: str  # SUCCESS, INSUFFICIENT_VERIFIED_KNOWLEDGE, VALIDATION_ERROR, DUPLICATE_REJECTED
    lead: Optional[Lead] = None
    customer: Optional[Customer] = None
    assignment: Optional[Assignment] = None
    next_action: Optional[NextAction] = None
    audit_event: Optional[AuditEvent] = None
    provenance_trace: Optional[ProvenanceTrace] = None
    error_code: Optional[str] = None
    message: Optional[str] = None
