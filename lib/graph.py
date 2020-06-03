"""
"""

import copy
from collections import defaultdict, OrderedDict
from typing import Dict, Iterable, Iterator, List, Mapping, Set

from declaration import Declaration
from traits import __Debug__

__all__ = (
    "Graph",
    "GraphEdgeError",
    "GraphError",
    "GraphWalkError",
)


class GraphError(Exception):
    """
    Base class for all graph errors.
    """
    pass


class GraphEdgeError(GraphError):
    """
    Error thrown when a Declaration has a dependency that does not exist.
    """
    def __init__(self, name: str, dependency: str):
        super(
        ).__init__(f"Declaration {name} has unknown dependency {dependency}")
        self.name = name
        self.dependency = dependency


class GraphWalkError(GraphError):
    """
    Error thrown when graph-walking fails to visit all Declarations.
    """
    def __init__(self, not_visited: Dict[str, Set[str]]):
        super().__init__(
            f"Failed to visit all Declarations during walk: {str(not_visited.keys())}"
        )
        self.not_visited = not_visited


class Graph(__Debug__):
    """
    A graph-representation of a collection of Declarations.

    Creates several mappings upon construction between Declarations, their
    names, and their dependencies.
    """
    def __init__(self, declarations: Iterable[Declaration]):
        self._declarations: Mapping[str, Declaration] = OrderedDict()
        for declaration in declarations:
            self._declarations[declaration.name] = declaration

        self._dependencies: Mapping[str, Set[str]] = defaultdict(set)
        self._reverse_dependencies: Mapping[str, Set[str]] = defaultdict(set)
        for name, declaration in self._declarations.items():
            # Create the empty-set if it does not exist yet.
            self._dependencies[name]
            # Populate the forward- and reverse-dependency mappings for this
            # declaration.
            for dependency_name in declaration.dependencies:
                if dependency_name not in self._declarations:
                    raise GraphEdgeError(name, dependency_name)
                self._dependencies[name].add(dependency_name)
                self._reverse_dependencies[dependency_name].add(name)

    def walk(self) -> Iterator[Declaration]:
        """
        Traverse this Graph, yielding Declarations in dependency order.
        """

        visited: Set[str] = set()
        visitable: List[str] = list()
        not_visited: Mapping[str, Set[str]] = copy.deepcopy(self._dependencies)

        # Mark all declarations without dependencies as immediately-visitable.
        for name, dependencies in not_visited.items():
            if not dependencies:
                visitable.append(name)

        # Remove all declarations that are now visitable from not_visited.
        for name in visitable:
            not_visited.pop(name, None)

        # Iteratively yield the next visitable Declaration, moving elements from
        # not_visited to visitable as their dependencies are visited.
        while visitable:
            visited_name = visitable.pop(0)
            yield self._declarations[visited_name]

            visited.add(visited_name)
            not_visited.pop(visited_name, None)
            for not_visited_name, dependencies in not_visited.items():
                # Mark this not_visited element as visitable if we have just
                # visited its last outstanding dependency.
                if dependencies:
                    dependencies.discard(visited_name)
                    if not dependencies:
                        visitable.append(not_visited_name)

        # Indicate that walking completed unsuccessfully, reporting the
        # Declarations that were not visited.
        if not_visited:
            raise GraphWalkError(dict(not_visited))
