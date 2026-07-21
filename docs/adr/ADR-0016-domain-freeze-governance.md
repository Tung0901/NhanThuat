# ADR-0016: Domain Freeze Governance

**Status:** accepted  
**Date:** 2026-07-21  
**Deciders:** Product Owner

## Context

ADR-0015 required future implementation to define frozen-register checks for
non-Epic entries and atomic batch/member freeze semantics before domain content
can be frozen. Human Nature final review exposed that the repository could
validate Frozen Epics and Milestones, but did not yet enforce domain-level
Frozen governance.

## Decision

Domain areas are first-class governance subjects. A domain area may have a
machine-readable status artifact at `docs/domains/<slug>/status.yaml` with:

- `domain_area_id`;
- `slug`;
- `name`;
- `status`;
- `previous_status` for Frozen transition validation;
- `approved_by` and `frozen_at` when Frozen;
- `blockers`;
- non-empty `members` grouped by unit type for atomic domain freeze checks;
- non-empty `artifacts` listing domain documents included in the freeze.

Domain lifecycle states use the existing repository vocabulary:

`idea -> draft -> review -> ready_for_review -> approved -> frozen`

`deprecated` is allowed as a terminal governance state. Product Owner approval
is still required before `approved` or `frozen`. A Product Owner-approved freeze
task may move a domain directly from `ready_for_review` to `frozen` when the
approval is explicit in the task.

A Frozen domain must have a `domain_area` entry in
`governance/frozen-register.yaml`. The entry must point to the domain status
artifact and must match its ID, Frozen status, approval metadata, and freeze
date. Duplicate Frozen entries or duplicate sources are validation failures.

When a Frozen domain status artifact declares `members`, each listed knowledge
unit must also be `frozen` and must match the declared member group type. Frozen
domain artifacts must include members, explicit artifact paths inside the domain
directory, and `unit_counts` that match the member inventory. The artifact list
must match the domain directory file inventory. This gives domain freeze atomic
semantics without requiring the validator to infer content membership from
prose. Domain members may include the existing knowledge-unit types law,
principle, model, strategy, tool, case, evidence, and anti-pattern. Standalone
Evidence Layer records are intentionally excluded from domain-member semantics
because they have a separate evidence lifecycle and registry.

## Consequences

- Existing Epic, Milestone, and Batch frozen-register records remain valid.
- Domain-level freeze can be validated before Human Nature or any later domain
  is frozen.
- Domain freeze remains separate from content authoring and from Product Owner
  approval.
- Future domain freeze tasks can update lifecycle metadata, frozen register,
  changelog, and roadmap without modifying the Domain Freeze infrastructure.
- Status artifacts without `members` remain valid for non-Frozen planning and
  review states.
