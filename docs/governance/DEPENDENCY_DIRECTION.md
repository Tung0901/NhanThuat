# DEPENDENCY DIRECTION POLICY

**Document ID:** `DOC-GOV-002`  
**Effective Date:** July 23, 2026  
**Governance Authority:** Chief System Architect  
**Status:** **AUTHORITATIVE ARCHITECTURAL DIRECTIVE**  

---

## 1. STRICT UNIDIRECTIONAL IMPORT DIRECTIVES

To maintain physical and logical package isolation, all imports across NhanThuat, BusinessOS, and SalesOS MUST follow a strict downward unidirectional flow:

```
┌────────────────────────────────────────────────────────────────────────┐
│                     UNIDIRECTIONAL IMPORT RULES                        │
├────────────────────────────────────────────────────────────────────────┤
│  Layer 1: NhanThuat Core (src/nhan_thuat/)                             │
│  - Imports NOTHING from backend/app or salesos_pack                    │
│                                                                        │
│  Layer 2: BusinessOS Kernel (backend/app/)                             │
│  - Imports from src/nhan_thuat (Public Contracts Only)                 │
│  - Imports NOTHING from salesos_pack                                   │
│                                                                        │
│  Layer 3: SalesOS Industry Pack (salesos_pack/)                        │
│  - Imports from backend/app (Public Runtime Contracts Only)            │
│  - Imports from src/nhan_thuat (Public Knowledge Interfaces)           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. EXPLICIT IMPORT BOUNDARY RULES

1. **Rule 1 (NhanThuat Isolation):**
   - Files in `src/nhan_thuat/` MUST NOT import `backend.app` or `salesos_pack`.
   - NhanThuat operates as a zero-dependency external knowledge provider.

2. **Rule 2 (BusinessOS Kernel Isolation):**
   - Files in `backend/app/` MAY import `nhan_thuat`.
   - Files in `backend/app/` MUST NOT import `salesos_pack` domain implementations.

3. **Rule 3 (SalesOS Plugin Isolation):**
   - Files in `salesos_pack/` MAY import `backend.app` public contracts and `nhan_thuat` public contracts.
   - SalesOS MUST run as an external plugin package.

---

## 3. AUTOMATED COMPLIANCE VERIFICATION

These dependency directions are automatically enforced by static AST analysis in `tests/test_import_boundaries.py` during every CI build.
