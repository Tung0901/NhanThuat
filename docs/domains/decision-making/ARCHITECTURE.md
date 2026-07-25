# Decision Making Domain Architecture

**Domain Area:** NT-DA-0015  
**Slug:** decision-making  
**Status:** ready_for_review  
**Wave:** Milestone 2 Wave 4  
**Review Owner:** Chief Architect or delegated Decision Making domain reviewer  

## 1. Domain Purpose

The Decision Making domain defines the structured process of evaluating alternatives under uncertainty and selecting a course of action. It focuses on how humans gather evidence, assess risk and uncertainty, counteract cognitive biases, and commit to choices that have opportunity costs. Decision Making separates the quality of the process from the quality of the outcome.

## 2. Core Questions

*   What is a decision?
*   How do humans make decisions under conditions of limited information and load?
*   What separates good decisions from good outcomes?
*   How should uncertainty be handled and priced?
*   What cognitive failures (anti-patterns) systematically distort decisions?
*   How should decisions be reviewed after execution to improve the process?

## 3. Boundary Rules with Adjacent Domains

| Adjacent Domain | In-scope for Decision Making | Out-of-scope (Steward Domain) |
| --- | --- | --- |
| **Leadership (`NT-DA-0004`)** | Establishing decision criteria and who participates in the decision process. | Direction setting, vision, and building trust. |
| **Authority (`NT-DA-0008`)** | Knowing who holds the right to finalize the choice. | Legitimate power structures and compliance. |
| **Delegation (`NT-DA-0007`)** | The mechanics of handing down decision-making rights. | Assigning specific tasks and accountability tracking. |
| **Execution (`NT-DA-0017`)** | The commitment to action resulting from the decision. | The actual mobilization of effort and progress tracking. |
| **Human Nature (`NT-DA-0001`)** | Cognitive biases affecting the evaluation of evidence. | Broad behavioral responses to threat and safety. |

**Decision Making is NOT:** Leadership, Management, Problem Solving, Planning, Execution, Communication, Persuasion, Voting, Authority, Delegation.

## 4. Required Architectural Questions Answered

### 1. What is a Decision within NhanThuat ontology?
A decision is an irrevocable allocation of resources (time, money, effort) toward a selected alternative, made under uncertainty. A choice without commitment is merely an opinion or preference.

### 2. What belongs to Decision Making versus Problem Solving?
Problem Solving involves identifying root causes and designing potential solutions. Decision Making is the act of selecting among those potential solutions, accepting the tradeoffs, and committing to action.

### 3. What are its upstream dependencies?
*   `NT-DA-0001` (Human Nature) for cognitive load and bias.
*   `NT-DA-0008` (Authority) for decision rights.
*   `NT-DA-0013` (Communication) for information transmission leading to evidence.

### 4. What downstream domains consume it?
*   `NT-DA-0016` (Strategy) for making high-level positioning choices.
*   `NT-DA-0017` (Execution) for operationalizing the choice.
*   `NT-DA-0012` (Negotiation) for evaluating tradeoffs with other parties.

### 5. Which claims are diagnostic, explanatory, normative, or predictive?
*   **Diagnostic:** Anti-patterns identifying flawed evaluation (Outcome Bias, Analysis Paralysis).
*   **Explanatory:** Models showing the relationship between risk, uncertainty, and evidence.
*   **Normative:** Principles on separating decision quality from outcome.
*   **Predictive:** Laws about the permanence of opportunity cost.

## 5. Candidate Knowledge Inventory (Freeze Candidates)

### Proposed Laws
*   **NT-LAW-0048:** Decision Quality Independence
*   **NT-LAW-0049:** Irreducible Uncertainty
*   **NT-LAW-0050:** Opportunity Cost Permanence

### Proposed Principles
*   **NT-PRINCIPLE-0078:** Evaluate Decisions by Process Not Outcome
*   **NT-PRINCIPLE-0079:** Bound and Price Uncertainty
*   **NT-PRINCIPLE-0080:** Make Opportunity Costs Explicit

### Proposed Models
*   **NT-MODEL-0015:** Decision Quality Model
*   **NT-MODEL-0016:** Evidence-Risk Matrix
*   **NT-MODEL-0017:** Uncertainty Evaluation Model

### Proposed Anti-patterns
*   **NT-ANTI-PATTERN-0023:** Outcome Bias
*   **NT-ANTI-PATTERN-0024:** Analysis Paralysis
*   **NT-ANTI-PATTERN-0025:** Authority Bias
*   **NT-ANTI-PATTERN-0026:** False Certainty
*   **NT-ANTI-PATTERN-0027:** Decision by Popularity

## 6. Blueprint Acceptance Criteria
This blueprint is accepted when the domain registry, concepts, laws, principles, models, and anti-patterns validate successfully, and the Chief Architect reviews the package.
