"""
SALESOS-CAP-001 — Lead Intake and Assignment Capability.
Orchestrates the complete executable vertical slice:
Lead Intake -> Normalization -> Duplicate Check -> Record Creation -> Lead Assignment -> Next Action -> Audit & Provenance.
"""

import uuid
from typing import Any, Dict, List, Optional
from salesos_pack.events.salesos_events import SalesOSEventPublisher
from salesos_pack.personas.sales_ops_coordinator import SalesOpsCoordinatorPersona
from salesos_pack.schemas.domain_contracts import (
    Lead,
    SalesUser,
    WorkflowResult,
)
from salesos_pack.skills.assign_lead import assign_lead_skill
from salesos_pack.skills.create_lead_record import create_lead_record_skill
from salesos_pack.skills.detect_duplicate_lead import detect_duplicate_lead_skill
from salesos_pack.skills.generate_audit_provenance import generate_audit_provenance_skill
from salesos_pack.skills.normalize_contact_data import normalize_contact_data_skill
from salesos_pack.skills.recommend_next_action import recommend_next_action_skill
from salesos_pack.skills.validate_lead_input import validate_lead_input_skill


class LeadIntakeCapability:
    """SALESOS-CAP-001 — Lead Intake & Assignment Capability Engine."""

    capability_id: str = "SALESOS-CAP-001"
    capability_name: str = "Lead Intake and Assignment"
    persona: SalesOpsCoordinatorPersona = SalesOpsCoordinatorPersona()

    def __init__(self) -> None:
        self.lead_repository: List[Lead] = []
        self.active_sales_users: List[SalesUser] = [
            SalesUser(object_id="USER-SALES-001", name="Nguyen Van A", assigned_lead_count=0),
            SalesUser(object_id="USER-SALES-002", name="Tran Thi B", assigned_lead_count=0),
        ]
        self.event_publisher = SalesOSEventPublisher()

    def process_lead_intake(
        self,
        raw_payload: Dict[str, Any],
        simulate_unverified_fallback: bool = False
    ) -> WorkflowResult:
        """
        Execute full vertical slice workflow.
        """
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"

        # 0. Check Verified Configuration Fallback Trigger
        if simulate_unverified_fallback or raw_payload.get("force_unverified_knowledge"):
            return WorkflowResult(
                status="INSUFFICIENT_VERIFIED_KNOWLEDGE",
                error_code="INSUFFICIENT_VERIFIED_KNOWLEDGE",
                message="No verified BusinessOS knowledge or configuration supports this lead intake request.",
            )

        # 1. Validate Input Payload
        is_valid, validation_errors = validate_lead_input_skill(raw_payload)
        if not is_valid:
            return WorkflowResult(
                status="VALIDATION_ERROR",
                error_code="VALIDATION_ERROR",
                message="; ".join(validation_errors),
            )

        # 2. Normalize Contact Data (Phone Normalization)
        norm_success, norm_data, norm_err = normalize_contact_data_skill(raw_payload)
        if not norm_success:
            return WorkflowResult(
                status="VALIDATION_ERROR",
                error_code="PHONE_NORMALIZATION_FAILED",
                message=norm_err,
            )

        # 3. Detect Duplicate Lead
        duplicate_lead = detect_duplicate_lead_skill(
            normalized_phone=norm_data["normalized_phone"],
            customer_name=norm_data["customer_name"],
            product_interest=norm_data["product_interest"],
            existing_leads=self.lead_repository,
        )
        if duplicate_lead:
            return WorkflowResult(
                status="DUPLICATE_REJECTED",
                lead=duplicate_lead,
                error_code="DUPLICATE_LEAD_DETECTED",
                message=f"Duplicate lead detected with ID {duplicate_lead.object_id} for phone {duplicate_lead.normalized_phone}.",
            )

        # 4. Create Lead Record & Customer Record
        lead_record, customer_record = create_lead_record_skill(norm_data)
        self.lead_repository.append(lead_record)

        # 5. Deterministic Lead Assignment
        assignment_record, updated_user = assign_lead_skill(lead_record, self.active_sales_users)
        # Update user list state
        self.active_sales_users = [
            u if u.object_id != updated_user.object_id else updated_user for u in self.active_sales_users
        ]

        # 6. Recommend Next Action
        next_action_record = recommend_next_action_skill(lead_record, updated_user)

        # 7. Generate Audit Event & Provenance Trace
        audit_record, provenance_trace = generate_audit_provenance_skill(
            workflow_id=workflow_id,
            lead=lead_record,
            next_action=next_action_record,
            actor_id=self.persona.persona_id,
        )

        # 8. Publish Telemetry Audit Event
        self.event_publisher.publish_audit_event(audit_record)

        return WorkflowResult(
            status="SUCCESS",
            lead=lead_record,
            customer=customer_record,
            assignment=assignment_record,
            next_action=next_action_record,
            audit_event=audit_record,
            provenance_trace=provenance_trace,
            message="Lead intake and assignment workflow completed successfully.",
        )
