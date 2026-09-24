"""
Enterprise Connectors & Executive Whisper Bot Module.
Module: modules.connectors.webhook_connector

Connects external enterprise collaboration platforms (Slack, Microsoft Teams, Lark)
and HRIS/CRM webhooks to the Nhan Thuat Behavioral & Action Routing Intelligence Pipeline.
Generates structured Executive Whisper Bot briefs for executive decision-makers.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any

from modules.business_os.router import ActionRouterResult, BusinessOSActionRouter
from modules.nhan_thuat.continuous_profiler import ContinuousBehavioralProfile, continuous_profiler
from modules.nhan_thuat.service import BehavioralEvaluationEvent, NhanThuatBehavioralService


@dataclass(frozen=True)
class WebhookPayload:
    """Normalized payload parsed from various external webhook formats."""
    source: str  # "slack" | "teams" | "lark" | "hris" | "crm" | "generic"
    author_id: str
    content: str
    channel_or_context: str = "general"
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExecutiveWhisperBrief:
    """Executive Whisper Bot brief structured for private C-level dispatch."""
    brief_id: str
    timestamp: float
    source: str
    author_id: str
    headline: str
    urgency_level: str  # "CRITICAL" | "HIGH" | "NORMAL"
    behavioral_summary: str
    load_risk_warning: str
    recommended_whisper_action: str
    alerts: list[str]
    slack_blocks: list[dict[str, Any]]
    teams_adaptive_card: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EnterpriseWebhookConnector:
    """Ingests enterprise webhooks and produces Executive Whisper Bot advisories."""

    def __init__(
        self,
        behavioral_service: NhanThuatBehavioralService | None = None,
        action_router: BusinessOSActionRouter | None = None,
    ) -> None:
        self.behavioral_service = behavioral_service or NhanThuatBehavioralService()
        self.action_router = action_router or BusinessOSActionRouter(confidence_threshold=0.85)
        self.history: list[ExecutiveWhisperBrief] = []

    def parse_webhook(self, source: str, raw_data: dict[str, Any]) -> WebhookPayload:
        """Normalize raw incoming webhook payload from Slack, Teams, Lark, HRIS, or Generic."""
        src = source.lower().strip()
        author_id = "EMP-UNKNOWN"
        content = ""
        context = "general"

        if src == "slack":
            # Slack event wrapper
            event = raw_data.get("event", raw_data)
            author_id = event.get("user", event.get("user_id", "SLACK-USER"))
            content = event.get("text", "")
            context = event.get("channel", "slack-channel")
        elif src == "teams":
            # Microsoft Teams webhook
            author_id = raw_data.get("from", {}).get("id", raw_data.get("sender", "TEAMS-USER"))
            content = raw_data.get("text", "")
            context = raw_data.get("conversation", {}).get("id", "teams-channel")
        elif src == "lark":
            # Lark / Feishu event
            event = raw_data.get("event", raw_data)
            author_id = event.get("sender", {}).get("sender_id", {}).get("open_id", "LARK-USER")
            content = event.get("message", {}).get("content", raw_data.get("text", ""))
            context = event.get("message", {}).get("chat_id", "lark-chat")
        elif src in ("hris", "crm"):
            # HRIS / CRM event (e.g. BambooHR, Salesforce)
            author_id = raw_data.get("employee_id", raw_data.get("lead_id", "HRIS-EMP"))
            content = raw_data.get("notes", raw_data.get("description", raw_data.get("reason", "")))
            context = raw_data.get("department", raw_data.get("deal_stage", "hr-crm-event"))
        else:
            # Generic JSON
            author_id = str(raw_data.get("author_id", raw_data.get("user_id", "EMP-GENERIC")))
            content = str(raw_data.get("content", raw_data.get("message", raw_data.get("text", ""))))
            context = str(raw_data.get("context", raw_data.get("channel", "general")))

        return WebhookPayload(
            source=src,
            author_id=author_id,
            content=content,
            channel_or_context=context,
            raw_payload=raw_data,
        )

    def process_incoming_webhook(
        self,
        source: str,
        raw_data: dict[str, Any],
        task_context: str = "",
    ) -> ExecutiveWhisperBrief:
        """Process incoming webhook through the complete Nhan Thuat intelligence pipeline."""
        webhook = self.parse_webhook(source, raw_data)
        context_str = task_context or webhook.channel_or_context

        # 1. Behavioral Evaluation
        eval_event: BehavioralEvaluationEvent = self.behavioral_service.evaluate(
            human_input=webhook.content,
            author_id=webhook.author_id,
            source_type=webhook.source,
        )

        # 2. Continuous Profiling & Load Forecast
        profile: ContinuousBehavioralProfile = continuous_profiler.ingest_event(eval_event)

        # 3. BusinessOS Action Routing
        router_result: ActionRouterResult = self.action_router.route(
            event=eval_event,
            task_context=context_str,
        )

        # 4. Synthesize Executive Whisper Brief
        urgency = "NORMAL"
        if eval_event.burnout_risk or eval_event.stress_score >= 5 or profile.flight_risk_level == "CRITICAL":
            urgency = "CRITICAL"
        elif eval_event.stress_score >= 4 or profile.flight_risk_level == "ELEVATED":
            urgency = "HIGH"

        headline = f"[{urgency}] Tín Hiệu Hành Vi Từ {webhook.author_id} ({webhook.source.upper()})"
        behavioral_summary = (
            f"DISC: {eval_event.behavior_style} (P={eval_event.behavior_style_confidence:.2f}) | "
            f"Stress: {eval_event.stress_score}/5 | "
            f"Nguy cơ kiệt sức: {'CÓ' if eval_event.burnout_risk else 'KHÔNG'} | "
            f"Rủi ro nghỉ việc: {profile.flight_risk_level} ({profile.flight_risk_score:.2f})"
        )

        load_warning = (
            f"Cảnh báo quá tải (NT-MODEL-0008): {profile.under_load_forecast.default_tendency}"
            if eval_event.stress_score >= 4
            else "Tâm lý trong ngưỡng kiểm soát, chưa xuất hiện biểu hiện thoái lui mặc định."
        )

        recommended_whisper = (
            profile.recommended_interventions[0]
            if profile.recommended_interventions
            else "Tiếp tục quan sát nhịp độ tương tác định kỳ."
        )

        # Slack Block Kit representation
        slack_blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"👑 Cố Vấn Bí Mật: {headline}"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Bản tóm lược tín hiệu:*\n{behavioral_summary}\n\n*Phân tích quá tải:*\n{load_warning}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Khuyến nghị hành động tức thì:*\n👉 {recommended_whisper}",
                },
            },
        ]

        # Teams Adaptive Card representation
        teams_card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {"type": "TextBlock", "text": headline, "weight": "Bolder", "size": "Medium"},
                {"type": "TextBlock", "text": behavioral_summary, "wrap": True},
                {"type": "TextBlock", "text": load_warning, "wrap": True, "color": "Attention" if urgency != "NORMAL" else "Default"},
                {"type": "TextBlock", "text": f"Khuyến nghị: {recommended_whisper}", "wrap": True, "weight": "Bolder"},
            ],
        }

        brief = ExecutiveWhisperBrief(
            brief_id=f"WHISPER-{uuid.uuid4().hex[:8].upper()}",
            timestamp=time.time(),
            source=webhook.source,
            author_id=webhook.author_id,
            headline=headline,
            urgency_level=urgency,
            behavioral_summary=behavioral_summary,
            load_risk_warning=load_warning,
            recommended_whisper_action=recommended_whisper,
            alerts=router_result.alerts_triggered,
            slack_blocks=slack_blocks,
            teams_adaptive_card=teams_card,
        )

        self.history.append(brief)
        return brief

    def seed_demo_data(self) -> None:
        """Seed initial executive whisper briefs for dashboard demonstration."""
        if self.history:
            return

        now = time.time()
        self.history.append(
            ExecutiveWhisperBrief(
                brief_id=f"WHISPER-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - 600,
                source="slack",
                author_id="EMP-HA (Trần Thu Hà - Head of Product)",
                headline="🚨 Cảnh báo Rủi ro Rời bỏ Cấp bách: Trưởng nhóm Product kiệt sức nghiêm trọng",
                urgency_level="CRITICAL",
                behavioral_summary="Phát hiện tín hiệu quá tải cảm xúc (Emotional Overload) và rạn nứt kết nối qua kênh #product-leads sau 3 tuần tăng ca liên tiếp.",
                load_risk_warning="Hành vi chuyển dịch sang dạng thoái lui bốc đồng (DISC Style I under load), nguy cơ nộp đơn nghỉ việc trong vòng 7 ngày.",
                recommended_whisper_action="Chủ tịch / CEO can thiệp kín: Thiết lập phiên gặp 1-1 riêng trong 24h, chủ động giảm 30% backlog tính năng và công khai ghi nhận thành quả.",
                alerts=["CRITICAL_FLIGHT_RISK", "BURNOUT_VELOCITY_HIGH"],
                slack_blocks=[
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": "*[CƠ MẬT CHỈ HUY]* Phát hiện rủi ro rời bỏ nghiêm trọng từ Head of Product."},
                    }
                ],
                teams_adaptive_card={
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {"type": "TextBlock", "text": "Executive Whisper Alert: Flight Risk", "weight": "Bolder"}
                    ],
                },
            )
        )
        self.history.append(
            ExecutiveWhisperBrief(
                brief_id=f"WHISPER-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - 1800,
                source="teams",
                author_id="EMP-LONG (Nguyễn Hoàng Long - VP Eng)",
                headline="⚠️ Cảnh báo Căng thẳng Lãnh đạo: Xung đột thẩm quyền kỹ thuật tại dự án Core",
                urgency_level="HIGH",
                behavioral_summary="Nhận diện xu hướng áp đặt mệnh lệnh cứng rắn (DISC Style D under load), bỏ qua tham vấn hội đồng giải pháp.",
                load_risk_warning="Nguy cơ tạo phản ứng ly khai hoặc chống đối thụ động từ các kỹ sư nòng cốt trong ban dự án.",
                recommended_whisper_action="Gặp riêng 1-1 tái xác nhận thẩm quyền kỹ thuật đi kèm rào chắn số liệu (guardrails), áp dụng thuật Lễ Định Phần của Tuân Tử.",
                alerts=["LEADERSHIP_FRICTION_ELEVATED"],
                slack_blocks=[],
                teams_adaptive_card={},
            )
        )


# Global singleton instance
enterprise_connector = EnterpriseWebhookConnector()
