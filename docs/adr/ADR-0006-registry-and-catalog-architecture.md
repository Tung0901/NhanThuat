# ADR-0006: Registry And Catalog Architecture

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

EPIC 0 provided a simple registry mapping knowledge-unit IDs to source
documents. EPIC 2 requires a fuller architecture while preserving backward
compatibility.

## Decision

Use a repository-backed `KnowledgeRegistry` as the loaded in-memory model for
domains, knowledge units, and relations. Use `KnowledgeCatalog` as a deterministic
projection for generated catalog output and consumer-facing indexes.

Keep `build_registry()` backward-compatible by returning the original
`dict[id, document]` shape.

## Consequences

- Existing callers and tests remain compatible.
- Registry loading remains separate from generated catalog projection.
- Future API, UI, search, and AI consumers can read catalog projections without
  becoming canonical sources.
- Catalog fields can grow without changing source content.
