# ADR-0001: Repository As Source Of Truth

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Nhan Thuat can receive input from conversation, notes, documents, and future
interfaces. Without one canonical source, content would become difficult to
audit, validate, review, or freeze.

## Decision

The repository is the official source of truth for project content, governance,
schemas, tests, and implementation.

Conversation and external materials are inputs only. They become official when
they are represented in repository files and pass the required process.

## Consequences

- Reviewers can inspect project state directly from version control.
- Validation and test evidence can be tied to exact files and commits.
- Generated files, applications, and AI outputs must trace back to repository
  content.
- Future integrations must not bypass repository governance.
