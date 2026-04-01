"""Dependency registry."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass

from src.layer0_core.enums.wiring import LinkType


@dataclass(frozen=True)
class Dependency:
    """A dependency edge between two components."""

    from_component: str
    to_component: str
    link_type: LinkType


class DependencyRegistry:
    """Registry for component dependencies."""

    def __init__(self) -> None:
        self._dependencies: list[Dependency] = []

    def add(self, from_comp: str, to_comp: str, link_type: LinkType) -> None:
        """Add a dependency edge."""
        dependency = Dependency(from_component=from_comp, to_component=to_comp, link_type=link_type)
        if dependency not in self._dependencies:
            self._dependencies.append(dependency)

    def get_dependencies(self, component_id: str) -> list[str]:
        """Return direct dependencies for a component."""
        return [
            dependency.to_component
            for dependency in self._dependencies
            if dependency.from_component == component_id
        ]

    def get_dependents(self, component_id: str) -> list[str]:
        """Return direct dependents for a component."""
        return [
            dependency.from_component
            for dependency in self._dependencies
            if dependency.to_component == component_id
        ]

    def all(self) -> list[Dependency]:
        """Return all dependencies."""
        return list(self._dependencies)

    def topological_sort(self) -> tuple[list[str], list[str]]:
        """Return ordered components and remaining cycle components."""
        nodes = {dependency.from_component for dependency in self._dependencies} | {
            dependency.to_component for dependency in self._dependencies
        }
        indegree = {node: 0 for node in nodes}
        outgoing: dict[str, list[str]] = defaultdict(list)

        for dependency in self._dependencies:
            outgoing[dependency.to_component].append(dependency.from_component)
            indegree[dependency.from_component] += 1

        queue = deque(node for node, degree in indegree.items() if degree == 0)
        ordered: list[str] = []

        while queue:
            node = queue.popleft()
            ordered.append(node)
            for dependent in outgoing.get(node, []):
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    queue.append(dependent)

        cycle_components = [node for node, degree in indegree.items() if degree > 0]
        return ordered, cycle_components

    def detect_cycles(self) -> list[list[str]]:
        """Return cycles found in the dependency graph."""
        graph: dict[str, list[str]] = defaultdict(list)
        for dependency in self._dependencies:
            graph[dependency.from_component].append(dependency.to_component)

        cycles: list[list[str]] = []
        visiting: set[str] = set()
        visited: set[str] = set()
        path: list[str] = []

        def visit(node: str) -> None:
            if node in visited:
                return
            if node in visiting:
                if node in path:
                    cycle_start = path.index(node)
                    cycles.append(path[cycle_start:] + [node])
                return
            visiting.add(node)
            path.append(node)
            for neighbor in graph.get(node, []):
                visit(neighbor)
            path.pop()
            visiting.remove(node)
            visited.add(node)

        for node in list(graph):
            visit(node)
        return cycles
