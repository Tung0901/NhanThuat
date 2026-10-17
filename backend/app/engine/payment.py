"""
Proposed subscription catalog for NhanThuat Executive Studio.
Checkout and entitlement grants are disabled pending independent settlement review.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any

# Pricing Tier Configuration
TIERS: dict[str, dict[str, Any]] = {
    "free": {
        "tier_id": "free",
        "name": "Khách Mời Trải Nghiệm",
        "price_vnd": 0,
        "period": "vĩnh viễn",
        "features": [
            "3 lượt phân tích chiến lược / ngày (dự kiến)",
            "Hội Đồng Cố Vấn Cổ Điển (5 Thành Viên)",
            "Tra cứu danh mục 19 cẩm nang điều hành",
            "Chẩn đoán Person-Role Fit cơ bản",
        ],
        "limits": {
            "daily_analyses": 3,
            "council_extended": False,
            "iching_oracle": False,
            "pdf_export": False,
            "war_room": False,
            "sparring": False,
        },
    },
    "pro": {
        "tier_id": "pro",
        "name": "Chuyên Viên / Cố Vấn Pro",
        "price_vnd": 299000,
        "period": "tháng",
        "features": [
            "Hạn mức phân tích mở rộng theo tài khoản",
            "13 Lăng Kính Triết Học đã qua kiểm định",
            "Đọc danh mục Cẩm Nang & Xuất Báo Cáo PDF",
            "Kịch bản đối thoại & Mẫu văn bản chỉ đạo",
        ],
        "limits": {
            "daily_analyses": 100,
            "council_extended": False,
            "iching_oracle": False,
            "pdf_export": True,
            "war_room": False,
            "sparring": True,
        },
    },
    "executive": {
        "tier_id": "executive",
        "name": "Điều Hành Cao Cấp (Executive Master)",
        "price_vnd": 999000,
        "period": "tháng",
        "features": [
            "Tất cả quyền lợi của gói Pro",
            "Hội đồng cố vấn chiến lược đa góc nhìn",
            "Sa Bàn Tình Thế (War Room Multi-Agent)",
            "Phòng Đấu Trí Giả Lập (AI Sparring Arena)",
            "Chỉ mục tài liệu doanh nghiệp phục vụ phân tích (Custom RAG)",
            "Ưu tiên hàng đợi xử lý",
        ],
        "limits": {
            "daily_analyses": 500,
            "council_extended": False,
            "iching_oracle": False,
            "pdf_export": True,
            "war_room": True,
            "sparring": True,
        },
    },
}


@dataclass
class PaymentOrder:
    order_id: str
    user_id: str
    tier_id: str
    amount_vnd: int
    status: str = "PENDING"  # PENDING, PAID, EXPIRED, CANCELLED
    transfer_content: str = ""
    qr_url: str = ""
    created_at: float = field(default_factory=time.time)
    paid_at: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PAYMENT_UNAVAILABLE_MESSAGE = (
    "Thanh toan chua mo: can luu tru ben vung, xac minh giao dich va kiem tra quyen."
)


class PaymentGateway:
    """Read-only commercial prototype; no checkout or grants before settlement review."""

    def __init__(self) -> None:
        self.orders: dict[str, PaymentOrder] = {}

    def get_tier(self, tier_id: str) -> dict[str, Any] | None:
        return TIERS.get(tier_id.lower())

    def get_user_tier(self, user_id: str) -> str:
        # A role or username is not proof of a purchased subscription.
        return "free"

    def check_entitlement(self, user_id: str, feature_key: str) -> tuple[bool, str]:
        allowed = TIERS["free"]["limits"].get(feature_key) is True
        return allowed, "Authorized" if allowed else PAYMENT_UNAVAILABLE_MESSAGE

    def create_order(self, user_id: str, tier_id: str) -> PaymentOrder:
        tier = self.get_tier(tier_id)
        if not tier or tier["price_vnd"] <= 0:
            raise ValueError(f"Invalid tier '{tier_id}' for payment order.")
        raise RuntimeError(PAYMENT_UNAVAILABLE_MESSAGE)

    def get_order(self, order_id: str) -> PaymentOrder | None:
        return self.orders.get(order_id)

    def mark_order_paid(self, order_id: str, paid_amount: int | None = None) -> bool:
        """No direct grants, including sandbox calls, against production entitlements."""
        return False

    def process_webhook(self, payload: dict[str, Any]) -> tuple[bool, str]:
        """Fail closed until a specific provider's verification contract is implemented."""
        return False, PAYMENT_UNAVAILABLE_MESSAGE


# Global Singleton Gateway
payment_gateway = PaymentGateway()
