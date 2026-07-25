# Influence Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0014  
**Slug:** influence  
**Status:** frozen  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0001 Human Nature** | authoring_prerequisite | Influence relies on understanding human perception, threat reflexes, and cognitive filters. |
| **NT-DA-0008 Communication** | authoring_prerequisite | Influence requires clear signal framing and meaning transmission channels. |
| **NT-DA-0010 Trust** | authoring_prerequisite | Legitimate influence depends on established structural trust and vulnerability acceptance. |

## Downstream Domain Areas

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0015 Decision-Making** | authoring_prerequisite | Influence shifts how options and uncertainty are evaluated before decisions are finalized. |
| **NT-DA-0017 Execution** | authoring_prerequisite | Influence ensures voluntary commitment during effort mobilization. |
| **NT-DA-0012 Negotiation** | authoring_prerequisite | Influence shapes the perceived value baseline prior to formal concession exchanges. |

## Recommended Authoring Order

```mermaid
graph TD
    UN-HN[NT-DA-0001 Human Nature] --> LAW-01(NT-LAW-0054: Legitimate Influence Mechanism)
    UN-COM[NT-DA-0008 Communication] --> LAW-02(NT-LAW-0055: Reframing Commitment Shift)
    UN-TRU[NT-DA-0010 Trust] --> LAW-03(NT-LAW-0056: Influence Degradation under Coercion)
    LAW-01 --> PRIN-01(NT-PRINCIPLE-0084: Align with Shared Purpose)
    LAW-02 --> PRIN-02(NT-PRINCIPLE-0085: Decouple from Power)
    LAW-01 & LAW-02 --> PRIN-03(NT-PRINCIPLE-0086: Design Transparent Value Frames)
    PRIN-01 & PRIN-02 --> MOD-01(NT-MODEL-0020: Influence Bridge Pipeline)
    LAW-02 & PRIN-03 --> MOD-02(NT-MODEL-0021: Legitimate Persuasion Matrix)
    PRIN-03 --> ANTI-01(NT-ANTI-PATTERN-0032: Manipulative Framing)
    PRIN-02 --> ANTI-02(NT-ANTI-PATTERN-0033: Coercive Leverage)
    LAW-02 --> ANTI-03(NT-ANTI-PATTERN-0034: Persuasion Isolation)
    PRIN-01 --> ANTI-04(NT-ANTI-PATTERN-0035: Pseudo-Consensus)
```
