# Hiring Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0005  
**Slug:** hiring  
**Status:** ready_for_review  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0001 Human Nature** | authoring_prerequisite | Selection must account for cognitive biases. |
| **NT-DA-0003 Personality** | authoring_prerequisite | Hiring must avoid the tyranny of typology. |
| **NT-DA-0004 Leadership** | authoring_prerequisite | Leaders are the primary agents of selection. |

## Knowledge Unit Flow

```mermaid
graph TD
    UN-PE[NT-DA-0003 Personality] --> LAW-40(NT-LAW-0040: Predictive Limits)
    UN-HN[NT-DA-0001 Human Nature] --> LAW-41(NT-LAW-0041: Signal Distortion)
    LAW-40 --> PRIN-66(NT-PRINCIPLE-0066: Select for structural fit)
    LAW-41 --> PRIN-67(NT-PRINCIPLE-0067: Standardize evaluation)
    LAW-40 & LAW-41 --> PRIN-68(NT-PRINCIPLE-0068: Interviews as hypotheses)
    LAW-40 --> MOD-11(NT-MODEL-0011: Context-Behavior Predictive Model)
    PRIN-66 --> ANTI-15(NT-ANTI-PATTERN-0015: Culture Fit Trap)
    PRIN-67 --> ANTI-16(NT-ANTI-PATTERN-0016: Intuition Fallacy)
```
