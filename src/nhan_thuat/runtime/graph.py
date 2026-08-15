"""Knowledge graph traversal and dependency resolution."""

from collections import defaultdict
from collections.abc import Iterable

from nhan_thuat.models import KnowledgeRelation, KnowledgeUnit


class CircularDependencyError(Exception):
    """Raised when a circular dependency is detected in the knowledge graph."""


class KnowledgeGraph:
    """Represents a graph of knowledge units and their relations."""

    def __init__(self, units: Iterable[KnowledgeUnit]):
        self._units: dict[str, KnowledgeUnit] = {unit.id: unit for unit in units}
        self._relations: list[KnowledgeRelation] = []
        self._adjacency: dict[str, list[KnowledgeRelation]] = defaultdict(list)
        self._reverse_adjacency: dict[str, list[KnowledgeRelation]] = defaultdict(list)

        for unit in units:
            for relation in unit.iter_relations():
                self._relations.append(relation)
                self._adjacency[relation.source].append(relation)
                self._reverse_adjacency[relation.target].append(relation)

    def get_unit(self, unit_id: str) -> KnowledgeUnit | None:
        """Get a unit by its ID."""
        return self._units.get(unit_id)

    def get_dependencies(self, unit_id: str, relation_types: set[str] | None = None) -> list[KnowledgeUnit]:
        """Get immediate dependencies of a unit."""
        dependencies = []
        for relation in self._adjacency[unit_id]:
            if relation_types is None or relation.type in relation_types:
                target = self.get_unit(relation.target)
                if target:
                    dependencies.append(target)
        return dependencies

    def get_transitive_dependencies(self, unit_id: str, relation_types: set[str] | None = None) -> list[KnowledgeUnit]:
        """Traverse the graph to find all transitive dependencies."""
        visited: set[str] = set()
        result: list[KnowledgeUnit] = []

        def _dfs(current_id: str, path: set[str]):
            if current_id in path:
                raise CircularDependencyError(f"Circular dependency detected involving {current_id}: {' -> '.join(path)} -> {current_id}")
            if current_id in visited:
                return
            
            visited.add(current_id)
            path.add(current_id)
            
            for relation in self._adjacency[current_id]:
                if relation_types is None or relation.type in relation_types:
                    _dfs(relation.target, path)
                    target_unit = self.get_unit(relation.target)
                    if target_unit and target_unit.id not in [u.id for u in result]:
                        result.append(target_unit)
                        
            path.remove(current_id)

        _dfs(unit_id, set())
        return result
