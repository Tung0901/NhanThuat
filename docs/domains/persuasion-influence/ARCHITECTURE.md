# Persuasion & Influence Domain Architecture

**Domain Area:** NT-DA-0030  
**Slug:** persuasion-influence  
**Category:** CAT-BEHAVIORAL  
**Status:** review

## 1. Domain Purpose

How does influence actually move people, and where is the line between legitimate persuasion and manipulation?

## 2. Core Questions

*   Scarcity Principle: Opportunities seem more valuable to us when their availability is limited.
*   Authority Principle: A deep-seated sense of duty to authority causes individuals to blindly comply with requests from perceived experts or leaders.
*   Liking Principle: People prefer to say yes to individuals they know and like.
*   Commitment and Consistency: Once we make a choice or take a stand, we face personal and interpersonal pressures to behave consistently with that commitment.
*   Unity Principle: We are heavily influenced by people who share a fundamental identity with us—the 'We' connection.
*   Door-in-the-Face Technique: Making an extreme request that is guaranteed to be rejected, followed immediately by a smaller, reasonable request.
*   Foot-in-the-Door Technique: Getting a person to agree to a large request by first having them agree to a modest request.
*   Ben Franklin Effect: A person who has performed a favor for someone is more likely to do another favor for them than they would be if they had received a favor from that person.
*   Identifiable Victim Effect: People are far more willing to offer aid to a specific, identifiable individual in hardship than to a large, vaguely defined group with the same need.
*   Message Framing (Gain vs. Loss): The way a choice is presented (framed) as either a gain or a loss drastically alters the likelihood of persuasion, even if the objective outcomes are identical.
*   Paradox of Choice (Choice Overload): While some choice is better than none, an abundance of options leads to decision paralysis, anxiety, and lower post-decision satisfaction.
*   Perceptual Contrast: Always present the most expensive, extreme, or difficult option first to alter the anchor point, making subsequent options appear significantly smaller or cheaper.
*   Reason-Respecting Tendency ('Because' Heuristic): People are highly likely to comply with a request if a reason is provided, even if that reason is completely meaningless.
*   Elaboration Likelihood Model (ELM): A dual-process theory describing the change of attitudes, identifying two distinct routes to persuasion: central (logical) and peripheral (superficial).
*   Inoculation Theory: People can be immunized against persuasive attacks and misinformation by preemptively exposing them to a weakened version of the argument.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `tri-nhan`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Model | NT-MODEL-3401 | Elaboration Likelihood Model (ELM) | review |
| Model | NT-MODEL-3402 | Inoculation Theory | review |
| Phenomenon | NT-PHENOMENON-3401 | Scarcity Principle | review |
| Phenomenon | NT-PHENOMENON-3402 | Authority Principle | review |
| Phenomenon | NT-PHENOMENON-3403 | Liking Principle | review |
| Phenomenon | NT-PHENOMENON-3404 | Commitment and Consistency | review |
| Phenomenon | NT-PHENOMENON-3405 | Unity Principle | review |
| Phenomenon | NT-PHENOMENON-3406 | Door-in-the-Face Technique | review |
| Phenomenon | NT-PHENOMENON-3407 | Foot-in-the-Door Technique | review |
| Phenomenon | NT-PHENOMENON-3408 | Ben Franklin Effect | review |
| Phenomenon | NT-PHENOMENON-3409 | Identifiable Victim Effect | review |
| Phenomenon | NT-PHENOMENON-3410 | Message Framing (Gain vs. Loss) | review |
| Phenomenon | NT-PHENOMENON-3411 | Paradox of Choice (Choice Overload) | review |
| Principle | NT-PRINCIPLE-3401 | Perceptual Contrast | review |
| Principle | NT-PRINCIPLE-3402 | Reason-Respecting Tendency ('Because' Heuristic) | review |

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
