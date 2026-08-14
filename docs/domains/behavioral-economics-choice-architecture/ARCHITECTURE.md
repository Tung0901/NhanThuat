# Behavioral Economics & Choice Architecture Domain Architecture

**Domain Area:** NT-DA-0027  
**Slug:** behavioral-economics-choice-architecture  
**Category:** CAT-BEHAVIORAL  
**Status:** review

## 1. Domain Purpose

How do systematic deviations from rational choice shape decisions, and how can environments be designed to compensate?

## 2. Core Questions

*   Reference Dependence: Outcomes are evaluated not on their absolute value, but as positive or negative deviations (gains or losses) from a subjective reference point.
*   Loss Aversion: The psychological impact of losing something is roughly twice as powerful as the impact of gaining the equivalent thing.
*   Endowment Effect: Individuals ascribe higher value to items merely because they own them.
*   Framing Effect: Drawing different conclusions from the same exact information depending on how it is presented.
*   Present Bias (Hyperbolic Discounting): The tendency to disproportionately prefer smaller, immediate rewards over larger, later rewards.
*   Status Quo Bias: An emotional preference for the current state of affairs, taking any change from the baseline as a loss.
*   Mental Accounting: The tendency to categorize and treat money differently depending on its origin or intended use, rather than treating it as fully fungible.
*   Sunk Cost Fallacy: Continuing an endeavor as a result of previously invested resources (time, money, or effort), despite evidence that it is no longer profitable.
*   Decoy Effect (Asymmetric Dominance): Preferences between two options change significantly when a third, clearly inferior option (the decoy) is introduced.
*   Peak-End Rule: People judge an experience largely based on how they felt at its peak (most intense point) and at its end, rather than based on the total sum or average of every moment.
*   Base Rate Neglect: The tendency to ignore general statistical information (base rates) in favor of specific, often irrelevant, individuating information.
*   Choice Architecture Design: Actively structure the environment in which decisions are made to guide behavior toward optimal outcomes without restricting freedom of choice.
*   Default Configuration Leverage: Set the default option to the most socially or systemically optimal choice, as a majority of users will never change it.
*   Friction Addition for High-Risk Decisions: Intentionally introduce cognitive or physical friction to slow down automatic processing (System 1) before irreversible or high-risk actions.
*   Prospect Theory Framework: A formal descriptive model of decision-making under risk, demonstrating that humans value gains and losses differently, evaluating outcomes relative to a reference point rather than final wealth states.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `tri-nhan`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Model | NT-MODEL-3101 | Prospect Theory Framework | review |
| Phenomenon | NT-PHENOMENON-3101 | Reference Dependence | review |
| Phenomenon | NT-PHENOMENON-3102 | Loss Aversion | review |
| Phenomenon | NT-PHENOMENON-3103 | Endowment Effect | review |
| Phenomenon | NT-PHENOMENON-3104 | Framing Effect | review |
| Phenomenon | NT-PHENOMENON-3105 | Present Bias (Hyperbolic Discounting) | review |
| Phenomenon | NT-PHENOMENON-3106 | Status Quo Bias | review |
| Phenomenon | NT-PHENOMENON-3107 | Mental Accounting | review |
| Phenomenon | NT-PHENOMENON-3108 | Sunk Cost Fallacy | review |
| Phenomenon | NT-PHENOMENON-3109 | Decoy Effect (Asymmetric Dominance) | review |
| Phenomenon | NT-PHENOMENON-3110 | Peak-End Rule | review |
| Phenomenon | NT-PHENOMENON-3111 | Base Rate Neglect | review |
| Principle | NT-PRINCIPLE-3101 | Choice Architecture Design | review |
| Principle | NT-PRINCIPLE-3102 | Default Configuration Leverage | review |
| Principle | NT-PRINCIPLE-3103 | Friction Addition for High-Risk Decisions | review |

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
