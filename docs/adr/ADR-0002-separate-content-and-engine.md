# ADR-0002: Separate Knowledge Content And Engine

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Nhan Thuat contains both structured knowledge and software that operates on that
knowledge. Mixing the two would make it harder to review content independently,
change applications safely, and preserve canonical records.

## Decision

Knowledge content lives under `knowledge/`. Schemas live under `schemas/`.
Engine code lives under `src/nhan_thuat/`. Applications, generated outputs, and
future integrations must consume these layers instead of redefining them.

## Consequences

- Content review can happen without changing runtime code.
- Engine changes can be tested without rewriting knowledge records.
- Future user interfaces and AI features must cite or load repository-backed
  records.
- Schema changes become explicit project decisions, not incidental app behavior.
