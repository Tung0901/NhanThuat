# ADR-0007: Identifier And Naming Conventions

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Stable identifiers are required for traceability, review, citations, and future
catalog/search behavior. EPIC 2 adds identifier parsing, generation, and naming
validation helpers.

## Decision

Identifiers remain permanent and type-prefixed. Knowledge-unit IDs use
`NT-TYPE-0001` style prefixes. Domain IDs preserve the existing compact
`NT-D01` form. File names for knowledge units must contain the record ID. Tags
must use lowercase kebab-case.

## Consequences

- Existing domain and knowledge-unit IDs remain valid.
- Future generated IDs can avoid collisions within each prefix.
- Renaming titles does not require ID changes.
- Naming problems are reported by validation before review.
