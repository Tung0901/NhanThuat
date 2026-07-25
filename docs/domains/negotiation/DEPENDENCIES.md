# Negotiation Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0012  
**Slug:** negotiation  
**Status:** frozen  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0008 Communication** | authoring_prerequisite | Negotiation requires clear framing and information exchange. |
| **NT-DA-0010 Trust** | authoring_prerequisite | Negotiation requires vulnerability acceptance to share true interests. |
| **NT-DA-0014 Influence** | authoring_prerequisite | Negotiation relies on reframing priorities prior to deal closure. |

## Downstream Domain Areas

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0015 Decision-Making** | authoring_prerequisite | Negotiation produces the agreed alternatives that leaders commit to. |
| **NT-DA-0017 Execution** | authoring_prerequisite | Executable negotiation terms define accountability during task delivery. |

## Recommended Authoring Order

```mermaid
graph TD
    UN-COM[NT-DA-0008 Communication] --> LAW-01(NT-LAW-0057: Interest-Position Decoupling)
    UN-TRU[NT-DA-0010 Trust] --> LAW-02(NT-LAW-0058: Integrative Value Creation)
    UN-INF[NT-DA-0014 Influence] --> LAW-03(NT-LAW-0059: Agreement Stability Asymmetry)
    LAW-01 --> PRIN-01(NT-PRINCIPLE-0087: Focus on Underlying Interests)
    LAW-02 --> PRIN-02(NT-PRINCIPLE-0088: Expand Value Before Allocation)
    LAW-03 --> PRIN-03(NT-PRINCIPLE-0089: Anchor in Objective Criteria)
    PRIN-01 & PRIN-02 --> MOD-01(NT-MODEL-0022: Negotiation Flow Pipeline)
    LAW-02 & PRIN-03 --> MOD-02(NT-MODEL-0023: Value Creation-Allocation Matrix)
    PRIN-01 --> ANTI-01(NT-ANTI-PATTERN-0036: Positional Bargaining Lock)
    LAW-02 --> ANTI-02(NT-ANTI-PATTERN-0037: Zero-Sum Illusion)
    PRIN-02 --> ANTI-03(NT-ANTI-PATTERN-0038: Premature Concession Surrender)
    LAW-03 --> ANTI-04(NT-ANTI-PATTERN-0039: Agreement Instability)
```
