# ADR-0003: Product Owner Approval And Frozen Control

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Validation proves structure, not truth. Tests prove expected behavior, not
project approval. Nhan Thuat needs a clear authority boundary between execution
and approval.

## Decision

Only the Product Owner may approve Epics, mark content Approved, or mark content
Frozen.

Codex may prepare changes, run validation, run tests, and produce review
packages, but must not self-approve or self-freeze content.

## Consequences

- Approval remains a human governance act.
- Automated checks remain evidence, not authority.
- Frozen content is protected from direct edits.
- Future changes to Frozen content require a Change Request and impact review.
