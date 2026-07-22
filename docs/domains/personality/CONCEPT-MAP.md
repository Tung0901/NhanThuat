# Personality Concept Map

**Domain Area:** NT-DA-0003  
**Slug:** personality  
**Status:** frozen  

## Core Question

What relatively stable individual differences in temperament, sensitivity, cognitive preferences, and behavioral defaults exist among individuals, and how do they interact with environmental contexts and role demands to shape action and adaptation costs?

## Concept Clusters

| Cluster | Scope | Units |
| --- | --- | --- |
| temperament-and-sensitivity | Sensory-emotional sensitivity, threat reactivity, baseline energy, and stimulation limits. | NT-LAW-0034 |
| cognitive-and-interaction-preferences | Enduring preferences in information processing, thinking styles, risk tolerance, and interpersonal defaults. | NT-PRINCIPLE-0062, NT-ANTI-PATTERN-0010 |
| trait-context-interaction | How environment, incentives, and situation strength amplify, suppress, or redirect trait expression. | NT-LAW-0036, NT-MODEL-0008 |
| person-role-fit-and-adaptation | Conceptual alignment of individual traits with roles, and the physiological/cognitive costs of adapting behavior. | NT-LAW-0035, NT-PRINCIPLE-0060, NT-PRINCIPLE-0061, NT-MODEL-0007, NT-ANTI-PATTERN-0009, NT-ANTI-PATTERN-0011 |

## Ontological Chain: Trait to Behavior

To model individual differences dynamically and avoid deterministic fallacies, this domain establishes the following ontological chain:

*   **Trait:** Latent, relatively stable cognitive, sensory-emotional, or behavioral disposition. Traits represent baseline preferences and defaults that remain relatively stable across time but are adaptive, capable of gradual development, and not fixed.
*   **Trait Expression:** The interaction layer between latent traits and situation strength/contextual factors. It represents the active manifestation tendency of a trait under specific environmental pressures or situation-strength cues, before transforming into concrete behavior.
*   **Observed Behavior:** The context-dependent, concrete action or response displayed by an individual. Observed behavior is not dictated by traits alone; it emerges dynamically from the interaction of trait expression, skills, motivation, experience, and conscious self-regulation under specific situational constraints.

## Cross-Domain Dependencies

Personality builds upon upstream foundations in:
- **Human Nature (`NT-DA-0001`):** Biological needs, cognitive load, basic threat/reward responses, and core adaptation cycles.

Personality provides upstream assumptions and constraints for downstream areas:
- **Hiring (`NT-DA-0005`):** Assessing relatively stable individual differences, traits, and role-environment fit.
- **Delegation (`NT-DA-0007`):** Assigning task authority and responsibility aligned with individual capability and trait defaults.
- **Team Building (`NT-DA-0006`):** Designing team composition, managing cognitive diversity, and avoiding homogeneous blind spots.
- **Leadership (`NT-DA-0004`):** Modulating leadership styles to align with group members' stable defaults.
- **Learning (`NT-DA-0018`):** Designing instruction and feedback paths tailored to cognitive styles.

## Completeness Criteria

This domain foundation is complete and ready for review when:
- Every concept cluster contains at least one approved Law or Model and one operational Principle;
- Anti-patterns document common operational failures (such as typing/stereotyping or ignoring fit) and reference violated Laws or Principles;
- Every Principle explicitly depends on one or more Laws;
- No branded taxonomies (such as MBTI, DISC, or Enneagram) are used as foundational canonical ontology;
- Validation, tests, and review package evidence pass.

## Structured Cluster Records

### PER-CL-001 — temperament-and-sensitivity

- **Definition:** Sensory-emotional sensitivity, reactivity, baseline energy, and limits under stimulation.
- **In scope:** Introversion/extroversion defaults, sensory processing sensitivity, threat reactivity, emotional stability, energy recovery modes.
- **Out of scope:** General biological threat responses (Human Nature).
- **Core questions:** Why do individuals have varying tolerance for high-stimulation environments? How do sensory limits affect default performance?
- **Units:** NT-LAW-0034.

### PER-CL-002 — cognitive-and-interaction-preferences

- **Definition:** Relatively stable cognitive patterns, thinking styles, decision-making defaults, and interpersonal interaction preferences.
- **In scope:** Detail focus vs. big-picture preference, risk aversion traits, structured vs. emergent planning style, task-oriented vs. relation-oriented defaults.
- **Out of scope:** Specific negotiation tactics (Negotiation), general cognitive biases (Human Nature).
- **Core questions:** What relatively stable cognitive styles govern how people structure their thoughts? How do interpersonal defaults affect communication patterns?
- **Units:** NT-PRINCIPLE-0062, NT-ANTI-PATTERN-0010.

### PER-CL-003 — trait-context-interaction

- **Definition:** How environmental factors, incentives, and situation strength amplify, suppress, or redirect trait expression.
- **In scope:** Trait activation theory, situation strength (strong vs. weak situations), behavioral adaptation, masking, self-regulation limits under load.
- **Out of scope:** Generic self-regulation fatigue (Human Nature), standard productivity habits (Motivation).
- **Core questions:** How does a "strong situation" override natural trait defaults? What happens when situational demands force masking over long periods?
- **Units:** NT-LAW-0036, NT-MODEL-0008.

### PER-CL-004 — person-role-fit-and-adaptation

- **Definition:** Alignment between relatively stable individual traits and organizational/role demands, including the physiological and cognitive costs of acting against defaults.
- **In scope:** Person-role fit assessment, adaptation friction, role adjustment strategies, cognitive load of long-term trait mismatch, coping mechanisms.
- **Out of scope:** Hiring selection workflows (Hiring), formal delegation authority (Delegation).
- **Core questions:** What is the operational cost of acting against stable trait defaults? How can roles be adjusted to align with stable traits?
- **Units:** NT-LAW-0035, NT-PRINCIPLE-0060, NT-PRINCIPLE-0061, NT-MODEL-0007, NT-ANTI-PATTERN-0009, NT-ANTI-PATTERN-0011.
