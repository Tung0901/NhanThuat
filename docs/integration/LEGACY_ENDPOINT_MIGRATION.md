# Legacy Endpoint Migration

**Document ID:** `DOC-INT-004`

## 1. Context

BusinessOS previously exposed unversioned API endpoints for Knowledge retrieval (e.g., `GET /knowledge/units/{unit_id}`). With the introduction of the NhanThuat Public Contract V1, these endpoints are now deprecated.

## 2. Deprecation Schedule

- **M4-B (Current Phase)**: Both V1 (`/api/v1/knowledge/...`) and legacy unversioned endpoints are active. V1 is backed by the new `NhanThuatProviderV1` adapter.
- **M5**: Legacy endpoints will emit a deprecation warning in their JSON response.
- **M6**: Legacy endpoints will be physically removed from `backend/app/main.py`.

## 3. Migration Instructions for Consumers

Consumers must migrate their calls:
- Replace `GET /knowledge/units/{unit_id}` with `GET /api/v1/knowledge/units/{unit_id}`.
- Replace `GET /knowledge/domains/{domain_slug}` with `GET /api/v1/knowledge/domains/{domain_slug}`.
- Replace `POST /knowledge/query` with `POST /api/v1/knowledge/query`.

The payload and response structures for V1 comply with the newly defined immutable data contracts.
