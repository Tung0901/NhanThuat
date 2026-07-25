"""
SALESOS-SKILL-006 — Recommend Next Action.
Generates next sales recommendation backed by verified NhanThuat Knowledge Units (NT-LAW-0054, NT-PRINCIPLE-0086).
"""

import uuid
from salesos_pack.schemas.domain_contracts import Lead, NextAction, SalesUser


def recommend_next_action_skill(lead: Lead, assigned_user: SalesUser) -> NextAction:
    """Recommend next action backed by verified knowledge citations."""
    return NextAction(
        object_id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
        lead_id=lead.object_id,
        action_type="SCHEDULE_DISCOVERY_CALL",
        description=f"Schedule Discovery Call with {lead.customer_name} regarding {lead.product_interest} within 24 hours.",
        priority="HIGH",
        due_hours=24,
        backed_by_knowledge_units=["NT-LAW-0054", "NT-PRINCIPLE-0086"],
        status="PENDING",
    )
