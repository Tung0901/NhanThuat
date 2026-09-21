"""
BusinessOS Action Router.
Listens to Nhân Thuật behavioral evaluation events.
Executes deterministic actions based on confidence thresholds (P > 0.85):
- If stress_score >= 4 or burnout_risk == True:
    -> Flag urgent manager alert & adjust task priority.
- If behavior_style == 'D':
    -> Format task dispatch as direct executive bullet-points.
- If behavior_style == 'C':
    -> Append technical specifications & validation criteria.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from modules.nhan_thuat.service import BehavioralEvaluationEvent

CONFIDENCE_THRESHOLD = 0.85


@dataclass(frozen=True)
class BusinessOSAction:
    """Represents an actionable operational directive emitted by BusinessOS."""
    action_type: str
    priority: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "NORMAL"
    payload: dict[str, Any]
    rationale: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_type": self.action_type,
            "priority": self.priority,
            "payload": self.payload,
            "rationale": self.rationale,
            "confidence": round(self.confidence, 4),
        }


@dataclass(frozen=True)
class ActionRouterResult:
    """Aggregated output of the BusinessOS Action Router."""
    router_id: str
    event_id: str
    author_id: str
    actions: list[BusinessOSAction]
    dispatch_text: str
    alerts_triggered: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "router_id": self.router_id,
            "event_id": self.event_id,
            "author_id": self.author_id,
            "actions": [a.to_dict() for a in self.actions],
            "dispatch_text": self.dispatch_text,
            "alerts_triggered": list(self.alerts_triggered),
            "metadata": self.metadata,
        }


class BusinessOSActionRouter:
    """
    Translates psychological/behavioral signals into concrete BusinessOS operational workflows.
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD) -> None:
        self.confidence_threshold = confidence_threshold

    def route(
        self,
        event: BehavioralEvaluationEvent,
        task_context: str | dict[str, Any] | None = None,
    ) -> ActionRouterResult:
        """
        Process a BehavioralEvaluationEvent and execute deterministic operational actions.
        """
        router_id = f"RTR-{uuid.uuid4().hex[:8].upper()}"
        actions: list[BusinessOSAction] = []
        alerts_triggered: list[str] = []

        raw_task = ""
        if isinstance(task_context, str):
            raw_task = task_context
        elif isinstance(task_context, dict):
            raw_task = str(task_context.get("task_description", ""))

        # 1. Stress & Burnout Evaluation (Threshold P > 0.85)
        high_stress = (
            event.stress_score >= 4
            and event.stress_score_confidence > self.confidence_threshold
        )
        high_burnout = (
            event.burnout_risk is True
            and event.burnout_risk_confidence > self.confidence_threshold
        )

        if high_stress or high_burnout:
            reasons = []
            if high_stress:
                reasons.append(f"stress_score={event.stress_score} (P={event.stress_score_confidence:.2f})")
            if high_burnout:
                reasons.append(f"burnout_risk=True (P={event.burnout_risk_confidence:.2f})")

            alert_reason = " & ".join(reasons)
            alerts_triggered.append(f"URGENT_BURNOUT_ALERT: {alert_reason}")

            # Urgent Manager Alert Action
            actions.append(
                BusinessOSAction(
                    action_type="URGENT_MANAGER_ALERT",
                    priority="CRITICAL",
                    payload={
                        "target_author_id": event.author_id,
                        "stress_score": event.stress_score,
                        "burnout_risk": event.burnout_risk,
                        "recommended_intervention": "Immediate 1-on-1 check-in, workload pause, and reassignment of critical path blockers.",
                    },
                    rationale=f"High risk behavioral indicators detected: {alert_reason}.",
                    confidence=max(event.stress_score_confidence, event.burnout_risk_confidence),
                )
            )

            # Adjust Task Priority Action
            actions.append(
                BusinessOSAction(
                    action_type="TASK_PRIORITY_ADJUSTMENT",
                    priority="HIGH",
                    payload={
                        "target_author_id": event.author_id,
                        "new_priority": "PAUSED_OR_DELEGATED",
                        "cooldown_period_hours": 24,
                    },
                    rationale="Automatic workload throttle engaged to mitigate burnout risk.",
                    confidence=max(event.stress_score_confidence, event.burnout_risk_confidence),
                )
            )

        # 2. Behavioral Style Dispatch Formatting (Threshold P > 0.85)
        dispatch_text = ""
        task_label = raw_task if raw_task else "Dự án Nâng cấp Hệ thống"

        if (
            event.behavior_style == "D"
            and event.behavior_style_confidence > self.confidence_threshold
        ):
            # Direct Executive Bullet-points
            dispatch_text = (
                f"### [EXECUTIVE DIRECT DISPATCH • STYLE D]\n"
                f"• Mục tiêu cốt lõi: {task_label}\n"
                f"• Kết quả bàn giao yêu cầu: Hoàn tất 100% KPI cam kết trước 17:00 hôm nay.\n"
                f"• Quyền hạn: Toàn quyền quyết định phương án kỹ thuật và điều phối nguồn lực.\n"
                f"• Kỷ luật thực thi: Báo cáo ngắn gọn 3 dòng khi hoàn thành."
            )
            actions.append(
                BusinessOSAction(
                    action_type="TASK_DISPATCH_DIRECT_BULLETS",
                    priority="HIGH" if not (high_stress or high_burnout) else "MEDIUM",
                    payload={
                        "style": "D",
                        "formatted_template": "executive_bullets",
                        "dispatch_content": dispatch_text,
                    },
                    rationale=f"Employee exhibits Dominance style (P={event.behavior_style_confidence:.2f}). Direct concise framing maximizes throughput.",
                    confidence=event.behavior_style_confidence,
                )
            )

        elif (
            event.behavior_style == "C"
            and event.behavior_style_confidence > self.confidence_threshold
        ):
            # Technical specifications & validation criteria
            dispatch_text = (
                f"### [TECHNICAL SPECIFICATION DISPATCH • STYLE C]\n"
                f"1. Phạm vi & Yêu cầu: {task_label}\n"
                f"2. Đặc tả kỹ thuật & Kiến trúc: Tuân thủ nghiêm ngặt chuẩn typed interfaces, schema validation.\n"
                f"3. Tiêu chí nghiệm thu (Acceptance Criteria):\n"
                f"   - [x] Syntax check / type-check pass (zero warnings).\n"
                f"   - [x] Test suite coverage 100% cho mọi edge cases.\n"
                f"   - [x] Exit code 0 trên môi trường thực tế."
            )
            actions.append(
                BusinessOSAction(
                    action_type="TASK_DISPATCH_TECH_SPEC",
                    priority="HIGH" if not (high_stress or high_burnout) else "MEDIUM",
                    payload={
                        "style": "C",
                        "formatted_template": "technical_spec",
                        "dispatch_content": dispatch_text,
                    },
                    rationale=f"Employee exhibits Conscientiousness style (P={event.behavior_style_confidence:.2f}). Detailed criteria ensure precision and quality.",
                    confidence=event.behavior_style_confidence,
                )
            )

        else:
            # Routine / Default Task Dispatch
            dispatch_text = (
                f"### [ROUTINE TASK DISPATCH]\n"
                f"Nhiệm vụ: {task_label}\n"
                f"Ghi chú: Phối hợp nhịp nhàng theo tiến độ chung của đội ngũ."
            )
            actions.append(
                BusinessOSAction(
                    action_type="ROUTINE_TASK_DISPATCH",
                    priority="NORMAL",
                    payload={
                        "style": event.behavior_style,
                        "formatted_template": "routine",
                        "dispatch_content": dispatch_text,
                    },
                    rationale=f"Standard operational routing applied (style={event.behavior_style}, P={event.behavior_style_confidence:.2f}).",
                    confidence=event.behavior_style_confidence,
                )
            )

        return ActionRouterResult(
            router_id=router_id,
            event_id=event.event_id,
            author_id=event.author_id,
            actions=actions,
            dispatch_text=dispatch_text,
            alerts_triggered=alerts_triggered,
            metadata={
                "stress_score": event.stress_score,
                "burnout_risk": event.burnout_risk,
                "behavior_style": event.behavior_style,
            },
        )
