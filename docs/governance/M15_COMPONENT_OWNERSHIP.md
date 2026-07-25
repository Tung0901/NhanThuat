# M15 COMPONENT OWNERSHIP CLASSIFICATION

**Document ID:** `DOC-GOV-003`  
**Effective Date:** July 23, 2026  
**Governance Authority:** BusinessOS & NhanThuat Technical Committee  
**Status:** **AUTHORITATIVE COMPONENT OWNERSHIP MAP**  

---

## 1. COMPONENT OWNERSHIP MATRIX

This classification assigns clear product ownership to all completed M15 files and directories across NhanThuat, BusinessOS, and SalesOS.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   M15 COMPONENT OWNERSHIP MAP                          │
├────────────────────────────────────────────────────────────────────────┤
│ NHANTHUAT-OWNED:                                                       │
│ - src/nhan_thuat/knowledge_engine.py                                  │
│ - knowledge/units/ (274 Units)                                         │
│ - schemas/ (JSON Validation Schemas)                                   │
│ - knowledge indexes, dependency graphs & SHA-256 checksums             │
├────────────────────────────────────────────────────────────────────────┤
│ BUSINESSOS-OWNED:                                                      │
│ - backend/app/engine/runtime.py (Runtime Orchestrator)                 │
│ - backend/app/engine/canonical_registry.py (Source Registry)           │
│ - backend/app/engine/philosophies/router.py (Philosophy Router)        │
│ - backend/app/engine/storage.py (Storage Boundary)                    │
│ - backend/app/main.py (Runtime REST APIs)                              │
├────────────────────────────────────────────────────────────────────────┤
│ SALESOS-OWNED:                                                         │
│ - salesos_pack/ (Plugin manifest, skills, persona, tool, schemas)      │
│ - /salesos/* REST Endpoints                                            │
│ - SalesOS Lead Intake & Assignment Workflow contracts                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PHYSICAL VS LOGICAL OWNERSHIP

Physical location in the repository does not alter product boundary rules:
- Files under `src/nhan_thuat/` are logically and physically owned by **NhanThuat Core**.
- Files under `backend/app/` are logically and physically owned by **BusinessOS Kernel**.
- Files under `salesos_pack/` are logically and physically owned by **SalesOS Plugin**.

All completed M15 implementations and test suites (116 passing tests) are retained in full.
