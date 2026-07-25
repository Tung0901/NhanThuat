# Team Building Cross-Domain Dependency Mapping

**Domain Area:** NT-DA-0006  
**Slug:** team-building  
**Status:** ready_for_review  

## Upstream Dependencies

| Upstream Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0003 Personality** | authoring_prerequisite | Team composition relies on understanding complementary trait defaults. |
| **NT-DA-0004 Leadership** | authoring_prerequisite | Leaders are responsible for designing structural interdependence. |
| **NT-DA-0005 Hiring** | authoring_prerequisite | Selection provides the raw material (individuals) that must be integrated. |

## Downstream Dependencies

| Target Domain Area | Dependency Kind | Rationale |
| --- | --- | --- |
| **NT-DA-0010 Trust** | limits_scope | Trust emerges within the structural bounds set by team building. |
| **NT-DA-0011 Conflict** | limits_scope | Cognitive diversity naturally generates conflict, requiring resolution frameworks. |

## Knowledge Unit Flow

```mermaid
graph TD
    UN-PE[NT-DA-0003 Personality] --> LAW-42(NT-LAW-0042: Cognitive Diversity)
    UN-LE[NT-DA-0004 Leadership] --> LAW-43(NT-LAW-0043: Structural Interdependence)
    LAW-42 --> PRIN-69(NT-PRINCIPLE-0069: Design for cognitive diversity)
    LAW-43 --> PRIN-70(NT-PRINCIPLE-0070: Establish boundaries via purpose)
    LAW-43 --> PRIN-71(NT-PRINCIPLE-0071: Force interdependence)
    LAW-42 --> MOD-12(NT-MODEL-0012: Cohesion-Friction Curve)
    PRIN-69 --> ANTI-17(NT-ANTI-PATTERN-0017: Clone Factory)
    PRIN-71 --> ANTI-18(NT-ANTI-PATTERN-0018: Siloed Team)
```
