"""
SALESOS-SKILL-005 — Assign Lead.
Assigns Lead using a deterministic assignment policy (round-robin / lowest capacity) to active SalesUsers.
"""

import uuid
from typing import List, Tuple
from salesos_pack.schemas.domain_contracts import Assignment, Lead, SalesUser


def assign_lead_skill(lead: Lead, active_users: List[SalesUser]) -> Tuple[Assignment, SalesUser]:
    """
    Assign lead deterministically to the active SalesUser with the lowest assigned_lead_count.
    
    Returns (Assignment, updated_SalesUser).
    """
    if not active_users:
        # Default system user if no active users are provided
        default_user = SalesUser(
            object_id="USER-SYS-001",
            name="Default Sales Rep",
            role="sales_representative",
            status="ACTIVE",
            assigned_lead_count=0,
        )
        active_users = [default_user]

    # Deterministic selection: min assigned_lead_count, sorted by object_id for reproducibility
    sorted_users = sorted(active_users, key=lambda u: (u.assigned_lead_count, u.object_id))
    target_user = sorted_users[0]

    updated_user = SalesUser(
        object_id=target_user.object_id,
        name=target_user.name,
        role=target_user.role,
        status=target_user.status,
        assigned_lead_count=target_user.assigned_lead_count + 1,
        version=target_user.version,
    )

    assignment = Assignment(
        object_id=f"ASN-{uuid.uuid4().hex[:8].upper()}",
        lead_id=lead.object_id,
        assigned_to_user_id=target_user.object_id,
        assigned_to_user_name=target_user.name,
        policy_applied="DETERMINISTIC_CAPACITY_ROUND_ROBIN",
        status="ASSIGNED",
    )

    return assignment, updated_user
