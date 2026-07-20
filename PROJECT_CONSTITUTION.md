# Project Constitution

**ID:** NT-GOV-CONSTITUTION-001  
**Version:** 0.1.0  
**Status:** draft  
**Owner:** Product Owner  
**Created:** 2026-07-20  
**Updated:** 2026-07-20

## 1. Authority

This Constitution is the highest governing document for the Nhan Thuat project.
When roadmap notes, governance documents, ADRs, schemas, tests, or implementation
details conflict, this Constitution takes precedence until the Product Owner
approves a newer version.

Only the Product Owner may approve an Epic, mark an item Frozen, or approve a
constitutional amendment. Codex may implement, validate, test, and prepare review
materials, but must not self-approve project content.

## 2. Mission

Nhan Thuat exists to become a structured, auditable knowledge system about human
understanding, human use, collective coordination, and purposeful action.

The repository is the official source of truth. Conversation, notes, and external
documents may inspire changes, but they become official only after they are
recorded in the repository and pass the required review process.

## 3. Scope Boundaries

The project is divided into two major layers:

- Knowledge Content: domains, laws, principles, models, strategies, tools, cases,
  evidence, and relationships.
- Knowledge Engine: code that loads, validates, indexes, retrieves, cites, tests,
  or serves the knowledge content.

Content and engine must remain separate. User interfaces, APIs, generated
catalogs, or AI integrations may consume repository content later, but they must
not become the canonical source of truth.

## 4. Governance States

The standard lifecycle is:

`Backlog -> Draft -> Schema Valid -> Internal Review -> Test Passed -> Ready for Epic Review -> Approved -> Frozen`

Operational status values may use the machine-readable equivalents already
defined by project schemas.

An item is not Approved or Frozen merely because tests pass. Approval and Frozen
state require explicit Product Owner decision.

Frozen content must not be changed directly. A future change to Frozen content
requires a Change Request, version update, rationale, impact note, and relevant
validation/test evidence.

## 5. Evidence And Knowledge Quality

Knowledge records must express:

- stable IDs;
- scope and domain;
- conditions where the statement applies;
- exceptions and risks;
- evidence level;
- traceable references when available;
- relationships to other knowledge units when relevant.

Nhan Thuat must not claim universal certainty about human behavior. Statements
about people must preserve context, uncertainty, and exception handling.

## 6. Architecture Decisions

Architectural and governance decisions that constrain future work must be recorded
as Architecture Decision Records under `docs/adr/`.

Initial required ADRs are:

- ADR-0001: Repository as source of truth.
- ADR-0002: Separation of knowledge content and engine.
- ADR-0003: Product Owner approval and Frozen control.
- ADR-0004: ADR process for durable decisions.

Future Epics may add ADRs when they introduce durable schema, storage, runtime,
retrieval, citation, release, or integration decisions.

## 7. Validation And Review

Every Epic must finish with relevant validation, tests, linting, and status
metadata. A review package should be sufficient for the Product Owner and external
reviewers to inspect the work without relying on private conversation context.

Validation and tests are required evidence. They are not a substitute for review.

## 8. Amendment Rule

This Constitution may change only through a Product Owner-approved amendment.
Each amendment must state:

- what changed;
- why it changed;
- which Epics or Frozen items are affected;
- which ADRs or governance documents need follow-up.
