# ADR-0017: Phenomenon Unit Type and domain_area Metadata

**Status:** accepted
**Date:** 2026-08-14
**Deciders:** Product Owner (via M16 review package approval)

## Context

The M16 knowledge expansion introduced ten new domain areas
(`NT-DA-0021`..`NT-DA-0030`) covering human behavior: cognitive science and
sensemaking, behavioral economics and choice architecture, behavioral design,
social psychology, and persuasion and influence. These domains describe
observable behavioral regularities that are better modeled as *phenomena*
(e.g. "progress momentum cycle", "ethical safeguard matrix") than as laws,
principles, models, or anti-patterns. The unit schema therefore had to evolve to
support a new unit type and to link units to the domain-area registry.

## Decision

1. **New unit type `phenomenon`.** The knowledge-unit schema extends the `type`
   enum with `phenomenon` and the `id` pattern with the `PHENOMENON` prefix
   (`^NT-PHENOMENON-[0-9]{4}$`). `identifiers.py` maps `phenomenon` to the
   `PHENOMENON` prefix; `validator.py` accepts the `phenomena` member group in
   frozen domain status artifacts and maps it to `type: phenomenon`;
   `factory.py` recognizes the type in quality-gate messages.
2. **Optional `domain_area` metadata on units.** A unit may declare
   `domain_area: ^NT-DA-[0-9]{4}$` to link itself to a domain-area registry id.
   The field is optional to preserve compatibility with all pre-existing frozen
   units (NT-DA-0001..0020), which do not carry it.
3. **Validation.** The repository validator now enforces that any present
   `domain_area` value must exist in `knowledge/domain-registry.yaml` (referential
   integrity). Units without the field remain valid.

## Consequences

- 96 new units (NT-DA-0021..0030) all carry `domain_area`; the 274 pre-existing
  frozen units do not and remain valid.
- Frozen domain status artifacts may declare `phenomena` members; validator
  cross-checks member type, unit status, and `unit_counts` exactly as for other
  groups.
- Domain freeze governance (ADR-0016) and `governance/domain-freeze.md` are
  updated to include the `phenomena` group.
- This ADR documents the schema evolution required by M16; it does not change
  the public contract (V1) which remains immutable.