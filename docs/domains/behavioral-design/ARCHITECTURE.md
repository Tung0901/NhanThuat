# Behavioral Design Domain Architecture

**Domain Area:** NT-DA-0028  
**Slug:** behavioral-design  
**Category:** CAT-BEHAVIORAL  
**Status:** review

## 1. Domain Purpose

How can products, processes, and environments be designed to steer behavior reliably and ethically?

## 2. Core Questions

*   Goal Gradient Effect: As people get closer to a goal, their efforts accelerate.
*   Zeigarnik Effect: People remember uncompleted or interrupted tasks better than completed tasks.
*   Variable Reward Schedule: Rewards delivered on an unpredictable, variable ratio schedule are highly effective at maintaining continuous behavior.
*   Temptation Bundling: Combining a behavior that is good for you in the long run with a behavior that feels good in the short run.
*   Decision Fatigue (Ego Depletion): The deteriorating quality of decisions made by an individual after a long session of decision making.
*   Implementation Intentions: A self-regulatory strategy in the form of an 'if-then' plan that leads to better goal attainment.
*   Overjustification Effect (Extrinsic Crowding-Out): Providing an external reward for an activity that was already intrinsically rewarding decreases a person's intrinsic motivation to perform it.
*   Pre-commitment: Making a binding decision in advance when in a cold, rational state to prevent acting irrationally in a future hot state.
*   Commitment Devices: Voluntarily constraining future choices to prevent oneself from acting against long-term interests.
*   Goal Shielding: Actively inhibiting alternative goals or distractions to protect the focal goal.
*   Environment Design for Habituation: Modifying physical or digital spaces to make good behaviors obvious and easy, and bad behaviors invisible and difficult.
*   Minimum Viable Routine (Tiny Habits): Scaling down a desired new behavior to an absurdly small, easily executable version to guarantee consistency.
*   Action Prompting (Contextual Triggers): Anchoring a new habit to an existing, reliable habit rather than relying on time or memory.
*   Habit Loop (Cue-Routine-Reward): A neurological loop that governs any habit, consisting of a cue that triggers the brain, a routine (the behavior itself), and a reward.
*   Fogg Behavior Model (B=MAP): Behavior (B) happens when three elements converge at the same moment: Motivation (M), Ability (A), and a Prompt (P).

## 3. Taxonomy Alignment

*   **Primary domain lens:** `tri-nhan`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Model | NT-MODEL-3201 | Habit Loop (Cue-Routine-Reward) | review |
| Model | NT-MODEL-3202 | Fogg Behavior Model (B=MAP) | review |
| Phenomenon | NT-PHENOMENON-3201 | Goal Gradient Effect | review |
| Phenomenon | NT-PHENOMENON-3202 | Zeigarnik Effect | review |
| Phenomenon | NT-PHENOMENON-3203 | Variable Reward Schedule | review |
| Phenomenon | NT-PHENOMENON-3204 | Temptation Bundling | review |
| Phenomenon | NT-PHENOMENON-3205 | Decision Fatigue (Ego Depletion) | review |
| Phenomenon | NT-PHENOMENON-3206 | Implementation Intentions | review |
| Phenomenon | NT-PHENOMENON-3207 | Overjustification Effect (Extrinsic Crowding-Out) | review |
| Phenomenon | NT-PHENOMENON-3208 | Pre-commitment | review |
| Principle | NT-PRINCIPLE-3201 | Commitment Devices | review |
| Principle | NT-PRINCIPLE-3202 | Goal Shielding | review |
| Principle | NT-PRINCIPLE-3203 | Environment Design for Habituation | review |
| Principle | NT-PRINCIPLE-3204 | Minimum Viable Routine (Tiny Habits) | review |
| Principle | NT-PRINCIPLE-3205 | Action Prompting (Contextual Triggers) | review |

## 5. Evidence Policy

*   Evidence posture is declared in `evidence-placeholders.yaml`; inline evidence fields remain provisional.
*   External references are not fabricated; future Evidence Layer batches will link standalone evidence records.

## 6. Ethical Safeguards

1.  Behavioral statements preserve context, uncertainty, and exception handling.
2.  Knowledge must not be used to coerce, manipulate, or stereotype individuals.
3.  No claim of universal certainty about human behavior.

## 7. Blueprint Acceptance Criteria

This blueprint is accepted when:
1.  The domain registry contains the domain id and slug.
2.  All blueprint files (`status.yaml`, `CONCEPT-MAP.md`, `ARCHITECTURE.md`, `DEPENDENCIES.md`, `GLOSSARY.md`) exist.
3.  All member units pass schema validation and `validate_all.py`.
