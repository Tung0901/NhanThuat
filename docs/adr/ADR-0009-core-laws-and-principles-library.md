# ADR-0009: Core Laws And Principles Library

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

EPIC 3 introduces the first curated set of laws and principles as managed
knowledge units. These records should exercise the EPIC 2 architecture without
adding runtime features or broad content expansion.

## Decision

Represent EPIC 3 content as YAML knowledge units under `knowledge/units/`, using
the existing `law` and `principle` types. Keep the first library small,
provisional, and relation-aware. Principles depend on laws they operationalize.
When EPIC 3 is Frozen, these initial units become Frozen content and future
changes require the formal change-control process.

## Consequences

- The registry and catalog expand through source content, not new runtime scope.
- Existing IDs remain stable and are not rewritten.
- Evidence can be strengthened later without changing record identity.
- Future content expansion can follow the same law/principle pattern.
