# Decision Making Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0015  
**Slug:** decision-making  
**Status:** ready_for_review  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0001 Human Nature** | authoring_prerequisite | Decision Making relies on understanding cognitive biases, load limits, and threat responses to explain why optimal decisions often fail. |
| **NT-DA-0008 Authority** | authoring_prerequisite | Understanding who holds legitimate power is necessary to establish final decision rights. |
| **NT-DA-0013 Communication** | authoring_prerequisite | Gathering evidence and framing choices requires effective transmission of information. |

## Downstream Domain Areas

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0016 Strategy** | authoring_prerequisite | Strategy is essentially a series of high-level, high-stakes decisions requiring tradeoffs. |
| **NT-DA-0017 Execution** | authoring_prerequisite | Execution is the realization of the commitment made during the decision process. |
| **NT-DA-0012 Negotiation** | authoring_prerequisite | Negotiation involves joint decision making under conflicting interests. |

## Recommended Authoring Order

```mermaid
graph TD
    UN-HN[NT-DA-0001 Human Nature] --> LAW-01(NT-LAW-0048: Decision Quality Independence)
    UN-AUTH[NT-DA-0008 Authority] --> LAW-02(NT-LAW-0049: Irreducible Uncertainty)
    UN-COM[NT-DA-0013 Communication] --> LAW-03(NT-LAW-0050: Opportunity Cost Permanence)
    LAW-01 --> PRIN-01(NT-PRINCIPLE-0078: Evaluate by Process)
    LAW-02 --> PRIN-02(NT-PRINCIPLE-0079: Bound Uncertainty)
    LAW-03 --> PRIN-03(NT-PRINCIPLE-0080: Make Costs Explicit)
    PRIN-01 --> MOD-01(NT-MODEL-0015: Decision Quality Model)
    PRIN-02 --> MOD-02(NT-MODEL-0016: Evidence-Risk Matrix)
    LAW-02 & PRIN-02 --> MOD-03(NT-MODEL-0017: Uncertainty Evaluation Model)
    PRIN-01 --> ANTI-01(NT-ANTI-PATTERN-0023: Outcome Bias)
    PRIN-02 --> ANTI-02(NT-ANTI-PATTERN-0024: Analysis Paralysis)
    UN-AUTH --> ANTI-03(NT-ANTI-PATTERN-0025: Authority Bias)
    LAW-02 --> ANTI-04(NT-ANTI-PATTERN-0026: False Certainty)
    UN-COM --> ANTI-05(NT-ANTI-PATTERN-0027: Decision by Popularity)
```
