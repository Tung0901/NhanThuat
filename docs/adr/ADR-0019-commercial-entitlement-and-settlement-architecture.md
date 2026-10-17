# ADR-0019: Commercial Entitlement, Settlement, and Webhook Architecture

**ID:** NT-ADR-0019

**Status:** proposed

**Owner:** Product Owner

**Created:** 2026-10-14  
**Decision scope:** Commercial persistence, subscription lifecycle, entitlement enforcement, payment settlement, and webhook integrity

---

## 1. Context

During the rapid prototype phase, NhanThuat introduced subscription tiers, VietQR invoice generation, and a webhook endpoint. An independent commercial and security audit (`NT-AUDIT-COMMERCIAL-2026-10-14`) identified critical systemic vulnerabilities in this design:

1. **Ephemeral State:** All orders, subscriptions, and user entitlements were stored exclusively in server RAM (`_ORDERS_DB`, `_ENTITLEMENTS_DB`). A server restart or crash permanently wiped all customer transactions and granted rights.
2. **Missing Settlement Contract:** Webhooks accepted unauthenticated payloads without cryptographic signature validation, allowing unauthorized external callers to forge payments.
3. **Absence of Server-Side Entitlement Middleware:** Tier limits (e.g., "3 requests/day", "unlimited", "15 lenses") were purely descriptive text on the client; no gateway middleware tracked quotas or enforced access boundaries per API request.
4. **Hardcoded Credentials:** Payment routing relied on sample environment variables, lacking secret rotation, webhook signature verification, and idempotency guarantees.

A durable, auditable, and resilient commercial architecture is required before any commercial transactions or public subscriptions can be accepted.

---

## 2. Decision

### 2.1 Durable Relational Persistence (PostgreSQL Schema)

All commercial and billing data must be persisted in an ACID-compliant relational database. The schema must strictly model:

1. **`customers`:** Persistent customer profile linked to an authenticated identity (`id`, `user_id`, `email`, `created_at`, `status`).
2. **`orders`:** Explicit order record (`order_id`, `customer_id`, `tier_id`, `amount_vnd`, `currency`, `state`, `created_at`, `expires_at`, `settled_at`).
3. **`transactions`:** Ledger record of payment attempts (`txn_id`, `order_id`, `provider`, `provider_ref`, `amount`, `status`, `raw_payload_hash`).
4. **`subscriptions`:** Time-bounded active subscription intervals (`subscription_id`, `customer_id`, `tier_id`, `starts_at`, `ends_at`, `auto_renew`, `status`).
5. **`entitlements`:** Fine-grained functional permission flags and quota counters (`customer_id`, `feature_key`, `quota_limit`, `quota_used`, `reset_period`, `valid_until`).
6. **`webhook_events`:** Inbound event ledger for idempotency and audit (`event_id`, `provider`, `event_type`, `signature`, `payload_json`, `processed_at`, `status`).

### 2.2 Formal Order State Machine

Orders must transition strictly through deterministic states:

```
[CREATED] ──> [PENDING_PAYMENT] ──┬──> [SETTLED] ──> [FULFILLED]
                                  ├──> [EXPIRED]
                                  └──> [FAILED]
[SETTLED] ──> [REFUNDED]
```

- State transitions must be transactional.
- Direct status mutation from the frontend or unauthenticated APIs is prohibited.
- An order enters `SETTLED` **only** upon successful cryptographic verification of an inbound webhook or verified gateway polling inquiry.

### 2.3 Cryptographic Webhook Contract & Idempotency

All payment providers (VietQR/PayOS/Stripe/MoMo) must adhere to a strict webhook handling protocol:

1. **HMAC Signature Verification:** Each inbound webhook must verify an `X-Signature` header computed via HMAC-SHA256 using a securely provisioned gateway webhook secret.
2. **Timestamp & Replay Protection:** Webhooks with timestamps differing by more than 300 seconds from server clock must be rejected (`400 BAD_REQUEST`).
3. **Idempotency Key:** Every webhook delivery ID or transaction reference must be stored in `webhook_events`. Duplicate deliveries must be acknowledged (`200 OK`) without re-executing entitlement grants or state transitions.
4. **Exact Amount & Currency Matching:** The received amount must match `order.amount_vnd` and `order.currency` exactly; underpayments or overpayments must transition to `DISCREPANCY_FLAGGED` for manual reconciliation.

### 2.4 Server-Side Entitlement & Quota Enforcement Middleware

1. Every protected endpoint (e.g. `/api/v1/nhan-thuat/analyze`, `/api/v1/council/deliberate`, `/api/v1/sparring/message`) must pass through an `EntitlementMiddleware`.
2. The middleware resolves the Bearer session to `customer_id`, queries active `entitlements`, checks remaining daily/monthly quotas, and increments the atomic counter.
3. If quota is exceeded, the request must fail-closed with `429 TOO_MANY_REQUESTS` and machine-readable quota headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`).
4. Unreviewed or draft capabilities (e.g., experimental lenses or oracle casting) must never be enabled via entitlement grants until approved by governance review.

---

## 3. Consequences

### Positive
- Materially reduces revenue and transaction-state loss across deployments and restarts.
- Adds controls against payment bypasses and replay attacks; it does not remove all fraud risk.
- Enables auditable usage and operating-cost telemetry per tier.
- Clean separation between operational casework, knowledge engines, and commercial billing.

### Negative / Required Work
- Requires provisioning and migrating a PostgreSQL instance.
- Requires building database migration scripts (Alembic) and unit test fixtures.
- Checkout and billing remain quarantined (`503 CHECKOUT_UNAVAILABLE`) until this architecture is implemented and passes penetration testing.
