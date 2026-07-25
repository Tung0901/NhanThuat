# NhanThuat Public Contract V1

**Document ID:** `DOC-INT-001`
**Version:** v1.0.0

## Overview

The NhanThuat Public Contract V1 establishes a stable, versioned boundary for external consumers (e.g., BusinessOS, SalesOS) to query and retrieve knowledge units without coupling to internal NhanThuat implementations, schemas, or filesystem paths.

## 1. Core Principles

- **Immutability**: Public data contracts are strictly typed and immutable (e.g. `dataclass(frozen=True)`).
- **Isolation**: Public contracts do NOT expose internal `IndexedUnit` models. All data is translated into safe, public `KnowledgeUnitSummary` and `KnowledgeResult` structures.
- **Strict Dependencies**: Consumers MUST import from `nhan_thuat.public.v1` and NEVER from `nhan_thuat.knowledge_engine`.

## 2. Public Interfaces

The primary entry point is the `NhanThuatProviderV1` abstract base class, which provides:

- `get_unit(unit_id: str)`: Returns raw metadata of a single unit.
- `query_knowledge(query: KnowledgeQuery)`: Returns a `KnowledgeResult` matching criteria.
- `list_domain_units(domain_slug: str)`: Lists summaries of all units in a domain.
- `list_capabilities()`: Returns supported capability descriptors.
- `get_contract_metadata()`: Returns the exact semantic version of the contract.

## 3. Errors

Consumers must catch `PublicError` (and its subclasses, e.g. `InsufficientVerifiedKnowledgeError`). Internal engine exceptions (e.g., `ValueError`, schema errors) are not leaked.
