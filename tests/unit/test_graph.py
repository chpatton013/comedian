import unittest
from typing import Callable, List

from context import comedian  # pylint: disable=W0611

from comedian.graph import (
    Graph,
    GraphEdgeError,
    GraphNameError,
    GraphNode,
    GraphResolveError,
    GraphWalkError,
    ResolveLink,
)


class TestGraphNode(GraphNode):
    def __init__(
        self,
        name: str,
        dependencies: List[str],
        references: List[str] = None,
        resolve_device: ResolveLink = ResolveLink(None, None),
        resolve_path: ResolveLink = ResolveLink(None, None),
    ):
        if references is None:
            references = []
        super().__init__(name, dependencies, references)
        self._resolve_device = resolve_device
        self._resolve_path = resolve_path

    def resolve_device(self) -> ResolveLink:
        return self._resolve_device

    def resolve_path(self) -> ResolveLink:
        return self._resolve_path


def _make_device_node_factory() -> Callable[..., TestGraphNode]:
    def fn(
        name: str,
        dependencies: List[str],
        references: List[str] = None,
        resolve: ResolveLink = ResolveLink(None, None),
    ) -> TestGraphNode:
        if references is None:
            references = []
        return TestGraphNode(
            name, dependencies, references=references, resolve_device=resolve
        )

    return fn


def _make_path_node_factory() -> Callable[..., TestGraphNode]:
    def fn(
        name: str,
        dependencies: List[str],
        references: List[str] = None,
        resolve: ResolveLink = ResolveLink(None, None),
    ) -> TestGraphNode:
        if references is None:
            references = []
        return TestGraphNode(
            name, dependencies, references=references, resolve_path=resolve
        )

    return fn


class GraphNameTest(unittest.TestCase):
    def test_repeat_name(self):
        a1 = TestGraphNode("a", [])
        a2 = TestGraphNode("a", [])

        nodes = [a1, a2]
        with self.assertRaises(GraphNameError) as context:
            Graph(nodes)

        self.assertEqual("a", context.exception.name)


class GraphEdgeTest(unittest.TestCase):
    def test_unknown_dependency(self):
        a = TestGraphNode("a", ["b"])

        nodes = [a]
        with self.assertRaises(GraphEdgeError) as context:
            Graph(nodes)

        self.assertEqual("a", context.exception.name)
        self.assertEqual("b", context.exception.dependency)

    def test_unknown_reference(self):
        a = TestGraphNode("a", [], ["b"])

        nodes = [a]
        with self.assertRaises(GraphEdgeError) as context:
            Graph(nodes)

        self.assertEqual("a", context.exception.name)
        self.assertEqual("b", context.exception.dependency)


class GraphResolveTest(unittest.TestCase):
    parameterization = (
        (
            "Test path resolution",
            _make_path_node_factory(),
            lambda graph, name: graph.resolve_path(name),
        ),
        (
            "Test device resolution",
            _make_device_node_factory(),
            lambda graph, name: graph.resolve_device(name),
        ),
    )

    def test_unknown_direct_resolve(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory("a", [])

                nodes = [a]
                graph = Graph(nodes)

                with self.assertRaises(GraphResolveError) as context:
                    graph_resolve(graph, "b")

                self.assertEqual("b", context.exception.reference)

    def test_successful_direct_resolve(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory("a", [], resolve=ResolveLink(None, "x"))

                nodes = [a]
                graph = Graph(nodes)

                self.assertEqual("x", graph_resolve(graph, "a"))

    def test_unknown_recursive_resolve(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory("a", ["b"], resolve=ResolveLink("b", "y"))
                b = node_factory("b", [], resolve=ResolveLink("c", "x"))

                nodes = [a, b]
                graph = Graph(nodes)

                with self.assertRaises(GraphResolveError) as context:
                    graph_resolve(graph, "a")

                self.assertEqual("c", context.exception.reference)

    def test_undeclared_recursive_resolve(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory("a", [], resolve=ResolveLink("b", "y"))
                b = node_factory("b", [], resolve=ResolveLink(None, "x"))

                nodes = [a, b]
                graph = Graph(nodes)

                with self.assertRaises(GraphResolveError) as context:
                    graph_resolve(graph, "a")

                self.assertEqual("b", context.exception.reference)

    def test_successful_recursive_resolve(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory("a", ["b"], resolve=ResolveLink("b", "y"))
                b = node_factory("b", [], resolve=ResolveLink(None, "x"))

                nodes = [a, b]
                graph = Graph(nodes)

                self.assertEqual("x/y", graph_resolve(graph, "a"))

    def test_successful_recursive_resolve_with_join(self):
        for msg, node_factory, graph_resolve in GraphResolveTest.parameterization:
            with self.subTest(msg=msg):
                a = node_factory(
                    "a", ["b"], resolve=ResolveLink("b", "y", lambda l, r: f"{l}j{r}")
                )
                b = node_factory(
                    "b", [], resolve=ResolveLink(None, "x", lambda l, r: f"{l}i{r}")
                )

                nodes = [a, b]
                graph = Graph(nodes)

                self.assertEqual("xiy", graph_resolve(graph, "a"))


class GraphWalkTest(unittest.TestCase):
    def test_empty(self):
        graph = Graph([])
        with self.assertRaises(StopIteration):
            next(graph.walk())

    def test_no_deps(self):
        a = TestGraphNode("a", [])
        b = TestGraphNode("b", [])
        c = TestGraphNode("c", [])

        nodes = [a, b, c]
        graph = Graph(nodes)

        expected = [a, b, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_forward_chain(self):
        a = TestGraphNode("a", [])
        b = TestGraphNode("b", ["a"])
        c = TestGraphNode("c", ["b"])

        nodes = [a, b, c]
        graph = Graph(nodes)

        expected = [a, b, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_reverse_chain(self):
        a = TestGraphNode("a", ["b"])
        b = TestGraphNode("b", ["c"])
        c = TestGraphNode("c", [])

        nodes = [a, b, c]
        graph = Graph(nodes)

        expected = [c, b, a]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_forward_branch(self):
        a = TestGraphNode("a", [])
        b = TestGraphNode("b", ["a"])
        c = TestGraphNode("c", ["b"])
        d = TestGraphNode("d", ["a"])
        e = TestGraphNode("e", ["d"])

        nodes = [a, b, c, d, e]
        graph = Graph(nodes)

        expected = [a, b, d, c, e]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_reverse_branch(self):
        a = TestGraphNode("a", ["b"])
        b = TestGraphNode("b", ["e"])
        c = TestGraphNode("c", ["d"])
        d = TestGraphNode("d", ["e"])
        e = TestGraphNode("e", [])

        nodes = [a, b, c, d, e]
        graph = Graph(nodes)

        expected = [e, b, d, a, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_diamond(self):
        a = TestGraphNode("a", [])
        b = TestGraphNode("b", ["a"])
        c = TestGraphNode("c", ["a"])
        d = TestGraphNode("d", ["b", "c"])

        nodes = [a, b, c, d]
        graph = Graph(nodes)

        expected = [a, b, c, d]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_self_reference(self):
        a = TestGraphNode("a", ["a"])

        nodes = [a]
        graph = Graph(nodes)

        with self.assertRaises(GraphWalkError) as context:
            next(graph.walk())

        expected = {"a": {"a"}}
        self.assertEqual(expected, context.exception.not_visited)

    def test_cycle(self):
        a = TestGraphNode("a", [])
        b = TestGraphNode("b", ["a", "c"])
        c = TestGraphNode("c", ["b"])
        d = TestGraphNode("d", ["c"])

        nodes = [a, b, c, d]
        graph = Graph(nodes)
        walk = graph.walk()

        self.assertEqual(a, next(walk))

        with self.assertRaises(GraphWalkError) as context:
            next(walk)

        expected = {
            "b": {"c"},
            "c": {"b"},
            "d": {"c"},
        }
        self.assertEqual(expected, context.exception.not_visited)
