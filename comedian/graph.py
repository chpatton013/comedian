"""
Graph API for relating GraphNodes to each other.

GraphNodes contain names, and (optionally) references to the names of other
nodes. Graphs contain a collection of GraphNodes, and maintain several mapping
structures between nodes according to their declared references.

TODO: Add cycle detection to graph construction
"""

import copy
import logging
import os
from collections import defaultdict, OrderedDict
from typing import (
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
)

from .traits import __Debug__, __Eq__

__all__ = (
    "Graph",
    "GraphEdgeError",
    "GraphError",
    "GraphNode",
    "GraphResolveError",
    "GraphWalkError",
)


class GraphError(Exception):
    """
    Base class for all graph errors.
    """
    pass


class GraphEdgeError(GraphError):
    """
    Error thrown when a GraphNode has a dependency or reference that does not
    exist.
    """
    def __init__(self, name: str, dependency: str):
        super().__init__(
            f"GraphNode {name} has unknown dependency {dependency}",
        )
        self.name = name
        self.dependency = dependency


class GraphResolveError(GraphError):
    """
    Error thrown when resolving a reference to a GraphNode.
    """
    def __init__(self, reference: str):
        super().__init__(f"Failed to resolve reference: {reference}")
        self.reference = reference


class GraphWalkError(GraphError):
    """
    Error thrown when graph-walking fails to visit all GraphNode.
    """
    def __init__(self, not_visited: Dict[str, Set[str]]):
        super().__init__(
            f"Failed to visit all GraphNode during walk: {str(list(not_visited.keys()))}",
        )
        self.not_visited = not_visited


class GraphNode(__Debug__, __Eq__):
    """
    A single node within a Graph, consisting of a unique name, a list of
    dependencies, and a list of non-dependency references.
    """
    def __init__(
        self,
        name: str,
        dependencies: List[str],
        references: List[str] = [],
    ):
        self.name = name
        self.dependencies = dependencies
        self.references = references

    def resolve(self) -> Tuple[Optional[str], Optional[str]]:
        return None, None


class Graph(__Debug__):
    """
    A graph-representation of a collection of GraphNodes.

    Creates several mappings upon construction between GraphNodes, their
    names, and their dependencies.
    """
    def __init__(self, nodes: Iterable[GraphNode]):
        self._nodes: Mapping[str, GraphNode] = OrderedDict()
        for node in nodes:
            self._nodes[node.name] = node

        self._dependencies: Mapping[str, Set[str]] = defaultdict(set)
        self._reverse_dependencies: Mapping[str, Set[str]] = defaultdict(set)
        for name, node in self._nodes.items():
            # Create the empty-set if it does not exist yet.
            self._dependencies[name]
            # Populate the forward- and reverse-dependency mappings for this
            # node.
            for dependency_name in node.dependencies:
                if dependency_name not in self._nodes:
                    raise GraphEdgeError(name, dependency_name)
                self._dependencies[name].add(dependency_name)
                self._reverse_dependencies[dependency_name].add(name)
            # Ensure that all other references exist.
            for reference_name in node.references:
                if reference_name not in self._nodes:
                    raise GraphEdgeError(name, reference_name)

    def resolve(self, name: str) -> Optional[str]:
        """
        Resolve the name of a GraphNode to a filepath whose parts are produced
        by an explicit chain of "parent" GraphNode.
        """

        logging.debug("Graph.resolve %s", name)

        # Ensure that the node exists.
        try:
            node = self._nodes[name]
        except KeyError:
            raise GraphResolveError(name)

        # Ensure that the "parent" node is declared as a dependency or reference
        # of the input node.
        parent_name, node_path = node.resolve()
        if (
            parent_name and parent_name not in node.dependencies and
            parent_name not in node.references
        ):
            raise GraphResolveError(parent_name)
        parent_path = self.resolve(parent_name) if parent_name else None

        logging.debug(" --> %s %s", parent_path, node_path)

        # Produce a resultant resolved path by joining the parent-path and
        # current-path if they are both set. Otherwise, return the one that is
        # set (or None if neither).
        if parent_path and node_path:
            return os.path.join(parent_path, node_path)
        elif parent_path:
            return parent_path
        elif node_path:
            return node_path
        else:
            return None

    def walk(self) -> Iterator[GraphNode]:
        """
        Traverse this Graph, yielding GraphNodes in dependency order.
        """

        visited: Set[str] = set()
        visitable: List[str] = list()
        not_visited: Mapping[str, Set[str]] = copy.deepcopy(self._dependencies)

        # Mark all nodes without dependencies as immediately-visitable.
        for name, dependencies in not_visited.items():
            if not dependencies:
                visitable.append(name)

        # Remove all nodes that are now visitable from not_visited.
        for name in visitable:
            not_visited.pop(name, None)

        # Iteratively yield the next visitable GraphNode, moving elements from
        # not_visited to visitable as their dependencies are visited.
        while visitable:
            visited_name = visitable.pop(0)
            yield self._nodes[visited_name]

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
        # GraphNodes that were not visited.
        if not_visited:
            raise GraphWalkError(dict(not_visited))
