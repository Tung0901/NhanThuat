# Communication Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0008  
**Slug:** communication  
**Status:** ready_for_review  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0001 Human Nature** | authoring_prerequisite | Baseline cognitive limits shape how much information can be processed. |
| **NT-DA-0003 Personality** | authoring_prerequisite | Trait defaults dictate differing interpretive frameworks and communication preferences. |

## Downstream Dependencies

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **All Other Domains** | foundational | Delegation, Team Building, Trust, and Execution all require closed-loop communication to function. |

## Knowledge Unit Flow

```mermaid
graph TD
    UN-PE[NT-DA-0003 Personality] --> LAW-46(NT-LAW-0046: Interpretive Variance)
    UN-HN[NT-DA-0001 Human Nature] --> LAW-47(NT-LAW-0047: Signal Degradation)
    LAW-47 --> PRIN-75(NT-PRINCIPLE-0075: Separate transmission from confirmation)
    LAW-46 --> PRIN-76(NT-PRINCIPLE-0076: Distinguish failure from disagreement)
    LAW-46 --> PRIN-77(NT-PRINCIPLE-0077: Decouple communication from influence)
    LAW-46 & LAW-47 --> MOD-14(NT-MODEL-0014: Closed-Loop Transmission Model)
    PRIN-75 --> ANTI-21(NT-ANTI-PATTERN-0021: Broadcast Fallacy)
    LAW-46 --> ANTI-22(NT-ANTI-PATTERN-0022: Semantic Illusion)
```
