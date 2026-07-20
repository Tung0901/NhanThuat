# Knowledge Factory Architecture

**Task:** TASK-011  
**Status:** frozen  
**Date:** 2026-07-20  
**Scope:** Production pipeline design only

## 1. Objective

The Knowledge Factory defines how Nhan Thuat should create, review, validate,
improve, and freeze knowledge at production scale while preserving the
repository as source of truth.

This document does not implement runtime code, modify schemas, freeze content,
commit, or push.

## 2. Current Foundation

The project currently has:

- Frozen governance and source-of-truth rules from EPIC 0 and EPIC 1.
- Frozen knowledge architecture from EPIC 2.
- Frozen law/principle seed content from EPIC 3.
- Knowledge Foundation Batch 1 in `ready_for_review` state.
- A proposed Evidence Layer architecture with first-class evidence, citations,
  confidence, and traceability.

The current registry and validation pipeline already enforce schema shape, ID
uniqueness, relation target existence, naming conventions, known relation types,
tag naming, and frozen-register integrity. The Knowledge Factory should extend
this operating pattern before adding large amounts of content.

## 3. Knowledge Authoring Workflow

Authoring should move through explicit stages:

1. **Intake:** capture proposed concept, source prompt, intended unit type,
   domain, and reason for inclusion.
2. **Triage:** decide whether the concept is new, duplicate, derivative,
   evidence-only, or out of scope.
3. **Draft:** create a structured knowledge unit with stable ID, type, title,
   summary, domain, conditions, exceptions, applications, risks, evidence
   summary, relations, tags, and dates.
4. **Linking:** add relationships to existing units and evidence records when
   available.
5. **Author self-check:** verify human readability, AI readability, scope
   boundaries, neutrality, and no placeholder text.
6. **Validation:** run repository validation and relevant tests.
7. **Internal review:** inspect meaning, overlap, conflicts, relation quality,
   and lifecycle state.
8. **Ready for review:** prepare Product Owner review package.
9. **Product Owner approval:** only the Product Owner may approve.
10. **Freeze:** after approval, update status/frozen register/changelog and
    commit through the defined freeze workflow.

Authoring should be batch-oriented for scale, but every unit must remain
reviewable independently.

## 4. Quality Gates

Each batch should pass these gates:

- **Scope gate:** content matches the approved batch or Epic scope.
- **Type gate:** each record is classified as law, principle, model, strategy,
  tool, case, evidence, or anti-pattern according to its editorial meaning.
- **Taxonomy gate:** primary and secondary domains are valid and not duplicated.
- **Evidence gate:** evidence level and references are explicit; unresolved
  evidence remains marked as provisional.
- **Relation gate:** relations point to existing records and use correct
  direction.
- **Duplicate gate:** no materially duplicate concept, title, ID, or slug exists.
- **Conflict gate:** known conflicts are represented rather than silently
  ignored.
- **Human readability gate:** unit can be understood without private
  conversation context.
- **AI readability gate:** unit has concise summary, explicit conditions,
  exceptions, risks, tags, and stable IDs.
- **Validation gate:** managed documents validate successfully.
- **Test gate:** content, registry, catalog, and negative cases are covered.
- **Governance gate:** no Frozen content is changed without approved change
  control.

## 5. Validation Pipeline

The future factory validation pipeline should be layered:

1. **Syntax validation:** YAML/JSON parse successfully.
2. **Schema validation:** records match approved schemas.
3. **Identifier validation:** IDs are unique, stable, type-aligned, and present
   in filenames.
4. **Taxonomy validation:** domains and tags conform to controlled rules.
5. **Relation validation:** relation types are known and targets exist.
6. **Evidence validation:** evidence references resolve when first-class
   evidence is implemented.
7. **Duplicate validation:** candidate units are compared against existing units.
8. **Conflict validation:** conceptual tensions are detected and either linked
   or documented.
9. **Lifecycle validation:** status transitions follow governance.
10. **Frozen validation:** Frozen content and register remain consistent.
11. **Catalog validation:** generated projections are deterministic when
    generated outputs exist.

Validation should distinguish hard failures from review warnings. Broken IDs,
invalid schema, and improper Frozen edits should fail. Potential duplicates,
weak evidence, or possible conflicts may begin as warnings requiring reviewer
disposition.

## 6. Duplicate Detection Strategy

Duplicate detection should combine deterministic and semantic checks.

Deterministic checks:

- duplicate ID;
- duplicate filename ID;
- duplicate normalized title;
- duplicate slug;
- duplicate summary fingerprint;
- same type plus same primary domain plus near-identical tags.

Semantic checks:

- same mechanism under different wording;
- same principle expressed as a law or vice versa;
- narrower unit that should be an application or exception of an existing unit;
- broader unit that should replace several draft units;
- duplicate relationship pattern.

Reviewer dispositions:

- `new`: concept is distinct;
- `merge`: combine into existing draft;
- `split`: concept contains multiple units;
- `supersede`: future lifecycle relation required;
- `reject`: out of scope or duplicate.

AI may propose duplicate candidates, but a human reviewer must decide final
disposition before review-ready status.

## 7. Conflict Detection Strategy

Conflict detection should preserve nuance rather than force artificial
consistency. Human behavior knowledge often contains conditional tensions.

Conflict categories:

- direct contradiction;
- boundary conflict;
- exception relationship;
- context-specific reversal;
- priority tradeoff;
- evidence contestation;
- terminology ambiguity.

Factory workflow should require one of these outcomes for detected conflicts:

- add `conflicts_with` relation;
- add exception or condition;
- clarify scope;
- rename or split the unit;
- defer with reviewer note;
- reject one candidate.

Conflicts are not automatically defects. Unacknowledged conflicts are defects.

## 8. Review Workflow

Review should have three layers:

1. **Author review:** verifies completeness, readability, taxonomy, relations,
   and no placeholders.
2. **Architecture review:** checks schema fit, ontology fit, lifecycle impact,
   duplication, conflict handling, evidence posture, and future compatibility.
3. **Product Owner review:** approves or rejects readiness for Frozen state.

Review packages should include:

- created/updated files;
- unit counts by type and status;
- validation/test/lint outputs;
- duplicate and conflict review notes;
- evidence posture summary;
- known limitations and deferred scope;
- explicit statement that approval/freeze remains Product Owner authority.

## 9. Freeze Workflow

Freeze should be a separate task after Product Owner approval.

Freeze steps:

1. Confirm Product Owner approval.
2. Re-read Constitution, governance, relevant ADRs, and target status.
3. Change only approved lifecycle/status files and required governance tracking.
4. Update frozen register.
5. Update changelog and roadmap when project convention requires it.
6. Ensure accepted ADR status for durable decisions being frozen.
7. Run validation, pytest, and ruff.
8. Commit with the requested message.
9. Push only when explicitly requested.

No implementation or content expansion should occur during freeze.

## 10. Knowledge Lifecycle

Factory content should use these lifecycle meanings:

- `idea`: captured but not structured.
- `draft`: authored but not validated.
- `review`: structured content awaiting internal review.
- `ready_for_review`: batch or Epic has passed internal gates.
- `approved`: Product Owner approved but not yet Frozen.
- `frozen`: official content protected by change control.
- `deprecated`: retained for traceability but no longer recommended.

Existing schemas may not yet support every operational batch state for every
record type. Future implementation should keep schema evolution backward
compatible and avoid forcing direct edits to Frozen content.

## 11. Human And AI Collaboration Workflow

AI may assist with:

- drafting candidate units;
- proposing taxonomy classifications;
- proposing relations;
- flagging potential duplicates;
- flagging potential conflicts;
- checking readability;
- preparing review packages;
- generating tests and validation plans.

Humans must retain authority over:

- Product Owner approval;
- Frozen decisions;
- durable governance decisions;
- conflict disposition;
- evidence confidence interpretation;
- acceptance of new taxonomy or ontology changes;
- final editorial meaning.

The AI workflow should preserve provenance:

- do not claim a source supports a unit unless an evidence record or citation
  supports that claim;
- label AI-generated drafts as drafts until reviewed;
- do not silently rewrite Frozen content;
- do not treat validation success as approval.

## 12. Batch Operating Model

Production-scale batches should be limited by review capacity, not generation
capacity. A recommended batch includes:

- a status file under `knowledge/foundation/<batch-id>/`;
- an architecture or batch rationale document;
- explicit unit counts by type;
- duplicate/conflict review notes;
- validation/test evidence;
- known limitations;
- next-state instruction.

Batch 1 demonstrates the initial shape with laws and principles. Later batches
should add evidence, models, strategies, tools, cases, or anti-patterns only
when those scopes are explicitly approved.

## 13. Backward Compatibility

The factory must preserve:

- existing IDs;
- existing Frozen status files;
- `build_registry()` legacy behavior;
- current inline evidence summaries;
- current relation vocabulary unless an ADR approves expansion;
- repository source-of-truth authority.

Future duplicate/conflict tooling should start as warnings where semantic
judgment is required, then become hard failures only after the Product Owner
approves the rule.

## 14. ADRs Accepted

TASK-011 introduced these ADRs, accepted during the Milestone 1 freeze:

- ADR-0012: Knowledge Factory workflow and quality gates.
- ADR-0013: Human and AI collaboration boundaries.

Both are accepted durable architecture decisions for the Milestone 1 Knowledge
Factory foundation.

## 15. Risks And Open Questions

Risks:

- Factory throughput may exceed human review capacity.
- Semantic duplicate detection can produce false positives.
- Conflict detection can over-flatten useful contextual tensions.
- AI-generated drafts may sound authoritative before evidence improves.
- Batch size may obscure unit-level quality problems.

Open questions:

- What is the maximum reviewable batch size per Product Owner cycle?
- Should duplicate/conflict warnings block `ready_for_review` or only require
  explicit reviewer disposition?
- Should there be a formal review-notes schema?
- Should author, reviewer, and AI-assistance metadata become required fields in
  future schemas?
