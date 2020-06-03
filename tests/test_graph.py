#!/usr/bin/env python3

import unittest

from context import comedian

from comedian.declaration import Declaration
from comedian.graph import Graph, GraphEdgeError, GraphWalkError


class TestDeclaration(Declaration):
    pass


class GraphTest(unittest.TestCase):
    def test_empty(self):
        graph = Graph([])
        with self.assertRaises(StopIteration):
            next(graph.walk())

    def test_unknown_dependency(self):
        a = TestDeclaration("a", ["b"])

        declarations = [a]
        with self.assertRaises(GraphEdgeError) as context:
            graph = Graph(declarations)

        self.assertEqual("a", context.exception.name)
        self.assertEqual("b", context.exception.dependency)

    def test_no_deps(self):
        a = TestDeclaration("a", [])
        b = TestDeclaration("b", [])
        c = TestDeclaration("c", [])

        declarations = [a, b, c]
        graph = Graph(declarations)

        expected = [a, b, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_forward_chain(self):
        a = TestDeclaration("a", [])
        b = TestDeclaration("b", ["a"])
        c = TestDeclaration("c", ["b"])

        declarations = [a, b, c]
        graph = Graph(declarations)

        expected = [a, b, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_reverse_chain(self):
        a = TestDeclaration("a", ["b"])
        b = TestDeclaration("b", ["c"])
        c = TestDeclaration("c", [])

        declarations = [a, b, c]
        graph = Graph(declarations)

        expected = [c, b, a]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_forward_branch(self):
        a = TestDeclaration("a", [])
        b = TestDeclaration("b", ["a"])
        c = TestDeclaration("c", ["b"])
        d = TestDeclaration("d", ["a"])
        e = TestDeclaration("e", ["d"])

        declarations = [a, b, c, d, e]
        graph = Graph(declarations)

        expected = [a, b, d, c, e]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_reverse_branch(self):
        a = TestDeclaration("a", ["b"])
        b = TestDeclaration("b", ["e"])
        c = TestDeclaration("c", ["d"])
        d = TestDeclaration("d", ["e"])
        e = TestDeclaration("e", [])

        declarations = [a, b, c, d, e]
        graph = Graph(declarations)

        expected = [e, b, d, a, c]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_diamond(self):
        a = TestDeclaration("a", [])
        b = TestDeclaration("b", ["a"])
        c = TestDeclaration("c", ["a"])
        d = TestDeclaration("d", ["b", "c"])

        declarations = [a, b, c, d]
        graph = Graph(declarations)

        expected = [a, b, c, d]
        actual = list(graph.walk())
        self.assertListEqual(expected, actual)

    def test_self_reference(self):
        a = TestDeclaration("a", ["a"])

        declarations = [a]
        graph = Graph(declarations)

        with self.assertRaises(GraphWalkError) as context:
            next(graph.walk())

        expected = {"a": {"a"}}
        self.assertEqual(expected, context.exception.not_visited)

    def test_cycle(self):
        a = TestDeclaration("a", [])
        b = TestDeclaration("b", ["a", "c"])
        c = TestDeclaration("c", ["b"])
        d = TestDeclaration("d", ["c"])

        declarations = [a, b, c, d]
        graph = Graph(declarations)
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
