# PRODUCT CONTEXT AND OWNERSHIP POLICY

**Document ID:** `DOC-GOV-001`  
**Effective Date:** July 23, 2026  
**Governance Authority:** BusinessOS & NhanThuat Product Owner  
**Status:** **AUTHORITATIVE CONSTITUTIONAL GOVERNANCE**  

---

## 1. PRODUCT BOUNDARIES AND OWNERSHIP

This document establishes the official product ownership boundaries separating **NhanThuat**, **BusinessOS**, and **SalesOS**.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM OWNERSHIP MAP                            │
├────────────────────────────────────────────────────────────────────────┤
│  NHANTHUAT (Independent Foundational Knowledge System)                │
│  - Knowledge Units, Laws, Principles, Models, Anti-Patterns            │
│  - Knowledge Schemas, Validation, Indexing & Dependency Graph         │
│  - Pure General-Purpose Knowledge Core                                 │
├────────────────────────────────────────────────────────────────────────┤
│  BUSINESSOS (Enterprise Operating System)                              │
│  - Enterprise Runtime, Orchestration & Memory                          │
│  - Capability Engine, Skill Runtime, Philosophy Router, Identity       │
│  - Plugin Framework & Storage Boundaries                               │
├────────────────────────────────────────────────────────────────────────┤
│  SALESOS (First Application Module inside BusinessOS)                  │
│  - Lead Intake & Assignment Workflow (SALESOS-CAP-001)                 │
│  - Sales Operations Coordinator Persona & Sales Domain Contracts       │
│  - External Plugin Pack (salesos_pack/)                                │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. PRODUCT DEFINITIONS

### 2.1 NHANTHUAT
NhanThuat is an **independent foundational knowledge system**. It owns:
- Knowledge Units, Laws, Principles, Models, Anti-Patterns
- Philosophical Knowledge Packs
- Knowledge Schemas (`schemas/knowledge-unit.schema.json`)
- Knowledge Validation, Indexing, and Transitive Dependency Graphs
- Knowledge Provenance and Query Contracts (`KnowledgeEngine`)

*Invariant:* NhanThuat is general-purpose external knowledge. It **MUST NOT** contain SalesOS business logic or depend on BusinessOS or SalesOS.

---

### 2.2 BUSINESSOS
BusinessOS is the **enterprise operating system**. It consumes NhanThuat through stable, versioned public contracts. It owns:
- Enterprise Runtime Engine (`BusinessOSRuntimeOrchestrator`)
- Capability Execution & Skill Runtime
- 7-Tier Memory Hierarchy
- Agent Coordination & Tool Runtime
- Telemetry Engine & Plugin Sandbox Context
- Department & Operational Modules

*Invariant:* BusinessOS is not the same product as NhanThuat. BusinessOS depends only on NhanThuat's public, versioned interfaces.

---

### 2.3 SALESOS
SalesOS is the **first practical business application module** implemented within BusinessOS.
- It is NOT a peer platform independent from BusinessOS.
- It is the first application and validation environment for BusinessOS.
- Future BusinessOS modules may include HR, Finance, Procurement, Marketing, Customer Service, and other enterprise functions.

---

## 3. UNIDIRECTIONAL DEPENDENCY RULE

```
SalesOS ──► Consumes ──► BusinessOS ──► Consumes ──► NhanThuat
```

- **NhanThuat** MUST NOT import BusinessOS or SalesOS.
- **BusinessOS** MUST NOT import SalesOS domain implementation.
- **SalesOS** MAY consume BusinessOS public contracts and NhanThuat approved knowledge.
