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
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
)

from comedian.traits import __Debug__, __Eq__

__all__ = (
    "Graph",
    "GraphEdgeError",
    "GraphError",
    "GraphNameError",
    "GraphNode",
    "GraphResolveError",
    "GraphWalkError",
)


class GraphError(Exception):
    """
    Base class for all graph errors.
    """
    pass


class GraphNameError(GraphError):
    """
    Error thrown when a GraphNode has a name that already exists.
    """
    def __init__(self, name: str):
        super().__init__(f"GraphNode {name} has repeated name")
        self.name = name


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


class ResolveLink(__Debug__, __Eq__):
    def __init__(
        self,
        parent: Optional[str],
        value: Optional[str],
        join: Callable[[str, str], str] = os.path.join,
    ):
        self.parent = parent
        self.value = value
        self.join = join

    def __iter__(self) -> Iterator[Any]:
        yield from (self.parent, self.value, self.join)

    def __fields__(self) -> Iterator[str]:
        yield from ("parent", "value")


class ResolveResult(__Debug__, __Eq__):
    def __init__(self, path: Optional[str], join: Callable[[str, str], str]):
        self.path = path
        self.join = join


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

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, None)


class Graph(__Debug__):
    """
    A graph-representation of a collection of GraphNodes.

    Creates several mappings upon construction between GraphNodes, their
    names, and their dependencies.
    """
    def __init__(self, nodes: Iterable[GraphNode]):
        self._nodes: Mapping[str, GraphNode] = OrderedDict()
        for node in nodes:
            if node.name in self._nodes:
                raise GraphNameError(node.name)
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

    def resolve_device(self, name: str) -> Optional[str]:
        """
        Resolve the name of a GraphNode to a devicepath whose parts are produced
        by an explicit chain of "parent" GraphNodes.
        """

        logging.debug("Graph.resolve_device %s", name)

        return self._resolve_device(name).path

    def resolve_path(self, name: str) -> Optional[str]:
        """
        Resolve the name of a GraphNode to a filepath whose parts are produced
        by an explicit chain of "parent" GraphNodes.
        """

        logging.debug("Graph.resolve_path %s", name)

        return self._resolve_path(name).path

    def _resolve_device(self, name: str) -> ResolveResult:
        return self._resolve(
            name,
            lambda node: node.resolve_device(),
            lambda name: self._resolve_device(name),
        )

    def _resolve_path(self, name: str) -> ResolveResult:
        return self._resolve(
            name,
            lambda node: node.resolve_path(),
            lambda name: self._resolve_path(name),
        )

    def _resolve(
        self,
        name: str,
        node_resolve: Callable[[str], ResolveLink],
        graph_resolve: Callable[[str], ResolveResult],
    ) -> ResolveResult:
        # Ensure that the node exists.
        try:
            node = self._nodes[name]
        except KeyError:
            raise GraphResolveError(name)

        # Ensure that the "parent" node is declared as a dependency or reference
        # of the input node.
        link = node_resolve(node)
        if (
            link.parent and link.parent not in node.dependencies and
            link.parent not in node.references
        ):
            raise GraphResolveError(link.parent)
        if link.parent:
            parent_result = graph_resolve(link.parent)
        else:
            parent_result = ResolveResult(None, link.join)

        logging.debug(" --> %s %s", parent_result.path, link.value)

        # Produce a resultant resolved path by joining the parent-path and
        # current-path if they are both set. Otherwise, return the one that is
        # set (or None if neither).
        if parent_result.path and link.value:
            return ResolveResult(
                parent_result.join(parent_result.path, link.value),
                link.join,
            )
        elif parent_result.path:
            return ResolveResult(parent_result.path, link.join)
        elif link.value:
            return ResolveResult(link.value, link.join)
        else:
            return ResolveResult(None, link.join)
