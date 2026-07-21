# Milestone 2 Domain Blueprint

**Task:** TASK-013  
**Milestone proposal:** NT-MILESTONE-02 — Domain Blueprint  
**Status:** approved  
**Date:** 2026-07-20  
**Scope:** Blueprint only; no domain content or knowledge units implemented

## 1. Objective

This document designs the production blueprint for domain-based knowledge
expansion. It defines the catalogue, hierarchy, dependencies, concept-map
structure, completeness criteria, batch strategy, review strategy, and freeze
strategy required before large-scale domain content is authored.

TASK-014 aligns the roadmap so this blueprint initializes Milestone 2:
Knowledge Expansion & Domain System. Intelligence Engine work moves to
Milestone 3.

This blueprint does not create or modify `knowledge/domains/` records, schemas,
runtime code, evidence records, or knowledge units. It prepares the expansion
plan that future approved batches can execute through the Frozen Knowledge
Factory.

## 2. Current Taxonomy Baseline

The Frozen Milestone 1 architecture keeps five top-level domains:

- `tu-than`: self-governance before governing others.
- `tri-nhan`: understanding people through needs, context, and behavior.
- `dung-nhan`: placing and enabling people in roles.
- `hop-chung`: turning individuals into coordinated groups.
- `thanh-su`: using people and organizations to produce intended outcomes.

Milestone 2 should preserve these five top-level domains. Production catalogue
entries should be treated as domain areas, subdomains, or concept clusters under
the current taxonomy unless a future Product Owner-approved ADR changes the
top-level taxonomy.

## 3. Master Domain Catalogue

The production catalogue begins with these domain areas:

| Domain area | Primary top-level domain | Secondary top-level domains | Purpose |
| --- | --- | --- | --- |
| Human Nature | `tri-nhan` | `tu-than`, `hop-chung` | Recurring human tendencies, needs, limits, biases, and social behavior. |
| Motivation | `tu-than` | `tri-nhan`, `dung-nhan` | Drivers of effort, meaning, reward, fear, identity, and persistence. |
| Personality | `tri-nhan` | `dung-nhan`, `tu-than` | Stable differences in temperament, preference, behavior, and fit. |
| Leadership | `dung-nhan` | `hop-chung`, `thanh-su` | Direction, responsibility, standards, legitimacy, and enabling others. |
| Hiring | `dung-nhan` | `tri-nhan`, `thanh-su` | Selection, assessment, fit, risk, and onboarding decisions. |
| Team Building | `hop-chung` | `dung-nhan`, `thanh-su` | Formation, cohesion, norms, coordination, and collective capability. |
| Delegation | `dung-nhan` | `thanh-su`, `hop-chung` | Assignment of work with authority, capability, support, and accountability. |
| Authority | `hop-chung` | `dung-nhan`, `thanh-su` | Legitimate power, decision rights, compliance, trust, and responsibility. |
| Incentives | `thanh-su` | `tri-nhan`, `dung-nhan` | Rewards, penalties, measures, tradeoffs, and behavior-shaping structures. |
| Trust | `hop-chung` | `dung-nhan`, `tri-nhan` | Reliability, vulnerability, repair, transparency, and coordination cost. |
| Conflict | `hop-chung` | `tri-nhan`, `thanh-su` | Tension, contradiction, interests, boundaries, and repair. |
| Negotiation | `thanh-su` | `hop-chung`, `tri-nhan` | Exchange, interests, leverage, options, concessions, and durable agreement. |
| Communication | `hop-chung` | `tri-nhan`, `dung-nhan` | Meaning transfer, listening, framing, feedback, escalation, and clarity. |
| Influence | `tri-nhan` | `hop-chung`, `thanh-su` | Attention, persuasion, social proof, framing, credibility, and behavior change. |
| Decision Making | `thanh-su` | `tri-nhan`, `tu-than` | Judgment, uncertainty, tradeoffs, authority, timing, and commitment. |
| Strategy | `thanh-su` | `hop-chung`, `dung-nhan` | Choice, positioning, priorities, constraints, leverage, and sequencing. |
| Execution | `thanh-su` | `dung-nhan`, `hop-chung` | Turning intent into outcomes through systems, cadence, accountability, and learning. |
| Learning | `tu-than` | `tri-nhan`, `thanh-su` | Correction, adaptation, reflection, feedback, transfer, and improvement. |
| Culture | `hop-chung` | `dung-nhan`, `thanh-su` | Shared norms, defaults, identity, incentives, rituals, and tolerated behavior. |
| Ethics | `tu-than` | `hop-chung`, `thanh-su` | Moral constraints, dignity, fairness, responsibility, and legitimate use of people. |

Additional domain areas may be proposed later, but each must include a rationale,
taxonomy placement, dependency impact, evidence plan, and review owner.

Stable catalogue IDs should be numeric and semantics-neutral. Slugs carry the
human-readable meaning:

| ID | Slug | Name |
| --- | --- | --- |
| NT-DA-0001 | `human-nature` | Human Nature |
| NT-DA-0002 | `motivation` | Motivation |
| NT-DA-0003 | `personality` | Personality |
| NT-DA-0004 | `leadership` | Leadership |
| NT-DA-0005 | `hiring` | Hiring |
| NT-DA-0006 | `team-building` | Team Building |
| NT-DA-0007 | `delegation` | Delegation |
| NT-DA-0008 | `authority` | Authority |
| NT-DA-0009 | `incentives` | Incentives |
| NT-DA-0010 | `trust` | Trust |
| NT-DA-0011 | `conflict` | Conflict |
| NT-DA-0012 | `negotiation` | Negotiation |
| NT-DA-0013 | `communication` | Communication |
| NT-DA-0014 | `influence` | Influence |
| NT-DA-0015 | `decision-making` | Decision Making |
| NT-DA-0016 | `strategy` | Strategy |
| NT-DA-0017 | `execution` | Execution |
| NT-DA-0018 | `learning` | Learning |
| NT-DA-0019 | `culture` | Culture |
| NT-DA-0020 | `ethics` | Ethics |

## 4. Domain Hierarchy

The recommended hierarchy is three layers:

1. **Top-level domain:** one of the five existing taxonomy domains.
2. **Domain area:** one production catalogue entry such as Trust, Delegation, or
   Decision Making.
3. **Concept cluster:** a focused map of laws, principles, models, strategies,
   tools, cases, anti-patterns, and evidence needs.

Example:

```text
hop-chung
  trust
    reliability
    transparency
    vulnerability
    repair
    coordination-cost
  conflict
    interests
    escalation
    role-boundaries
    tradeoffs
    repair
  culture
    norms
    rituals
    defaults
    identity
    tolerated-behavior
```

Domain areas should not become top-level taxonomy entries automatically. Primary
top-level domain means stewardship for review and organization, not exclusive
conceptual ownership. Tags remain cross-cutting retrieval facets rather than
hierarchy levels. New top-level domains require Product Owner review and a
separate ADR because they would alter validation, navigation, catalog
projection, and future retrieval.

## 5. Domain Dependency Graph

Domain dependencies describe learning and authoring order, not hard runtime
dependencies. A dependency means one domain area relies on concepts that should
be stabilized first.

Recommended dependency graph:

```text
Human Nature
  -> Motivation
  -> Personality
  -> Communication
  -> Influence

Motivation
  -> Incentives
  -> Leadership
  -> Learning

Personality
  -> Hiring
  -> Delegation
  -> Team Building

Communication
  -> Trust
  -> Conflict
  -> Negotiation
  -> Leadership

Trust
  -> Delegation
  -> Team Building
  -> Culture

Authority
  -> Delegation
  -> Leadership
  -> Decision Making

Decision Making
  -> Strategy
  -> Execution
  -> Negotiation

Strategy
  -> Execution

Ethics
  -> Authority
  -> Incentives
  -> Leadership
  -> Culture
```

The first production expansion waves should stabilize Human Nature, Motivation,
Communication, Trust, Authority, Decision Making, Ethics, and Execution because
they serve as anchors for many downstream areas.

Normalized dependency edges should be stored by ID when implemented. Direction
means "source should be reviewed before target." Edge kinds should be separated
from knowledge-unit `depends_on` relations:

| Source | Target | Edge kind | Rationale |
| --- | --- | --- | --- |
| NT-DA-0001 | NT-DA-0002 | authoring_prerequisite | Motivation relies on assumptions about human drives and limits. |
| NT-DA-0001 | NT-DA-0003 | authoring_prerequisite | Personality needs a baseline model of human variation. |
| NT-DA-0001 | NT-DA-0013 | authoring_prerequisite | Communication depends on attention, perception, and interpretation. |
| NT-DA-0002 | NT-DA-0009 | authoring_prerequisite | Incentive design depends on motivation mechanics. |
| NT-DA-0002 | NT-DA-0004 | authoring_prerequisite | Leadership depends on motivation and commitment. |
| NT-DA-0003 | NT-DA-0005 | authoring_prerequisite | Hiring requires understanding variation and fit. |
| NT-DA-0003 | NT-DA-0007 | authoring_prerequisite | Delegation depends on capability and fit. |
| NT-DA-0013 | NT-DA-0010 | authoring_prerequisite | Trust depends on reliable meaning transfer and candor. |
| NT-DA-0013 | NT-DA-0011 | authoring_prerequisite | Conflict work depends on communication channels and framing. |
| NT-DA-0010 | NT-DA-0006 | authoring_prerequisite | Team building depends on trust and coordination cost. |
| NT-DA-0008 | NT-DA-0007 | authoring_prerequisite | Delegation requires decision rights and authority boundaries. |
| NT-DA-0008 | NT-DA-0015 | authoring_prerequisite | Decision making depends on authority and accountability. |
| NT-DA-0015 | NT-DA-0016 | authoring_prerequisite | Strategy depends on choice and tradeoff quality. |
| NT-DA-0016 | NT-DA-0017 | authoring_prerequisite | Execution operationalizes strategic choices. |
| NT-DA-0020 | NT-DA-0008 | authoring_prerequisite | Authority must be bounded by legitimate use. |
| NT-DA-0020 | NT-DA-0009 | authoring_prerequisite | Incentives need ethical constraints. |

Conceptual influence may be cyclic, but authoring-prerequisite edges should be
acyclic within a planned batch. Authors should record dependency inputs and
derive downstream outputs rather than hand-maintaining both directions.

## 6. Concept Map Structure

Each domain area should use the same concept-map template:

- `domain_area_id`: stable catalogue identifier, such as `NT-DA-0010`.
- `slug`: stable kebab-case human-readable slug, such as `trust`.
- `name`: human-readable name.
- `top_level_domain`: primary existing taxonomy slug.
- `secondary_domains`: existing taxonomy slugs.
- `scope`: what belongs in the area.
- `out_of_scope`: what should be handled elsewhere.
- `core_questions`: review questions the area should answer.
- `concept_clusters`: named subtopics.
- `expected_unit_mix`: planning guardrail by unit type, never a quota.
- `dependency_inputs`: upstream domain areas needed first.
- `dependency_outputs`: downstream areas likely to consume it.
- `evidence_needs`: sources or evidence categories required later.
- `duplicate_risks`: nearby domains where overlap is likely.
- `conflict_risks`: known tension areas.
- `completeness_criteria`: definition of enough coverage.
- `review_owner`: human role or Product Owner delegate for domain review; this
  role cannot approve or freeze unless it is the Product Owner acting in that
  authority.

This structure should initially live in architecture/planning documents, not in
canonical domain YAML, until the Product Owner approves a schema or content model
for domain-area records.

Structured concept clusters should include:

- cluster ID and slug;
- definition;
- in-scope concepts;
- out-of-scope concepts;
- core questions;
- existing-unit references;
- candidate gaps;
- evidence needs;
- coverage disposition.

## 7. Domain Completeness Criteria

A domain area should not be considered complete because it has many units.
Completeness requires balanced coverage:

- Core definitions are clear and non-overlapping.
- At least one concept cluster exists for each major subtopic.
- Laws describe recurring tendencies.
- Principles operationalize the laws.
- Models explain diagnosis or structure where needed.
- Strategies and tools are deferred until explicitly approved for that domain
  batch.
- Evidence needs are recorded, even when evidence remains provisional.
- Dependencies and downstream consumers are documented.
- Duplicate and conflict candidates are reviewed.
- Conditions, exceptions, risks, and applicability boundaries are visible.
- Human-readable and AI-readable meaning are both preserved.
- Validation, tests, and review package evidence pass.

Planning-only markers such as `architecture_draft` or `blueprinted` are document
labels, not current machine lifecycle states for canonical knowledge records.
Future implementation should either define them in schema or use existing
lifecycle states.

Four separate gates must not be collapsed:

- **Catalogue completeness:** every required domain area is mapped to an ID,
  slug, top-level steward, dependencies, and concept clusters.
- **Blueprint completeness:** scope, out-of-scope boundaries, evidence needs,
  review owners, and freeze semantics are documented.
- **Content coverage:** authored units cover the domain area's core questions,
  conditions, exceptions, and risks.
- **Freeze readiness:** validation, tests, review evidence, Product Owner
  approval, and frozen-register integrity pass.

Expected unit mix is only a planning guardrail. A domain area is complete when
its questions and risks are responsibly covered, not when a target count is hit.

## 7.1 Existing Coverage Crosswalk

Before future content authoring, every existing unit should be mapped to a
domain area and concept cluster or explicitly deferred.

Initial crosswalk:

| Existing scope | Domain area disposition | Notes |
| --- | --- | --- |
| `NT-LAW-0001`, `NT-LAW-0004`, `NT-LAW-0009`, `NT-LAW-0014`, `NT-LAW-0017`, `NT-LAW-0018`, `NT-LAW-0020`, `NT-LAW-0021` | Human Nature, Influence, Authority, Decision Making | Covers motivation, context, status, identity, proximity, roles, uncertainty, and participation. |
| `NT-LAW-0002`, `NT-LAW-0013`, `NT-PRINCIPLE-0021`, `NT-PRINCIPLE-0022` | Influence, Decision Making, Execution | Covers attention, perceived significance, measurement, and metric side effects. |
| `NT-LAW-0003`, `NT-LAW-0011`, `NT-PRINCIPLE-0017`, `NT-PRINCIPLE-0018`, `NT-PRINCIPLE-0043` | Trust | Covers trust, consistency, repair, candor, and coordination cost. |
| `NT-LAW-0005`, `NT-PRINCIPLE-0006`, `NT-PRINCIPLE-0007` | Motivation, Incentives | Covers incentive audit and value/measure alignment. |
| `NT-LAW-0006`, `NT-PRINCIPLE-0008`, `NT-PRINCIPLE-0009` | Communication, Execution | Covers clarity, ownership, standards, and recurring confusion. |
| `NT-LAW-0007`, `NT-LAW-0010`, `NT-PRINCIPLE-0002`, `NT-PRINCIPLE-0010`, `NT-PRINCIPLE-0015`, `NT-PRINCIPLE-0016` | Delegation, Authority, Leadership | Covers capability, decision rights, responsibility, agency, and escalation. |
| `NT-LAW-0008`, `NT-LAW-0023`, `NT-PRINCIPLE-0011`, `NT-PRINCIPLE-0012`, `NT-PRINCIPLE-0041`, `NT-PRINCIPLE-0042` | Learning, Communication, Leadership | Covers feedback, correction, blame separation, and learning safety. |
| `NT-LAW-0012`, `NT-PRINCIPLE-0019`, `NT-PRINCIPLE-0020` | Conflict, Decision Making | Covers tradeoffs and conflict resolution level. |
| `NT-LAW-0015`, `NT-LAW-0016`, `NT-LAW-0019`, `NT-LAW-0022`, `NT-PRINCIPLE-0025` through `NT-PRINCIPLE-0040` | Execution, Learning, Culture, Strategy | Covers energy, habits, defaults, bottlenecks, overload, uncertainty, participation, and systems. |
| `NT-PRINCIPLE-0001`, `NT-PRINCIPLE-0004`, `NT-PRINCIPLE-0005`, `NT-PRINCIPLE-0013`, `NT-PRINCIPLE-0014`, `NT-PRINCIPLE-0023`, `NT-PRINCIPLE-0024` | Human Nature, Communication, Conflict, Ethics | Covers interests, context, bad-news channels, silence, face, and separating person from position. |
| Hiring, Team Building, Negotiation, Personality, Sales-adjacent topics | Deferred / gap | Current units touch prerequisites but do not yet provide sufficient direct coverage. |
| Emotion and self-regulation, capability development, feedback/performance, goals/resources/measurement/change, alliances/consensus | Deferred / explicit future cluster work | Present in current domain topics but not yet fully mapped to production clusters. |

## 8. Batch Planning Strategy

Batch planning should follow dependency order and review capacity.

Recommended waves, with internal order:

1. **Foundational human behavior:** Human Nature -> Motivation -> Personality ->
   Learning -> Ethics.
2. **Coordination foundations:** Communication -> Trust -> Conflict ->
   Influence -> Authority.
3. **People systems:** Hiring -> Delegation -> Team Building -> Leadership ->
   Culture.
4. **Action systems:** Decision Making -> Strategy -> Execution -> Incentives ->
   Negotiation.

Waves are roadmap-scale groupings. Batches are review-capacity-sized units of
work inside a wave. A wave may require several batches, and dependency edges
inside a wave should be ordered topologically before authoring starts.

Each batch should declare:

- included domain areas;
- excluded adjacent areas;
- planned unit type mix;
- expected evidence posture;
- duplicate/conflict watchlist;
- reviewer capacity;
- freeze target;
- no-go criteria.

Batch size should be constrained by reviewability. If reviewers cannot inspect
each unit and relation, the batch is too large.

## 9. Review Strategy

Review should combine domain review and architecture review:

- Domain review checks meaning, completeness, overlap, practical usefulness,
  and BusinessOS-neutral applicability.
- Architecture review checks taxonomy fit, ontology relations, evidence posture,
  validation, backward compatibility, and Frozen-content protection.
- Product Owner review decides approval and freeze.

Review owners may conduct domain review and recommend disposition, but only the
Product Owner may approve or freeze.

Each domain-area review should produce:

- unit count by type and lifecycle;
- coverage map against concept clusters;
- duplicate candidate list;
- conflict candidate list;
- evidence posture summary;
- accepted fixes and rejected findings;
- freeze eligibility recommendation.

No domain area should be frozen unless unresolved blockers are zero.

## 10. Freeze Strategy

Freeze should remain a separate Product Owner-approved task.

Freeze package requirements:

- approved domain-area blueprint or batch scope;
- machine-readable batch manifest;
- human-readable review report;
- validation, pytest, and ruff outputs;
- updated frozen register when content becomes Frozen;
- changelog and roadmap updates where relevant;
- accepted ADRs for durable taxonomy or workflow decisions;
- no direct modification of Frozen content outside change control.

Domain blueprints may be frozen before domain content. Content batches should be
frozen separately after their own review.

Future implementation should define atomic freeze semantics for domain batches:

- whether freezing a batch freezes all member units;
- whether member units must also move to `frozen`;
- how aggregate batch status and member lifecycle status remain consistent;
- how the frozen register validates non-Epic entries such as batches,
  milestones, domain areas, and evidence sets;
- how change control applies to a frozen batch when only one member unit needs a
  correction.

This blueprint does not retroactively change Frozen Milestone 1 or Batch 1
semantics. It records the requirement so future domain expansion can make batch
and member freeze rules enforceable.

## 11. ADRs Required

TASK-013 introduces these proposed ADRs:

- ADR-0014: Domain catalogue, hierarchy, and dependency graph.
- ADR-0015: Domain expansion planning, completeness, review, and freeze gates.

Both are accepted by Product Owner approval in TASK-014.

## 12. Risks And Open Questions

Risks:

- Domain areas may overlap heavily if concept boundaries are vague.
- A hierarchy can become too rigid for cross-domain human behavior patterns.
- Dependency order may slow urgent high-value content areas.
- Completeness metrics may reward volume over quality.
- Domain planning may drift into premature content generation.
- Existing validator behavior does not yet enforce frozen-register integrity for
  non-Epic entries or atomic batch/member freeze semantics.

Open questions:

- Should domain-area records eventually become first-class YAML under a new
  canonical path?
- Should concept clusters be controlled vocabulary, generated catalog metadata,
  or reviewer notes?
- What batch size is reviewable for each domain wave?
- Which domain areas require external evidence before any content is frozen?
- Should Milestone 2 freeze the blueprint only, or the first domain expansion
  batch as well?
