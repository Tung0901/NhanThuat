# Negotiation Domain Architecture

**Domain Area:** NT-DA-0012  
**Slug:** negotiation  
**Status:** frozen  
**Wave:** Milestone 2 Wave 4  
**Review Owner:** Chief Architect or delegated Negotiation domain reviewer  

## 1. Domain Purpose

The Negotiation domain area defines the structured organizational process of aligning divergent interests, expanding mutual value, allocating scarce resources, and reaching sustainable, executable agreements. Within NhanThuat, Negotiation converts social influence and established trust into binding, commitments-backed agreements that precede decision commitment and execution.

## 2. Core Questions

*   How do parties discover underlying interests rather than locking into rigid positions?
*   How can mutual value be created and expanded before resource allocation occurs?
*   How are agreements stabilized to prevent post-signature erosion and breach?
*   How is structural trust preserved during hard resource allocation discussions?
*   How should negotiation strategies adapt when power or information is asymmetric?
*   How should BusinessOS recommend negotiation tactics and support AI negotiation assistants?

## 3. Boundary Rules & Strict Distinctions

| Concept | Versus | Concept | Operational Distinction |
| --- | --- | --- | --- |
| **Negotiation** | vs | **Persuasion** | Persuasion is the communicative act of shifting frames (`NT-DA-0014`). Negotiation is the multi-party structural process of exchanging commitments and allocating value. |
| **Negotiation** | vs | **Influence** | Influence shifts underlying beliefs and priorities (`NT-DA-0014`). Negotiation translates those shifted priorities into explicit, binding agreement terms. |
| **Negotiation** | vs | **Authority** | Authority enforces compliance by positional command (`NT-DA-0013`). Negotiation resolves divergent interests through voluntary, multi-lateral agreement. |
| **Negotiation** | vs | **Manipulation** | Manipulation uses hidden intent and deceptive framing (`NT-ANTI-PATTERN-0032`). Negotiation relies on transparent interest discovery and objective criteria. |
| **Negotiation** | vs | **Conflict** | Conflict is the state of opposing interests or emotional friction (`NT-DA-0011`). Negotiation is a structured mechanism used to resolve conflict constructively. |
| **Negotiation** | vs | **Mediation** | Mediation involves an independent third-party facilitator (`NT-DA-0011`). Negotiation is the direct interaction between primary stakeholders. |
| **Negotiation** | vs | **Compromise** | Compromise splits the difference between positions (often reducing total value). Integrative Negotiation expands options to meet core interests before splitting value. |
| **Negotiation** | vs | **Selling** | Selling uncovers customer needs and positions product value (`NT-DA-0014`). Negotiation deals with specific contract terms, pricing, risk allocation, and commitments. |

## 4. Architectural Position

```text
[Communication: NT-DA-0008] (Meaning Transmission)
         ↓
[Trust: NT-DA-0010] (Vulnerability & Verification Cadence)
         ↓
[Influence: NT-DA-0014] (Value Reframing & Priority Shift)
         ↓
[NEGOTIATION: NT-DA-0012] (Interest Alignment & Executable Agreement)
         ↓
[Decision-Making: NT-DA-0015] (Option Selection & Resource Commitment)
         ↓
[Execution: NT-DA-0017] (Effort Mobilization & Action Delivery)
```

## 5. Candidate Knowledge Inventory

### Proposed Laws
*   **NT-LAW-0057:** Interest-Position Decoupling
*   **NT-LAW-0058:** Integrative Value Creation
*   **NT-LAW-0059:** Agreement Stability Asymmetry

### Proposed Principles
*   **NT-PRINCIPLE-0087:** Focus on Underlying Interests
*   **NT-PRINCIPLE-0088:** Expand Value Before Allocation
*   **NT-PRINCIPLE-0089:** Anchor Agreements in Objective Criteria

### Proposed Models
*   **NT-MODEL-0022:** Negotiation Flow Pipeline
*   **NT-MODEL-0023:** Value Creation-Allocation Matrix

### Proposed Anti-patterns
*   **NT-ANTI-PATTERN-0036:** Positional Bargaining Lock
*   **NT-ANTI-PATTERN-0037:** Zero-Sum Illusion
*   **NT-ANTI-PATTERN-0038:** Premature Concession Surrender
*   **NT-ANTI-PATTERN-0039:** Agreement Instability

## 6. BusinessOS Capability & AI Mapping

Negotiation knowledge units provide direct integration hooks for BusinessOS capability modules:
- **Sales & Price Negotiation:** Structuring win-win deal terms without discounting brand equity.
- **Procurement & Vendor Management:** Balancing supplier risk allocation with cost optimization.
- **Conflict Resolution:** Uncovering hidden interests in cross-departmental disputes.
- **Contract Discussion:** Establishing objective benchmarks for service-level agreements (SLAs).
- **Internal Resource Allocation:** Balancing headcount and budget requests across competing teams.
- **CRM Recommendation Engine & AI Assistant:** Generating real-time BATNA (Best Alternative to a Negotiated Agreement) assessments and trade-off recommendations during live negotiations.
