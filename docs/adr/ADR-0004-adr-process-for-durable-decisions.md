# ADR-0004: ADR Process For Durable Decisions

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Future Epics will introduce decisions about schemas, ontology, retrieval,
evidence, applications, APIs, release, and AI behavior. These decisions need a
stable audit trail.

## Decision

Durable architecture and governance decisions must be recorded as ADRs under
`docs/adr/`.

An ADR should include title, status, date, deciders, context, decision, and
consequences. If a later decision replaces it, the earlier ADR must be marked
superseded instead of deleted.

## Consequences

- Reviewers can understand why a constraint exists.
- Future Epics can evolve decisions without losing history.
- Architectural changes become explicit and reviewable.
- The Constitution remains compact while ADRs carry detailed rationale.
