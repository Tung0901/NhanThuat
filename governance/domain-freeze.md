# Domain Freeze Governance

**ID:** NT-GOV-DOMAIN-FREEZE-001  
**Version:** 0.1.0  
**Status:** accepted  
**Owner:** Product Owner  
**Created:** 2026-07-21

Domain Freeze is the governance process for making a domain area an official,
change-controlled part of Nhan Thuat.

## Lifecycle

Domain areas use the repository lifecycle vocabulary:

`idea -> draft -> review -> ready_for_review -> approved -> frozen`

`deprecated` may be used for retained historical content that should no longer
be expanded. Only the Product Owner may move a domain area to `approved` or
`frozen`.

## Status Artifact

A domain status artifact lives at:

```text
docs/domains/<slug>/status.yaml
```

The status artifact must declare:

- `domain_area_id`;
- `slug`;
- `name`;
- `status`;
- `blockers`.

Frozen domains must also declare:

- `approved_by`;
- `frozen_at`;
- `previous_status`;
- no blockers;
- non-empty `members` grouped by unit type;
- non-empty `artifacts` listing domain documents included in the freeze.

`previous_status` is required when entering `frozen` so validation can reject
invalid transitions. Product Owner-approved domain freeze may move directly from
`ready_for_review` to `frozen`.

## Frozen Register

Frozen domains are registered in `governance/frozen-register.yaml` using:

```yaml
type: domain_area
```

The Frozen Register entry must match the source status artifact:

- same domain ID;
- `status: frozen`;
- same `approved_by`;
- same `frozen_at`;
- source path points to the domain status artifact.

Duplicate Frozen entries and duplicate Frozen sources are validation failures.

## Atomic Member Semantics

Every Frozen domain status artifact must declare non-empty `members`. Every
listed knowledge unit must also be Frozen and must match the declared member
group type, such as `laws` for `type: law`. Supported member groups are `laws`,
`principles`, `models`, `strategies`, `tools`, `cases`, `evidence_units`,
`anti_patterns`, and `phenomena`. `evidence_units` covers the legacy knowledge-unit
type `evidence`; standalone Evidence Layer records remain governed by the Evidence
Layer and are not domain members. The validator checks the listed IDs against
the loaded knowledge registry content and verifies `unit_counts` exactly against
the member lists.

Frozen domains must also declare non-empty `artifacts` so the domain planning
documents included in the freeze are explicit. The artifact list must include
the domain `status.yaml`, contain no duplicates, remain inside the matching
`docs/domains/<slug>/` directory, point only to existing files, and match the
domain directory file inventory.

The validator does not infer domain membership from prose, tags, or directory
names. Domain freeze scope must be explicit.

## Change Control

Frozen domains and their declared members must not be modified directly. Any
change requires Product Owner-approved change control, rationale, impact note,
and relevant validation/test evidence.
