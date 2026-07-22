# Personality Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0003  
**Slug:** personality  
**Status:** frozen  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0001 Human Nature** | authoring_prerequisite | Personality requires a baseline model of human variation and adaptation mechanisms before differences are classified. |

## Downstream Domain Areas

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0005 Hiring** | authoring_prerequisite | Selection decisions and role fit assessments rely on modeling relatively stable individual traits and preferences. |
| **NT-DA-0007 Delegation** | authoring_prerequisite | Delegating task authority and responsibility depends on matching traits to role demands. |
| **NT-DA-0006 Team Building** | authoring_prerequisite | Team composition, cognitive diversity, and coordination defaults require trait-level analysis. |
| **NT-DA-0004 Leadership** | authoring_prerequisite | Leaders adapt leadership behaviors and environments to align with members' behavioral defaults. |
| **NT-DA-0018 Learning** | authoring_prerequisite | Instructional formats and feedback loops are tailored to cognitive preferences. |

## Recommended Authoring Order

To manage complexity and respect dependencies, the future content within NT-DA-0003 should be authored in the following order:

```mermaid
graph TD
    UN-HN[NT-DA-0001 Human Nature (Frozen)] --> LAW-01(Candidate Law: Relative Trait Stability)
    UN-HN --> LAW-03(Candidate Law: Probabilistic Default Expression)
    LAW-01 --> LAW-02(Candidate Law: Person-Role Fit)
    LAW-01 --> PRIN-01(Candidate Principle: Assess Defaults to Map Support)
    LAW-02 --> PRIN-02(Candidate Principle: Redesign Roles)
    LAW-03 --> PRIN-03(Candidate Principle: Adapt Communication)
    LAW-02 --> MOD-01(Candidate Model: Person-Role Fit Model)
    LAW-03 --> MOD-02(Candidate Model: Default Expression under Load Model)
    PRIN-01 --> ANTI-01(Candidate Anti-pattern: Willpower Fallacy)
    PRIN-01 --> ANTI-02(Candidate Anti-pattern: Tyranny of Typology)
    PRIN-02 --> ANTI-03(Candidate Anti-pattern: Homogeneity Trap)
```

1. **Foundational Laws:** Establish the relative stability of traits (`Relative Trait Stability`) and the probability of default expression under load (`Probabilistic Default Expression`).
2. **Derivative Laws:** Establish the cost dynamics of mismatch (`Person-Role Fit`).
3. **Core Principles & Models:** Operationalize the laws into assessment/adaptation heuristics (`Assess Defaults to Map Support`, `Redesign Roles`) and diagnostic patterns (`Person-Role Fit Model`, `Default Expression under Load Model`).
4. **Anti-patterns:** Map typical failure modes that violate these principles (`Willpower Fallacy`, `Tyranny of Typology`, `Homogeneity Trap`).
