# EPIC 3 Laws And Principles Architecture

**Epic:** NT-EPIC-03  
**Status:** ready_for_review target  
**Date:** 2026-07-20  
**Scope:** Core laws and principles library

## Objective

EPIC 3 establishes the first curated library of core Nhan Thuat laws and
principles. It turns the EPIC 2 knowledge architecture into managed content while
preserving repository source-of-truth, validation, traceability, and Product
Owner approval boundaries.

## Boundaries

EPIC 3 implements knowledge content only. It does not implement search, AI
indexing, embeddings, LLM integration, ingestion pipelines, UI, CLI, external
storage, or performance optimization.

Frozen EPIC 0, EPIC 1, and EPIC 2 governance/status deliverables remain
unchanged. The existing registry and validator are used as-is.

## Content Architecture

The library uses two knowledge-unit types already supported by the Frozen EPIC 2
architecture:

- `law`: recurring behavioral or organizational tendency with conditions,
  exceptions, risks, and applications.
- `principle`: practical guidance derived from one or more laws.

Each unit must include stable ID, lifecycle status, version, summary, primary
domain, conditions, exceptions, applications, risks, evidence level, relations,
tags, and dates.

## Initial Content Set

EPIC 3 keeps the initial set deliberately small:

- `NT-LAW-0002`: Attention follows perceived significance.
- `NT-LAW-0003`: Trust reduces coordination cost.
- `NT-PRINCIPLE-0001`: Clarify interests before designing action.
- `NT-PRINCIPLE-0002`: Match role, capability, and authority.
- `NT-PRINCIPLE-0003`: Make coordination costs visible.

The existing `NT-LAW-0001` remains unchanged and becomes a dependency for the
first principle.

## Relation Strategy

Relations remain embedded in knowledge units and use the EPIC 2 vocabulary:

- principles `depends_on` laws they operationalize;
- laws may `supports` principles or other laws only when the direction is clear;
- conflicts are left empty until actual conflicting units exist;
- `applies_to` remains empty until application-target units exist.

This avoids invented graph edges while keeping future catalog traversal ready.

## Evidence Policy

All initial EPIC 3 units use `provisional` evidence with empty references. This
is intentional: the library records structured draft knowledge but does not claim
strong external support yet. Later Epics may add standalone evidence records and
citations without changing these IDs.

## Validation And Review

EPIC 3 acceptance requires:

- every added unit validates against `knowledge-unit.schema.json`;
- IDs are unique and match unit type;
- filenames contain record IDs;
- relation targets exist;
- tags use lowercase kebab-case;
- registry and catalog include all added units;
- tests cover the new content layer;
- EPIC 3 status is `ready_for_review`, not Approved or Frozen.

## Deferred Scope

Deferred items include evidence expansion, source citation records, search,
retrieval, AI behavior, UI, CLI, ingestion, external storage, and performance
work.
