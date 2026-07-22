# Personality Domain Architecture

**Domain Area:** NT-DA-0003  
**Slug:** personality  
**Status:** frozen  
**Wave:** Milestone 2 Wave 1  
**Review Owner:** Product Owner or delegated Personality domain reviewer  

## 1. Domain Purpose

The Personality domain area defines relatively stable individual differences in temperament, sensitivity, cognitive processing preferences, and behavioral defaults. Rather than treating personality as a fixed, immutable state, NhanThuat models personality as relatively stable yet adaptive and capable of gradual development. It provides the framework for understanding how individuals differ in their baseline tendencies, how these tendencies interact with environmental context and situation strength to shape trait expression, and the systemic adaptation costs incurred when individuals adapt their behavior to meet role demands. It bridges the gap between universal human nature mechanics and the practical application areas of role placement, team coordination, and leadership.

## 2. Core Questions

* What relatively stable individual differences exist in cognitive, sensory-emotional, and behavioral defaults?
* How does the interaction between individual traits and situation strength govern trait expression and observed behavior?
* What are the cognitive and physiological costs of behavioral adaptation (acting against defaults)?
* How do we measure and leverage fit without falling into stereotyping, bias, or deterministic fallacies?

## 3. Boundary Rules with Adjacent Domains

To prevent conceptual duplication and maintain clear boundaries across the repository, the following rules apply:

| Adjacent Domain | In-scope for Personality | Out-of-scope (Steward Domain) |
| --- | --- | --- |
| **Human Nature (`NT-DA-0001`)** | Individual variations in baseline sensitivity, defaults, and adaptation limits. | Universal human biological drives, needs, threat reflexes, and cognitive limits. |
| **Motivation (`NT-DA-0002`)** | Stable preferences for autonomy, task structure, or social affiliation. | Dynamic drivers of effort, rewards, goals, persistence, and feedback loops. |
| **Hiring (`NT-DA-0005`)** | Conceptual person-role fit models and limits of psychometric testing. | Workflows, recruitment processes, selection algorithms, and onboarding tasks. |
| **Delegation (`NT-DA-0007`)** | Cognitive compatibility between delegation style and recipient traits. | Assignment authority, task tracking, accountability rules, and delegation workflows. |
| **Team Building (`NT-DA-0006`)** | The dynamics of cognitive diversity and trait complementarity. | Team operating norms, rituals, team formation stages, and meeting cadences. |

## 4. Ontological Chain: Trait to Behavior

To prevent deterministic fallacies, NhanThuat distinguishes between latent dispositions and manifest actions using a three-part ontological chain:

1.  **Trait:** Latent, relatively stable cognitive, sensory-emotional, or behavioral dispositions. Traits represent default baselines and preferences that resist rapid change but are adaptive, capable of gradual development, and not fixed.
2.  **Trait Expression:** The active interaction layer between latent traits and situation strength or context. It represents how strongly a latent trait is activated and manifested in a given situation before being moderated into concrete actions.
3.  **Observed Behavior:** The final, context-dependent concrete action or response displayed by an individual. It is not dictated by traits alone; instead, it emerges dynamically from the interaction of trait expression, skills, motivation, experience, environment, and deliberate self-regulation under specific situational constraints.

## 5. Proposed Knowledge-Unit Families

The proposed knowledge structure comprises:
* **Laws:** Ground-truth observations about relative trait stability, context/situation strength interaction, and adaptation costs.
* **Principles:** Actionable operational heuristics for role design, communication adaptation, and environmental adjustments.
* **Models:** Structural and diagnostic patterns explaining fit and default expression under load.
* **Anti-patterns:** Common organizational failure modes in typing, willpower expectations under mismatch, and team composition.

## 6. Candidate Knowledge Inventory

*IMPORTANT: These are proposals only. Canonical YAML knowledge units are not yet created.*

### Candidate Laws

1. **Law of Relative Trait Stability:** Individuals exhibit relatively stable cognitive, sensory-emotional, and behavioral preferences that act as default operational tendencies. Rather than being fixed or immutable, personality is adaptive and capable of gradual development, though it functions as a baseline default in everyday environments.
2. **Law of Person-Role Fit (Adaptation Cost):** Personality traits alone must never be used to predict performance. Performance emerges dynamically from the complex interaction of seven factors: Personality (latent defaults), Skills (capabilities), Motivation (drivers), Environment (context), Role demands (expectations), Experience (background), and Deliberate self-regulation (executive control). Person-role fit models the alignment of latent defaults with role demands to estimate potential adaptation costs (physiological/cognitive energy needed to adapt behavior), representing a diagnostic, probabilistic, and hypothesis-generating tool rather than a predictive performance filter.
3. **Law of Probabilistic Default Expression under Load:** Under sustained cognitive, emotional, or physical load, executive control limits are stressed, increasing the probability that an individual's behavioral expression will fall back on latent default patterns (behavioral defaults). This shift is probabilistic and depends on the interaction of cognitive load, environmental demands, and current executive control resources, without assuming a literal resource depletion (ego depletion) mechanism.

### Candidate Principles

1. **Assess trait defaults to map adaptation support:** Map cognitive and interaction defaults to understand adaptation costs and guide environment or role customization, rather than using fit as a hiring filter, exclusion criterion, or competence judgement.
2. **Redesign roles before demanding personality change:** When performance lags due to trait-role mismatch, prefer adjusting the task, tools, or environmental context rather than demanding personality modification.
3. **Adapt communication to trait preferences:** Tailor communication formats (e.g., structured/written vs. emergent/verbal) to the recipient's processing defaults rather than the sender's.

### Candidate Models

1. **Person-Role Fit Model:** A diagnostic, hypothesis-generating model mapping role demands, environmental situation strength, and latent trait baselines to estimate adaptation friction and energy consumption, rather than predicting performance.
2. **Default Expression under Load Model:** A diagnostic model mapping cognitive load and situational constraints to predict the probability of behavioral default expression as executive control capacity shifts.

### Candidate Anti-patterns

1. **Willpower Fallacy in Trait Mismatch:** Treating performance failures caused by long-term trait-role mismatch and high adaptation costs as personal willpower, motivation, or attitude failures.
2. **Tyranny of Simplistic Typology:** Using branded test categories (e.g., MBTI, DISC) as absolute, immutable labels to pigeonhole, exclude, or make deterministic hiring/placement decisions.
3. **Homogeneity Trap:** Building teams with identical personality profiles to reduce short-term friction, resulting in massive collective blind spots.

## 7. Evidence and Taxonomy Policy

* **Construct-Level Focus:** Knowledge units must use general, construct-level psychological terms (e.g., sensory processing sensitivity, cognitive style, risk tolerance) rather than trademarked typologies.
* **Provisional Evidence Posture:** All units should start with provisional evidence and explicitly state scientific consensus vs. contestability. Popular typologies may only be cited as examples of tools, never as canonical truth.
* **Taxonomy Alignment:** Primary top-level domain is `tri-nhan`. Secondary top-level domains are `dung-nhan` and `tu-than`.

## 8. Ethical Safeguards

1. **Probabilistic representation:** Traits represent statistical likelihoods of trait expression under specific conditions, not mechanical determinants of observed behavior. Performance is an emergent outcome of personality, skills, motivation, environment, role demands, experience, and deliberate self-regulation. Personality alone must never predict performance.
2. **Traits do not equal competence:** A person's personality trait profile indicates their *default style*, not their capacity to perform or learn a skill. Person-role fit is diagnostic, probabilistic, and hypothesis-generating; it must never be used as a competence judgement, exclusion criterion, or hiring filter.
3. **Traits do not equal ethics:** Stable preferences are morally neutral and must never be used to judge moral worth or integrity.
4. **Anti-discrimination:** Personality data must never be used to justify discrimination, exclusion, or systemic degradation of dignity.
5. **Contextual amplification:** Situational strength can amplify, suppress, or redirect trait expression.
6. **Compensating behaviors:** Individuals have agency and can learn compensatory strategies, skills, and adaptive behaviors to manage adaptation costs.
7. **Direct observation precedence:** Personality labels must never override direct observation, performance data, and empirical evidence.

## 9. Open Architectural Questions

* How should the Evidence Layer model the scientific contestability of personality frameworks like the Big Five vs. MBTI?
* Should NhanThuat introduce a metadata tag for "trait sensitivity" to automatically trigger validation warnings when principles are misapplied deterministically?
* How can BusinessOS interfaces safely present person-role fit recommendations without encouraging user bias, stereotyping, or predictive exclusion?

## 10. Blueprint Acceptance Criteria

This blueprint is accepted when:
1. The domain registry contains `NT-DA-0003` as `personality`.
2. All five blueprint files (`status.yaml`, `CONCEPT-MAP.md`, `ARCHITECTURE.md`, `DEPENDENCIES.md`, `GLOSSARY.md`) are created and validate successfully under the `validate_all.py` script.
3. The Product Owner reviews and signs off on the boundary rules and ethical safeguards.
