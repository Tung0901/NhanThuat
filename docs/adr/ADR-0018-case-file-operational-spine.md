# ADR-0018: Case File Operational Spine

**ID:** NT-ADR-0018

**Status:** proposed

**Owner:** Product Owner

**Created:** 2026-10-08
**Decision scope:** Application runtime and product workflow

## Context

Nhan Thuat currently exposes advisory, diagnostics, council, sparring, war-room,
and reference capabilities as separate workspaces. Each workspace can accept its
own scenario text or create its own session, but the product has no canonical
operational record that carries one situation through the full decision process.

The existing `CaseStudy` model represents a saved historical case or exported
learning artifact. It must not also become the mutable record for active work.
Likewise, runtime case data must not become canonical knowledge content under
`knowledge/`.

## Proposed Decision

Introduce a `CaseFile` operational aggregate as the product spine. A Case File
will own the current situation statement, revision, access boundary, epistemic
claims, module artifacts, decision records, and timeline. Engines will consume a
revision snapshot and return artifacts; they will not own or silently mutate the
Case File.

The initial frontend integration may keep one `selectedScenario` in
`sessionStorage` to prove the cross-workspace interaction. It is explicitly an
unsaved tab-scoped draft and is not a substitute for server-side Case File
persistence.

## Boundaries

- `knowledge/` remains read-only at runtime and remains the canonical knowledge
  source.
- `CaseFile` is operational casework, not a knowledge unit and not a CaseStudy.
- `CaseStudy` remains a historical/export representation.
- Advisory, diagnostics, council, sparring, and war room return versioned
  artifacts tied to a Case File revision.
- References are a final projection over artifact citations, not another
  reasoning engine.
- HTTP handlers authenticate, authorize, validate, and serialize. Casework
  lifecycle logic belongs in a service layer.

## Minimum Contract

A future server-side `CaseFile` requires:

- `schema_version`, `case_id`, `revision`, `title`, `situation_statement`;
- `objective`, `status`, `owner_user_id`, `org_id`, `sensitivity`;
- `domain_tags`, `stakeholders`, `constraints`;
- `known_facts`, `assumptions`, `unknowns`, `risk_if_wrong`;
- `observation_signals`, `created_at`, and `updated_at`.

Every claim must declare one epistemic status:

- `observed_fact`;
- `user_claim`;
- `assumption`;
- `engine_inference`;
- `simulation`;
- `recommendation`.

Every module result must be wrapped as a `CaseArtifact` with its source module,
module version, Case File revision, input hash, knowledge references,
provenance, confidence, limitations, creator, and creation time.

## API Compatibility

- Keep `/api/v1/cases` compatible for existing CaseStudy consumers.
- Reserve `/api/v1/case-files` for the new operational aggregate.
- Add optional `case_id` and `case_revision` correlation fields to engine calls
  only after the server contract and authorization checks exist.
- Do not automatically migrate historical CaseStudy records into Case Files.

## Security And Privacy Gate

Server persistence must not ship until every Case File has `owner_user_id` and
`org_id`, and every read or write verifies the authenticated session and access
scope. Sensitive human assessments must not be stored in browser-local
persistent storage. The frontend proof therefore uses `sessionStorage` only.

## Migration Notes

Runtime SQLite storage currently defaults beneath `knowledge/`. Moving it to a
runtime path such as `var/nhan_thuat.db` or `NT_RUNTIME_DB_PATH` requires a
versioned migration that preserves existing operational data and never modifies
Frozen knowledge files.

## Consequences

Positive:

- one scenario can move through the complete product workflow;
- facts remain distinguishable from assumptions and simulations;
- module results become auditable and can be marked stale after revision;
- the frontend and backend gain a stable decomposition boundary.

Costs and risks:

- authorization and revision conflict handling become mandatory;
- existing session types need adapters instead of direct merging;
- operational database migration must be planned and tested.

## Acceptance Before Status Change

- Product Owner reviews this ADR and the Case File contract.
- Knowledge architecture review findings are addressed.
- Existing APIs and Frozen content remain unchanged.
- Characterization tests cover current CaseStudy and engine behavior.
- Ownership, revision, provenance, stale-artifact, and restart persistence tests
  pass before server-side Case Files are enabled.
