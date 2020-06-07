#!/usr/bin/env python3

import unittest

from context import comedian

from comedian.graph import (
    Graph,
    GraphEdgeError,
    GraphNode,
    GraphWalkError,
)


class TestDeclaration(Declaration):
    pass



class GraphEdgeTest(unittest.TestCase):
    def test_unknown_dependency(self):
        a = TestGraphNode("a", ["b"])

        nodes = [a]
        with self.assertRaises(GraphEdgeError) as context:
            graph = Graph(nodes)

        self.assertEqual("a", context.exception.name)
        self.assertEqual("b", context.exception.dependency)

    def test_unknown_reference(self):
        a = TestGraphNode("a", [], ["b"])

        nodes = [a]
        with self.assertRaises(GraphEdgeError) as context:
            graph = Graph(nodes)

        self.assertEqual("a", context.exception.name)
        self.assertEqual("b", context.exception.dependency)


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


if __name__ == "__main__":
    unittest.main()
