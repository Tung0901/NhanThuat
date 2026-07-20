# ADR-0012: Knowledge Factory Workflow And Quality Gates

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Nhan Thuat now has Frozen governance, a Frozen knowledge architecture, a Frozen
law/principle seed library, and a ready-for-review Knowledge Foundation Batch 1.
Future growth requires a repeatable production workflow so large content batches
do not bypass taxonomy, ontology, evidence, validation, review, or Frozen
controls.

## Decision

Propose a Knowledge Factory workflow with explicit stages:

1. intake;
2. triage;
3. draft;
4. linking;
5. author self-check;
6. validation;
7. internal review;
8. ready-for-review packaging;
9. Product Owner approval;
10. freeze.

Each batch should pass scope, type, taxonomy, evidence, relation, duplicate,
conflict, readability, validation, test, and governance gates before being
marked ready for review.

Freeze remains a separate post-approval task and must not include new content
implementation or scope expansion.

## Consequences

- Large-scale knowledge creation becomes repeatable and auditable.
- Review capacity becomes a first-class constraint.
- Duplicate and conflict checks become explicit review obligations.
- Validation and tests remain required evidence but do not replace Product Owner
  approval.
- Future implementation may add schemas or tooling for batch status, review
  notes, duplicate warnings, and conflict disposition, but this ADR does not
  implement them.
