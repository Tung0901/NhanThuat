"""Catalog coverage and fail-closed regression tests for unreleased commercial features."""

import io
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend.app.engine.payment import PaymentGateway, PaymentOrder
from backend.app.engine.philosophies.iching_service import iching_service


def test_hexagram_catalog_numbers_and_lookups():
    hexagrams = iching_service.list_hexagrams()
    assert iching_service.total_count == 64
    assert sorted(h["number"] for h in hexagrams) == list(range(1, 65))
    assert len({h["symbol"] for h in hexagrams}) == 64
    assert iching_service.get_hexagram(1)["number"] == 1
    assert iching_service.get_hexagram("HEX-01")["number"] == 1
    assert iching_service.get_hexagram("Thuần Khôn")["number"] == 2
    assert iching_service.get_hexagram(65) is None
    assert iching_service.get_hexagram("") is None


def test_hexagram_filters():
    results = iching_service.list_hexagrams(palace="Càn")
    assert results
    assert all("Càn" in h["palace"] for h in results)
    results = iching_service.list_hexagrams(query="Kháng Long")
    assert results
    assert any("Kháng Long" in h.get("strategic_warning", "") for h in results)


@pytest.mark.parametrize("seed", [None, 0, 42, -1, "bad"])
def test_unverified_oracle_never_emits_guidance(seed):
    result = iching_service.cast_oracle(inquiry="A strategic decision", seed=seed)
    assert result["error_code"] == "ORACLE_UNAVAILABLE"
    assert result["epistemic_status"] == "unreviewed"
    assert "executive_synthesis" not in result
    assert "primary_hexagram" not in result


def test_catalog_is_not_a_checkout_or_subscription():
    gateway = PaymentGateway()
    assert gateway.get_tier("free")["price_vnd"] == 0
    assert gateway.get_tier("pro")["price_vnd"] == 299000
    assert gateway.get_tier("executive")["price_vnd"] == 999000
    with pytest.raises(ValueError):
        gateway.create_order("owner", "unknown")
    with pytest.raises(RuntimeError):
        gateway.create_order("owner", "pro")
    assert gateway.orders == {}
    for user in ("admin", "executive", "advisor", "new-customer"):
        assert gateway.get_user_tier(user) == "free"
        assert gateway.check_entitlement(user, "council_extended")[0] is False
        assert gateway.check_entitlement(user, "iching_oracle")[0] is False


@pytest.mark.parametrize("amount", [None, 0, -1, 299000, "invalid"])
def test_unverified_webhook_and_direct_confirmation_never_grant(amount):
    gateway = PaymentGateway()
    order = PaymentOrder("NT-PRO-TEST", "owner", "pro", 299000)
    gateway.orders[order.order_id] = order
    ok, _ = gateway.process_webhook({"content": order.order_id, "amount": amount})
    assert ok is False
    assert gateway.mark_order_paid(order.order_id, paid_amount=amount) is False
    assert order.status == "PENDING"
    assert order.paid_at is None
    assert gateway.get_user_tier("owner") == "free"


@pytest.fixture
def commercial_api(monkeypatch):
    from backend.app import main

    gateway = PaymentGateway()
    monkeypatch.setattr(main, "payment_gateway", gateway)
    session = main.auth_manager.create_session(
        {"name": "Owner", "role": "ADVISOR", "avatar": "T"},
        "test-commercial-owner",
        custom_ttl=60,
    )

    def request(method, path, payload=None, authenticated=False):
        handler = main.BusinessOSGatewayHandler.__new__(main.BusinessOSGatewayHandler)
        handler.path = path
        body = json.dumps(payload or {}).encode("utf-8")
        handler.rfile = io.BytesIO(body)
        handler.headers = {
            "Content-Length": str(len(body)),
            "Authorization": f"Bearer {session['token']}" if authenticated else "",
        }
        handler._send_json_response = MagicMock()
        getattr(handler, f"do_{method}")()
        return handler._send_json_response.call_args.args

    yield request, gateway, session
    main.auth_manager.revoke_session(session["token"])


def test_checkout_requires_session_and_stays_closed(commercial_api):
    request, gateway, _ = commercial_api
    assert request("POST", "/api/v1/payment/orders", {"user_id": "admin"})[0] == 401
    code, data = request(
        "POST", "/api/v1/payment/orders", {"user_id": "admin", "tier_id": "pro"}, True
    )
    assert code == 503
    assert data["error_code"] == "CHECKOUT_UNAVAILABLE"
    assert gateway.orders == {}
    code, data = request("GET", "/api/v1/payment/tiers")
    assert code == 200
    assert data["checkout_available"] is False
    assert data["catalog_status"] == "proposal"


def test_order_ownership_and_entitlements_derive_from_session(commercial_api):
    request, gateway, session = commercial_api
    own_order = PaymentOrder("NT-PRO-OWN", session["user_id"], "pro", 299000)
    other_order = PaymentOrder("NT-PRO-OTHER", "another-owner", "pro", 299000)
    gateway.orders[own_order.order_id] = own_order
    gateway.orders[other_order.order_id] = other_order
    assert request("GET", "/api/v1/payment/orders/NT-PRO-OWN")[0] == 401
    assert request("GET", "/api/v1/payment/orders/NT-PRO-OTHER", authenticated=True)[0] == 404
    code, data = request("GET", "/api/v1/payment/orders/NT-PRO-OWN", authenticated=True)
    assert code == 200
    assert data["order"]["user_id"] == session["user_id"]
    assert request("GET", "/api/v1/payment/entitlements?user_id=admin")[0] == 401
    code, data = request(
        "GET", "/api/v1/payment/entitlements?user_id=admin", authenticated=True
    )
    assert code == 200
    assert data["user_id"] == session["user_id"]
    assert data["tier"]["tier_id"] == "free"


def test_demo_webhook_and_oracle_routes_do_not_mutate(commercial_api):
    request, gateway, session = commercial_api
    order = PaymentOrder("NT-PRO-TEST", session["user_id"], "pro", 299000)
    gateway.orders[order.order_id] = order
    for authenticated in (False, True):
        assert request(
            "POST", "/api/v1/payment/confirm-demo", {"order_id": order.order_id}, authenticated
        )[0] == 404
        assert request(
            "POST", "/api/v1/payment/webhook",
            {"content": order.order_id, "amount": 299000}, authenticated,
        )[0] == 503
    code, data = request("POST", "/api/v1/iching/cast", {"inquiry": [], "seed": "bad"})
    assert code == 503
    assert data["error_code"] == "ORACLE_UNAVAILABLE"
    assert order.status == "PENDING"
    code, data = request("GET", "/api/v1/iching/hexagrams/HEX-01")
    assert code == 200
    assert data["epistemic_status"] == "unreviewed"


def test_authorized_qualitative_lens_runs_without_oracle(commercial_api):
    request, _, _ = commercial_api
    code, data = request(
        "POST",
        "/api/v1/nhan-thuat/analyze",
        {"scenario_text": "Phân tích quẻ Kinh Dịch và hào biến cho quyết định này"},
    )
    assert code == 200
    assert data["status"] == "success"
    assert data["philosophy_routing"]["primary_philosophy"] == "ICHING"
    assert "action_script" in data


def test_frontend_does_not_offer_fake_checkout_or_unverified_cast():
    html = Path("frontend/app.html").read_text(encoding="utf-8")
    council = Path("src/nhan_thuat/council/council_engine.py").read_text(encoding="utf-8")
    assert "confirmDemoPayment" not in html
    assert "090123456789" not in html
    assert "nhanthuat_secret_token_2026" not in html
    assert "user-scalable=no" not in html
    assert "Thuật Chu Dịch 3 đồng xu" not in html
    assert "Gieo Quẻ Dịch" not in html
    assert "Nâng Cấp Pro" not in html
    assert "iching-modal-backdrop" not in html
    assert "pricing-modal-backdrop" not in html
    assert "council-extended-toggle" not in html
    assert html.count("data-council-lens") == 7
    assert html.count('data-council-lens data-lens-status="active"') == 7
    assert html.count('data-council-lens data-lens-status="draft"') == 0
    assert "Dịch Học" in html
    assert "Thời Thế" in html
    assert "EXTENDED_COUNCIL_MEMBERS" not in council
    assert "extended: bool" not in council


def test_pwa_assets_and_manifest():
    html = Path("frontend/app.html").read_text(encoding="utf-8")
    manifest_path = Path("frontend/manifest.json")
    assert manifest_path.exists()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data["name"] == "Nhân Thuật — Executive Studio"
    assert manifest_data["icons"]
    for icon in manifest_data["icons"]:
        icon_path = Path("frontend") / icon["src"].lstrip("/")
        assert icon_path.exists(), f"Missing icon asset: {icon_path}"
    assert 'rel="manifest" href="/manifest.json"' in html
    assert "navigator.serviceWorker.register('/sw.js')" in html

    service_worker = Path("frontend/sw.js").read_text(encoding="utf-8")
    assert Path("frontend/offline.html").exists()
    assert "'/offline.html'" in service_worker
    assert "url.pathname.startsWith('/api/')" in service_worker
    assert "STATIC_ASSETS.includes(url.pathname)" in service_worker


def test_tier_naming_and_claims_are_not_superlative():
    gateway = PaymentGateway()
    for tier_id in ("free", "pro", "executive"):
        tier = gateway.get_tier(tier_id)
        assert "Tối Cao" not in tier["name"]
        for feat in tier["features"]:
            assert "Tối Cao" not in feat
            assert "Không giới hạn" not in feat
            assert "15 Lăng Kính" not in feat
            assert "7 Thành Viên" not in feat

