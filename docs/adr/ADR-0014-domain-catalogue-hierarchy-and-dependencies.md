# ADR-0014: Domain Catalogue, Hierarchy, And Dependencies

**Status:** accepted  
**Date:** 2026-07-21  
**Deciders:** Product Owner

## Context

Milestone 1 froze the Knowledge Core with five top-level taxonomy domains,
Batch 1 laws and principles, an Evidence Layer foundation, and a Knowledge
Factory foundation. Milestone 2 needs a production blueprint for domain-based
knowledge expansion without prematurely changing canonical taxonomy files or
generating new knowledge units.

The requested catalogue includes domain areas such as Human Nature, Motivation,
Leadership, Trust, Decision Making, Culture, and Ethics. These areas are more
specific than the five existing top-level domains and often cross-cut them.

## Decision

Propose preserving the five existing top-level domains and introducing a planning
layer of production domain areas beneath them.

Domain areas should be mapped to one primary top-level domain and one or more
secondary top-level domains. They should also declare dependencies on other
domain areas to guide authoring order, duplicate review, and conflict review.

Domain-area identifiers should be numeric and semantics-neutral, such as
`NT-DA-0001`, with mutable human meaning carried by a separate kebab-case slug
such as `human-nature`. Primary top-level domain means stewardship, not exclusive
conceptual ownership.

Dependency edges should be normalized by ID with direction, rationale, and edge
kind. Authoring-prerequisite edges should be acyclic inside a batch. Conceptual
influence edges may be cyclic but must not be confused with knowledge-unit
`depends_on` relations.

Domain-area catalogue changes should require a documented rationale, dependency
impact note, evidence plan, and Product Owner review before becoming Frozen.

Domain areas do not become canonical `knowledge/domains/` records during the
blueprint phase. A future Product Owner-approved implementation may introduce
first-class domain-area records if schema and validation support are approved.

## Consequences

- The Frozen EPIC 2 taxonomy remains backward-compatible.
- Domain expansion can be planned in detail without changing runtime or schemas.
- Cross-domain areas remain visible without creating too many top-level domains.
- Future catalogue implementation requires explicit schema and validation
  decisions.
- New top-level domains still require Product Owner review and an ADR.
- A later ADR is required if domain areas or concept clusters become first-class
  YAML records with schema, registry, catalog, or migration support.
