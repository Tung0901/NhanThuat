# Contract Versioning Policy

**Document ID:** `DOC-INT-003`

## 1. Versioning Semantics

NhanThuat Public Contracts use standard Semantic Versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to the contract structure (e.g., removing a field from `KnowledgeUnitSummary`). Requires consumers to migrate to the new `nhan_thuat.public.v2` namespace.
- **MINOR**: Additions to the contract (e.g., adding a new optional field). Fully backwards compatible.
- **PATCH**: Internal bug fixes or performance improvements in the adapter that do not change the public API surface.

## 2. Namespace Guarantee

Once `nhan_thuat.public.v1` is declared stable, its structures are immutable. We will never break existing v1 consumers. Future major revisions will be placed in `nhan_thuat.public.v2`, allowing them to coexist simultaneously during migrations.
