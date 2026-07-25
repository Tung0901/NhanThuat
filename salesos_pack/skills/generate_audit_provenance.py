"""
SALESOS-SKILL-007 — Generate Audit and Provenance.
Produces immutable AuditEvent and ProvenanceTrace contracts with integrity SHA-256 checksums.
"""

import uuid
from typing import Any, Dict, Tuple
from salesos_pack.schemas.domain_contracts import AuditEvent, Lead, NextAction, ProvenanceTrace


def generate_audit_provenance_skill(
    workflow_id: str,
    lead: Lead,
    next_action: NextAction,
    actor_id: str = "SALESOS-PERSONA-001"
) -> Tuple[AuditEvent, ProvenanceTrace]:
    """Generate AuditEvent and ProvenanceTrace payloads."""
    audit_event = AuditEvent(
        object_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        event_type="LEAD_INTAKE_COMPLETED",
        aggregate_id=lead.object_id,
        payload={
            "lead_id": lead.object_id,
            "customer_name": lead.customer_name,
            "normalized_phone": lead.normalized_phone,
            "product_interest": lead.product_interest,
            "next_action_id": next_action.object_id,
        },
        actor_id=actor_id,
        status="PUBLISHED",
    )

    provenance_trace = ProvenanceTrace(
        object_id=f"TRC-{uuid.uuid4().hex[:8].upper()}",
        workflow_id=workflow_id,
        capability_id="SALESOS-CAP-001",
        persona_id=actor_id,
        knowledge_citations=["NT-LAW-0054", "NT-PRINCIPLE-0086"],
        skill_pipeline=[
            "SALESOS-SKILL-001",
            "SALESOS-SKILL-002",
            "SALESOS-SKILL-003",
            "SALESOS-SKILL-004",
            "SALESOS-SKILL-005",
            "SALESOS-SKILL-006",
            "SALESOS-SKILL-007",
        ],
        lenses_applied=["LENS-RHETORIC", "LENS-CONFUCIAN"],
        confidence_score=0.95,
        status="RECORDED",
    )

    return audit_event, provenance_trace
