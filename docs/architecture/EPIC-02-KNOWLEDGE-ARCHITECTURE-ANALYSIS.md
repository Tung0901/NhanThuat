# EPIC 2 Knowledge Architecture Analysis

**Epic:** NT-EPIC-02 — Knowledge Architecture  
**Status:** architecture_review  
**Scope:** analysis and documentation only  
**Date:** 2026-07-20

## 1. EPIC Objective And Boundaries

EPIC 2 should define the durable knowledge architecture for Nhan Thuat: taxonomy,
ontology, knowledge-unit classification, ID conventions, registry/catalog
structure, evidence traceability, schema evolution rules, validation coverage,
and lifecycle implications for future knowledge expansion.

This analysis does not implement EPIC 2 runtime behavior, schema changes,
registry changes, migration, generated catalogs, or additional knowledge content.
It prepares the architecture basis for Product Owner review and later
implementation work.

EPIC 2 must preserve the EPIC 0 and EPIC 1 Frozen state. Any required change to
Frozen deliverables must go through formal change control rather than direct
modification.

## 2. Current-State Assessment

The repository currently has a clean separation between knowledge content,
schemas, and engine code:

- `knowledge/domains/` contains five draft domains.
- `knowledge/units/` contains one draft knowledge unit.
- `schemas/` defines domain, epic, evidence, knowledge-unit, and relation
  structures.
- `src/nhan_thuat/` provides loading, validation, and an in-memory registry
  foundation.
- `docs/adr/` records durable governance and architecture decisions.
- `governance/frozen-register.yaml` marks EPIC 0 and EPIC 1 as Frozen.

The current foundation is intentionally minimal. It validates basic schemas,
unique knowledge-unit IDs, and relation target existence among knowledge units.
It does not yet define a complete taxonomy tree, relation semantics, separate
evidence records, registry indexes, catalog outputs, lifecycle transition rules,
or search/retrieval contracts.

One known governance-schema mismatch is relevant: EPIC 2 is requested to use
`architecture_review`, but `schemas/epic.schema.json` currently permits only
`not_started`, `in_progress`, `ready_for_review`, `approved`, `frozen`, and
`blocked`. EPIC 2 should resolve this through a schema-evolution decision during
implementation, not by ad hoc status handling.

## 3. Taxonomy Design

The current five top-level domains form the first taxonomy layer:

- `tu-than`: self-governance before governing others.
- `tri-nhan`: understanding people through needs, context, and behavior.
- `dung-nhan`: placing and enabling people in roles.
- `hop-chung`: turning individuals into coordinated groups.
- `thanh-su`: using people and organizations to produce intended outcomes.

EPIC 2 should formalize a taxonomy model with:

- stable domain IDs and slugs;
- optional subdomains or topics under each domain;
- controlled tags for cross-cutting retrieval;
- clear ownership of domain/topic definitions;
- rules for when a concept becomes a domain, subdomain, topic, tag, or knowledge
  unit.

Recommended principle: domains should remain few and stable; subdomains and tags
should absorb normal growth. New top-level domains should require ADR-level
review because they reshape navigation, validation, and future retrieval.

## 4. Ontology And Relation Model

The current relation vocabulary is:

- `supports`
- `conflicts_with`
- `depends_on`
- `applies_to`

EPIC 2 should define relation semantics precisely enough for validation,
reviewers, and later search systems. At minimum, each relation type should
specify direction, expected target types, whether reciprocal edges are required,
and whether cycles are allowed.

Recommended ontology layers:

- domain membership: primary and secondary domain assignment;
- conceptual dependency: prerequisites and mechanisms;
- evidential relation: evidence supporting, contesting, or contextualizing a
  unit;
- application relation: where a unit is usable;
- conflict relation: conceptual contradiction, boundary conflict, or exception;
- lifecycle relation: supersedes, replaces, deprecated-by, or derived-from.

The current relation model is embedded inside each knowledge unit. EPIC 2 should
decide whether relations remain embedded, become standalone relation records, or
use a hybrid model. A hybrid is likely best: keep high-value direct relations in
knowledge units for readability, but allow a future relation registry for
cross-cutting graph analysis.

## 5. Knowledge Unit Classification

The current knowledge-unit types are:

- `law`
- `principle`
- `model`
- `strategy`
- `tool`
- `case`
- `evidence`
- `anti-pattern`

EPIC 2 should define the editorial meaning of each type:

- A law states a recurring pattern or tendency with conditions and exceptions.
- A principle states a normative or practical guidance rule.
- A model structures interpretation or diagnosis.
- A strategy describes a repeatable approach for pursuing outcomes.
- A tool is an operational method, checklist, or instrument.
- A case records a concrete example or application context.
- Evidence records a source-backed support item.
- An anti-pattern records a recurring harmful pattern and its warning signs.

Evidence may be better represented as a separate record family rather than as a
standard knowledge-unit type. EPIC 2 should decide whether `evidence` remains a
unit type, moves to `knowledge/evidence/`, or is supported by both patterns with
clear constraints.

## 6. ID And Naming Conventions

Current conventions include:

- domain IDs: `NT-D01` through `NT-D05`;
- knowledge-unit IDs: `NT-LAW-0001`, `NT-PRINCIPLE-0001`, and equivalent
  type-prefixed forms;
- evidence IDs: `NT-EVIDENCE-0001`;
- epic IDs: `NT-EPIC-00`.

EPIC 2 should define ID allocation rules that are stable, human-readable, and
not overloaded with mutable taxonomy meaning. Recommended rules:

- IDs are permanent after publication.
- Slugs may change only through lifecycle/version rules.
- Type prefixes should reflect record type at creation time.
- Renaming a title must not change the ID.
- Moving a unit between domains must not change the ID.
- Deprecated IDs must remain reserved.
- Sequential numbers should be unique within each prefix.

File names should use lowercase slugs where practical, but the ID remains the
canonical identifier.

## 7. Registry And Catalog Architecture

Current `build_registry()` loads knowledge units into an in-memory map keyed by
ID. EPIC 2 should define a broader registry architecture with:

- domain registry;
- knowledge-unit registry;
- relation index;
- evidence index;
- tag index;
- lifecycle/status index;
- generated read-only catalog outputs.

The repository should remain the source of truth. Generated catalogs under
`docs/generated/` or another explicit generated-output path should be
reproducible from repository content and never become canonical.

Registry functions should support deterministic ordering, duplicate detection,
broken-reference detection, and future query preparation without coupling the
content layer to one user interface or database.

## 8. Evidence And Citation Traceability

The Constitution requires statements about people to preserve context,
uncertainty, and exceptions. EPIC 2 should strengthen evidence traceability by
defining:

- evidence levels and their editorial meaning;
- reference identifiers and source metadata;
- citation fields for title, author/source, publication date when known, access
  date when needed, URL or repository path, and notes;
- support/contest/context relation types between evidence and knowledge units;
- rules for claims with no external citation yet;
- requirements for distinguishing inference from direct source support.

Evidence should be traceable from each knowledge unit to source records and from
each source record back to units it supports. Later AI systems should be able to
return citations without inventing provenance.

## 9. Schema Evolution And Backward Compatibility

EPIC 2 should define a schema-versioning policy before making schema changes.
Recommended policy:

- schemas use semantic versions;
- additive optional fields are minor changes;
- required-field additions, type changes, enum removals, ID-pattern changes, and
  relation semantic changes are breaking changes;
- breaking changes require ADR and migration notes;
- migrations should preserve IDs and lifecycle history;
- old Frozen content cannot be edited directly to satisfy a new schema unless a
  change-control process authorizes it.

The status value `architecture_review` should be handled through a formal schema
decision because it is currently outside the epic schema enum.

## 10. Validation Rules And Integrity Checks

Current validation covers schema shape, unique knowledge-unit IDs, and broken
relations among knowledge units. EPIC 2 should extend validation with:

- unique IDs across all managed records;
- known domain and subdomain references;
- known tag vocabulary where controlled tags are introduced;
- relation target existence and allowed target types;
- relation direction and reciprocal-edge requirements where applicable;
- duplicate title or slug warnings;
- evidence reference existence;
- status transition checks;
- Frozen direct-modification checks;
- generated catalog determinism checks;
- lifecycle supersession/deprecation integrity.

Validation should distinguish hard failures from warnings. For example, a broken
ID reference should fail; a missing optional citation date may warn depending on
evidence level.

## 11. Lifecycle And Frozen-Content Implications

EPIC 2 must align with the lifecycle:

`Backlog -> Draft -> Schema Valid -> Internal Review -> Test Passed -> Ready for Epic Review -> Approved -> Frozen`

Operational machine states may differ, but they must not bypass Product Owner
approval. Agents may prepare review evidence but must not mark EPIC 2 Approved
or Frozen.

Frozen content must be append-only unless Product Owner-approved change control
authorizes a direct change. If EPIC 2 introduces schema changes affecting EPIC 0
or EPIC 1 Frozen deliverables, the implementation plan must either:

- maintain backward compatibility for Frozen records; or
- open a formal change request with rationale, version update, impact note, and
  validation evidence.

## 12. Search And Future AI-Readiness Constraints

Future retrieval and AI use should be designed around repository-backed records.
EPIC 2 should prepare for:

- stable IDs in every answerable record;
- concise summaries for search snippets;
- explicit conditions, exceptions, and risks;
- citation-ready evidence references;
- deterministic catalog generation;
- graph traversal through typed relations;
- multilingual or transliteration needs without breaking IDs;
- distinction between canonical source content and generated AI outputs.

The architecture should avoid UI-specific fields in canonical content. Search
indexes, embeddings, and AI prompts should be generated artifacts or runtime
consumers of canonical records.

## 13. Risks, Assumptions, Dependencies, And Deferred Scope

Risks:

- overbuilding ontology before enough content exists;
- changing schemas in ways that invalidate Frozen content;
- treating evidence levels as certainty rather than editorial confidence;
- allowing tags to become uncontrolled duplicates;
- mixing generated catalogs with canonical content;
- expanding knowledge content during architecture work.

Assumptions:

- the five current domains remain the top-level taxonomy for EPIC 2;
- repository files remain canonical;
- Product Owner approval remains required for approval and Frozen transitions;
- EPIC 2 implementation will happen after this analysis is reviewed.

Dependencies:

- Product Owner decision on taxonomy depth;
- ADR decisions for ontology, schema versioning, evidence policy, and registry
  architecture;
- validation rules that can enforce the accepted model.

Deferred scope:

- runtime search;
- AI integration;
- database storage;
- web UI;
- large-scale knowledge expansion;
- migration of Frozen deliverables unless change control is approved.

## 14. Proposed Deliverables

Recommended EPIC 2 deliverables:

- taxonomy architecture specification;
- ontology and relation semantics specification;
- knowledge-unit classification guide;
- ID and naming convention guide;
- evidence and citation policy;
- registry/catalog architecture specification;
- schema-evolution and backward-compatibility policy;
- validation and integrity-check plan;
- required ADRs in proposed or accepted form;
- lightweight implementation plan for later EPIC 2 execution.

## 15. Acceptance Criteria

EPIC 2 should be ready for Product Owner review when:

- taxonomy rules are documented and consistent with the five current domains;
- relation semantics are documented with direction and allowed targets;
- knowledge-unit types have clear editorial definitions;
- ID allocation and naming rules are documented;
- registry/catalog boundaries preserve repository source-of-truth authority;
- evidence policy supports traceable citations and uncertainty handling;
- schema-evolution rules distinguish backward-compatible and breaking changes;
- validation requirements are listed and feasible;
- Frozen-content rules are explicitly preserved;
- required ADRs are created for durable decisions;
- no EPIC 2 runtime, schema, registry, migration, or knowledge expansion has been
  implemented before approval.

## 16. Recommended Implementation Sequence

Recommended sequence after Product Owner review:

1. Create proposed ADRs for taxonomy/ontology, evidence policy, schema
   versioning, and registry/catalog architecture.
2. Update or create architecture documents reflecting Product Owner decisions.
3. Evolve schemas only after ADR direction is accepted.
4. Add validation rules for new schema and relation integrity.
5. Add registry/catalog implementation for approved record types.
6. Add tests covering schema, lifecycle, evidence, and relation behavior.
7. Run repository validation and test suite.
8. Prepare EPIC 2 review package without marking Approved or Frozen.

## 17. Architecture Decisions That Require ADRs

EPIC 2 should create ADRs for at least these durable decisions:

- taxonomy depth and domain/subdomain/topic/tag boundaries;
- ontology relation vocabulary, directionality, and lifecycle relation policy;
- evidence record model and citation traceability requirements;
- schema versioning and backward-compatibility policy;
- registry/catalog architecture and generated-output boundaries;
- status lifecycle machine values, including whether `architecture_review`
  becomes an official status;
- Frozen-content compatibility strategy for future schema changes.
