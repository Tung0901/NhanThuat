# ADR-0010: Evidence Layer Separation And Source Abstraction

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Nhan Thuat knowledge units currently include an inline evidence summary with a
qualitative level and references list. Knowledge Foundation Batch 1 uses this
structure with provisional evidence and empty references. This is valid for the
current architecture, but it is not sufficient for durable source traceability,
citation review, or future evidence-strengthening workflows.

Evidence has a different lifecycle from canonical knowledge. A law or principle
may stay stable while new evidence is added, corrected, contested, or deprecated.

## Decision

Propose making the Evidence Layer a first-class repository-backed content layer
separate from Canonical Knowledge.

Future evidence records should live in a dedicated evidence source path, such as
`knowledge/evidence/`, and should use stable `NT-EVIDENCE-0001` style IDs. They
should describe sources, evidence claims, support/contest/context links,
limitations, confidence metadata, and review state.

Canonical knowledge units should continue to express their reusable claim,
conditions, exceptions, risks, taxonomy classification, and relations. They
should reference evidence records rather than duplicate full source metadata.

Source metadata should use a source-kind abstraction so books, papers, web
pages, reports, observations, datasets, interviews, and internal documents can
share a common envelope while retaining source-specific locators.

## Consequences

- Existing knowledge units remain backward-compatible.
- Evidence can mature independently from law and principle content.
- Future registry and catalog work can expose evidence traceability without
  making generated outputs canonical.
- Validation can eventually detect broken evidence references and incomplete
  source metadata.
- Schema changes are required in a later implementation Epic, but this ADR does
  not modify schemas.
- Frozen content must not be edited directly during migration unless Product
  Owner-approved change control authorizes it.
