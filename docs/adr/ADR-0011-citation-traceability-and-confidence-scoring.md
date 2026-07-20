# ADR-0011: Citation Traceability And Confidence Scoring

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

The Constitution requires knowledge records to preserve context, uncertainty,
exceptions, evidence level, and traceable references when available. Current
knowledge units can state a qualitative evidence level, but they cannot yet
represent precise citations, source locators, claim-level support, contestation,
or confidence rationale.

Future AI-readable catalogs and review packages need citation traceability that
does not invent provenance or collapse uncertainty into false certainty.

## Decision

Propose a claim-addressable citation model and an editorial confidence model.

Citations should point to specific source locations when possible, including
page, section, paragraph, timestamp, row, figure, URL, repository path, DOI,
ISBN, or archive locator. Evidence records should summarize source claims and
connect them to the knowledge units they support, contest, or contextualize.

Confidence should remain qualitative first, using the existing evidence levels:
`hypothesis`, `provisional`, `supported`, `strong`, and `contested`. A future
optional numeric score from `0.0` to `1.0` may support ranking and review
workflows, but it must include a rationale and should not be treated as
universal certainty.

## Consequences

- Citation traceability becomes inspectable by humans and future AI consumers.
- Existing inline evidence summaries remain valid during migration.
- Numeric confidence is optional and cannot replace reviewer judgment.
- Validation can later enforce citation IDs, locator requirements, confidence
  ranges, and evidence-to-knowledge reference integrity.
- Evidence can support, contest, or contextualize knowledge without requiring
  immediate rewrites of canonical law and principle records.
