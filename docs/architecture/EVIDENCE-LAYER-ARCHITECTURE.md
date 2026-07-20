# Evidence Layer Architecture

**Task:** TASK-010  
**Status:** frozen  
**Date:** 2026-07-20  
**Scope:** Architecture and ADR preparation only

## 1. Objective

The Evidence Layer makes evidence a first-class architecture component for Nhan
Thuat. It defines how sources, citations, confidence, and traceability should be
represented without turning evidence into the canonical knowledge itself.

This document does not implement the Evidence Layer, modify schemas, migrate
existing files, change runtime code, freeze content, commit, or push.

## 2. Current State

Current knowledge units store an inline evidence summary:

```yaml
evidence:
  level: provisional
  references: []
```

The current schema also contains a minimal standalone evidence schema with `id`,
`type`, `status`, `version`, `title`, and `source`, but the registry and
validation pipeline presently load only domains, knowledge units, Epic statuses,
and embedded unit relations. Knowledge Foundation Batch 1 intentionally uses
`provisional` evidence with empty references because no source corpus has been
introduced yet.

This means the project has an evidence placeholder, but not yet a complete
evidence architecture.

## 3. Architecture Boundaries

The Evidence Layer should be canonical repository content, but it must remain
separate from Canonical Knowledge:

- Canonical Knowledge states the reusable claim, law, principle, model,
  strategy, tool, case, or anti-pattern.
- Evidence records describe source-backed support, contestation, context, or
  limitation for those knowledge units.
- Citations point to source locations or bibliographic details.
- Confidence scores summarize the current evidence posture for review and
  retrieval; they do not replace human review.

The Evidence Layer must not introduce search, embeddings, LLM integration, UI,
CLI, ingestion pipelines, external databases, or generated answer behavior.

## 4. Evidence Data Model

The future first-class evidence record should use stable repository-backed YAML
records under a dedicated evidence source path such as `knowledge/evidence/`.

Recommended fields:

- `id`: stable identifier, for example `NT-EVIDENCE-0001`.
- `type`: `evidence`.
- `status`: lifecycle state using the existing project lifecycle vocabulary.
- `version`: semantic content version.
- `title`: short human-readable source or evidence title.
- `summary`: concise AI-readable description of what the evidence says.
- `source`: normalized source metadata object.
- `citations`: one or more citation targets.
- `claims`: claim-level summaries extracted from the source.
- `supports`: knowledge-unit IDs this evidence supports.
- `contests`: knowledge-unit IDs this evidence contests.
- `contextualizes`: knowledge-unit IDs this evidence bounds, explains, or
  limits without directly supporting or contesting.
- `confidence`: confidence scoring object.
- `limitations`: known limits, ambiguity, bias, missing context, or quality
  concerns.
- `review`: reviewer notes, review date, and review status.
- `created_at` and `updated_at`.

Evidence records should be content records, not generated cache artifacts.

## 5. Source Abstraction

Sources should be abstracted by source kind rather than by storage mechanism.
Recommended source kinds:

- `book`
- `article`
- `paper`
- `report`
- `web_page`
- `case_note`
- `interview`
- `dataset`
- `internal_document`
- `observation`
- `derived_analysis`

Every source should support a shared metadata envelope:

- `source_id` or external identifier when available.
- `title`.
- `authors` or responsible organization.
- `publisher` or host.
- `published_at` when known.
- `accessed_at` when relevant.
- `language`.
- `url` or repository path when available.
- `license` or usage note when known.
- `source_kind`.

The source abstraction should allow future ingestion adapters, but the canonical
record remains the repository YAML evidence record.

## 6. Citation Model

Citations should be claim-addressable, not only source-addressable. A citation
should identify the exact part of a source that supports an evidence claim when
possible.

Recommended citation fields:

- `citation_id`: stable citation identifier local to the evidence record or
  globally addressable if needed later.
- `source_locator`: URL, repository path, DOI, ISBN, archive link, or local
  source reference.
- `locator_type`: page, section, paragraph, timestamp, row, chapter, figure, or
  general.
- `locator`: concrete page number, section name, timestamp, row key, or other
  pointer.
- `quote`: optional short excerpt, subject to copyright limits.
- `paraphrase`: required when a direct quote is absent or inappropriate.
- `accessed_at`: required for mutable online sources.

Knowledge units should not need to repeat full citation metadata. They should
reference evidence IDs or claim IDs.

## 7. Confidence Scoring Model

Confidence must communicate editorial confidence, not universal certainty.
Recommended model:

- `level`: existing qualitative value such as `hypothesis`, `provisional`,
  `supported`, `strong`, or `contested`.
- `score`: optional numeric value from `0.0` to `1.0` for future ranking and
  review workflows.
- `basis`: short rationale explaining why the level or score was assigned.
- `factors`: structured factors such as source quality, directness, recency,
  consistency, reproducibility, and domain fit.
- `reviewed_by`: optional reviewer identifier or role.
- `reviewed_at`: review date.

The qualitative `level` remains the backward-compatible bridge for current
knowledge units. Numeric scores should be optional until migration is approved.

## 8. Traceability Architecture

Traceability should work in both directions:

- From a knowledge unit to all evidence that supports, contests, or
  contextualizes it.
- From an evidence record to every knowledge unit that relies on it.
- From a citation to the claim it supports.
- From a confidence level to the evidence factors behind it.

The future registry should load an Evidence Registry beside the Knowledge
Registry and expose a deterministic Evidence Catalog projection. Validation
should detect broken evidence references, duplicate evidence IDs, duplicate
citations inside a record, invalid source kinds, and evidence references to
unknown knowledge units.

## 9. Separation From Canonical Knowledge

Canonical Knowledge and Evidence must remain separate because they have different
lifecycles:

- A law or principle may remain stable while its supporting evidence improves.
- Evidence may be added, corrected, contested, or deprecated without changing the
  canonical claim ID.
- A knowledge unit may have multiple evidence records with different confidence
  implications.
- A source may support one claim, contest another, and contextualize a third.

Knowledge-unit `evidence.level` should be treated as a summary derived from or
manually aligned with first-class evidence records after migration, not as the
only source of evidence truth.

## 10. Backward Compatibility Strategy

The current inline evidence summary must remain valid:

```yaml
evidence:
  level: provisional
  references: []
```

Recommended compatibility path:

1. Keep inline evidence fields required for existing knowledge units.
2. Add first-class evidence records in a future schema version without requiring
   immediate edits to Frozen knowledge units.
3. Allow `evidence.references` to contain evidence IDs such as
   `NT-EVIDENCE-0001` once the evidence registry exists.
4. Treat empty references with `provisional` level as valid but reviewable.
5. Add validation warnings before hard failures when tightening evidence
   requirements.
6. Preserve all existing knowledge-unit IDs and filenames.

No existing Frozen content should be modified directly to satisfy the Evidence
Layer without Product Owner-approved change control.

## 11. Migration Strategy

Migration should happen in staged, reviewable increments:

1. Architecture approval: accept ADRs for evidence separation, citation, and
   confidence.
2. Schema proposal: define a richer evidence schema and relation semantics.
3. Loader proposal: extend the registry with evidence loading without changing
   the current `build_registry()` legacy shape.
4. Validation proposal: add duplicate, broken-reference, citation, confidence,
   and source-kind checks.
5. Seed evidence records: introduce a small reviewed evidence corpus.
6. Link migration: update non-Frozen or change-controlled knowledge units to
   reference evidence IDs.
7. Catalog projection: expose evidence traceability as generated read-only
   catalog data.
8. Review gate: run validation, pytest, and ruff before marking any future Epic
   ready for review.

The first migration should avoid mass editing the Batch 1 knowledge units until
evidence records exist and the Product Owner approves the change scope.

## 12. Validation Requirements For Future Implementation

Future implementation should validate:

- evidence ID uniqueness;
- evidence filename contains ID;
- source kind is known;
- citation IDs are unique inside each evidence record;
- citation locators are present for source kinds that require them;
- evidence relations point to existing knowledge units;
- knowledge-unit evidence references point to existing evidence records when
  they use `NT-EVIDENCE-*` IDs;
- confidence levels are valid;
- numeric confidence scores stay within range when present;
- evidence lifecycle status is compatible with consuming knowledge units;
- Frozen knowledge-unit changes follow change control.

## 13. ADRs Accepted

TASK-010 introduced these ADRs, accepted during the Milestone 1 freeze:

- ADR-0010: Evidence Layer separation and source abstraction.
- ADR-0011: Citation traceability and confidence scoring.

Both are accepted durable architecture decisions for the Milestone 1 Evidence
Layer foundation.

## 14. Risks And Open Questions

Risks:

- Evidence metadata could become too heavy for authors if required too early.
- Numeric confidence scores may create false precision.
- Citation quality may vary across books, web pages, interviews, and internal
  observations.
- Frozen Batch 1 units currently have provisional evidence and no references.
- External source licensing and copyright constraints must be handled carefully.

Open questions:

- Should evidence records live only under `knowledge/evidence/`, or should
  source metadata have a separate `knowledge/sources/` directory?
- Should evidence-to-knowledge links be embedded in evidence records only, or
  mirrored in knowledge-unit summaries after migration?
- Should confidence aggregation be manual, computed, or hybrid?
- Which source kinds require hard citation locator rules?

## 15. Acceptance Criteria For A Future Implementation Epic

A future implementation Epic should be ready for review when:

- evidence records validate against an approved schema;
- registry and catalog expose evidence separately from canonical knowledge;
- current inline evidence summaries remain backward-compatible;
- citation and confidence fields are tested with positive and negative cases;
- broken evidence references fail validation;
- Frozen content is not modified without change control;
- generated traceability can be inspected deterministically.
