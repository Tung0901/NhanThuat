"""
SALESOS-SKILL-003 — Detect Duplicate Lead.
Applies deterministic matching rules to detect duplicate leads against existing lead repository.
"""

from typing import Dict, List, Optional
from salesos_pack.schemas.domain_contracts import Lead


def detect_duplicate_lead_skill(
    normalized_phone: str,
    customer_name: str,
    product_interest: str,
    existing_leads: List[Lead]
) -> Optional[Lead]:
    """
    Detect duplicate lead by normalized phone OR (customer_name + product_interest).
    
    Returns matching Lead if duplicate, else None.
    """
    target_name_lower = customer_name.strip().lower()
    target_interest_lower = product_interest.strip().lower()

    for lead in existing_leads:
        # Rule 1: Exact Normalized Phone Match
        if lead.normalized_phone == normalized_phone:
            return lead

        # Rule 2: Exact Name + Product Interest Match
        if (
            lead.customer_name.strip().lower() == target_name_lower
            and lead.product_interest.strip().lower() == target_interest_lower
        ):
            return lead

    return None
