# ADR-0008: Validation Interfaces And Frozen Integrity

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Validation is required evidence but does not approve project content. EPIC 2
adds architecture-level validation checks while preserving schema validation.

## Decision

Keep `validate_repository()` as the public validation interface and extend it
with architecture checks for identifier/type consistency, filename conventions,
primary/secondary domain consistency, tag naming, known relation types, and
frozen-register integrity.

Frozen-register validation confirms that registered Frozen Epic sources exist
and remain marked `frozen`.

## Consequences

- Validation failures remain readable for review packages.
- Frozen status drift is detected without modifying Frozen deliverables.
- Future validators can add checks through the same issue-reporting interface.
- Product Owner approval remains separate from validation success.
