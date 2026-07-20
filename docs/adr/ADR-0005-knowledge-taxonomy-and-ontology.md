# ADR-0005: Knowledge Taxonomy And Ontology

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

EPIC 2 introduces typed knowledge records, a taxonomy model, and an ontology
relationship model. These choices constrain future schemas, validation, catalog
generation, and retrieval behavior.

## Decision

Keep the five existing domains as the top-level taxonomy layer and represent
domain-local topics inside domain records. Keep the initial ontology relation
vocabulary backward-compatible with existing knowledge units:

- `supports`
- `conflicts_with`
- `depends_on`
- `applies_to`

Relation semantics are modeled in code through relation specifications and
expanded from embedded knowledge-unit relation blocks.

## Consequences

- Existing domain and knowledge-unit files remain valid.
- The ontology can grow later through explicit ADR review.
- Future graph features can use relation metadata without changing source YAML.
- New top-level domains or relation types require Product Owner review.
