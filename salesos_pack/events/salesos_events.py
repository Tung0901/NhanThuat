"""
SalesOS Event Publisher.
Publishes LeadIntake, LeadAssigned, and Audit events.
"""

from typing import Any, Dict, List
from salesos_pack.schemas.domain_contracts import AuditEvent, Lead


class SalesOSEventPublisher:
    """SalesOS Event Publisher storing published event history in memory."""

    def __init__(self) -> None:
        self.published_events: List[Dict[str, Any]] = []

    def publish_audit_event(self, audit_event: AuditEvent) -> Dict[str, Any]:
        event_data = {
            "topic": "salesos.audit",
            "event_id": audit_event.object_id,
            "event_type": audit_event.event_type,
            "aggregate_id": audit_event.aggregate_id,
            "payload": audit_event.payload,
            "actor_id": audit_event.actor_id,
            "checksum": audit_event.checksum,
            "created_at": audit_event.created_at,
        }
        self.published_events.append(event_data)
        return event_data
