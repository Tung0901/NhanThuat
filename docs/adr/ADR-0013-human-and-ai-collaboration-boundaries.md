# ADR-0013: Human And AI Collaboration Boundaries

**Status:** accepted  
**Date:** 2026-07-20  
**Deciders:** Product Owner

## Context

Nhan Thuat is designed to be human-readable, AI-readable, auditable, and governed
by Product Owner authority. AI can accelerate drafting, relation proposal,
duplicate detection, conflict review, validation planning, and review-package
preparation. However, AI-generated content can also introduce overconfident
claims, weak provenance, unnoticed duplication, and unauthorized governance
changes.

## Decision

Propose that AI may assist the Knowledge Factory but must not hold approval,
Frozen, or durable governance authority.

AI may:

- draft candidate knowledge units;
- propose taxonomy and ontology links;
- identify possible duplicates or conflicts;
- suggest evidence needs;
- prepare validation and review materials;
- update implementation or content only within an approved task scope.

Humans, and specifically the Product Owner where required, retain authority over:

- approval;
- Frozen state;
- constitutional or governance changes;
- durable ADR acceptance;
- conflict disposition;
- evidence confidence interpretation;
- final editorial meaning.

AI-generated drafts must remain reviewable repository changes and must not be
treated as official until they pass the required review and approval process.

## Consequences

- AI can improve throughput without replacing accountability.
- Provenance and evidence limits stay visible.
- Product Owner authority remains consistent with the Constitution.
- Future factory tooling should record AI assistance where it materially shaped
  content or review decisions.
- Frozen content remains protected from direct AI modification without formal
  change control.
