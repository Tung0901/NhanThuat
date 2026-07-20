"""Taxonomy model for domains and domain-local topics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Domain


@dataclass(frozen=True)
class Taxonomy:
    domains: dict[str, Domain]

    @classmethod
    def from_domains(cls, domains: Iterable[Domain]) -> "Taxonomy":
        return cls(domains={domain.slug: domain for domain in sorted(domains, key=lambda item: item.id)})

    def require_domain(self, slug: str) -> Domain:
        try:
            return self.domains[slug]
        except KeyError as exc:
            raise KeyError(f"Unknown domain: {slug}") from exc

    def has_domain(self, slug: str) -> bool:
        return slug in self.domains

    def topics_for(self, slug: str) -> tuple[str, ...]:
        return self.require_domain(slug).topics

    def slugs(self) -> tuple[str, ...]:
        return tuple(self.domains)
