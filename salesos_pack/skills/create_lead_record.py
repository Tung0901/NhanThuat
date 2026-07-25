"""
SALESOS-SKILL-004 — Create Lead Record.
Instantiates immutable Lead and Customer domain contract records.
"""

import uuid
from typing import Any, Dict, Tuple
from salesos_pack.schemas.domain_contracts import Customer, Lead


def create_lead_record_skill(normalized_data: Dict[str, Any]) -> Tuple[Lead, Customer]:
    """Create Lead and Customer records with unique object_ids and integrity checksums."""
    lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
    customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"

    customer = Customer(
        object_id=customer_id,
        name=normalized_data["customer_name"],
        phone=normalized_data["normalized_phone"],
        status="ACTIVE",
    )

    lead = Lead(
        object_id=lead_id,
        customer_name=normalized_data["customer_name"],
        normalized_phone=normalized_data["normalized_phone"],
        raw_phone=normalized_data["raw_phone"],
        lead_source=normalized_data["lead_source"],
        product_interest=normalized_data["product_interest"],
        notes=normalized_data.get("notes", ""),
        status="NEW",
    )

    return lead, customer
