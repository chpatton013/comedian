import unittest
from typing import Iterator

from context import comedian  # pylint: disable=W0611

from comedian.traits import DebugMixin, EqMixin


class X(DebugMixin, EqMixin):
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __fields__(self) -> Iterator[str]:
        yield from ("x")


class XY(DebugMixin, EqMixin):
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __fields__(self) -> Iterator[str]:
        yield from ("x", "y")


class XYZ(DebugMixin, EqMixin):
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __fields__(self) -> Iterator[str]:
        yield from ("x", "y", "z")


class Default(DebugMixin, EqMixin):
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z


class FieldsTest(unittest.TestCase):
    def test_x(self):
        self.assertSetEqual({"x"}, set(X(1, 2, 3).__fields__()))
        self.assertEqual("X(x=1)", X(1, 2, 3).__str__())
        self.assertEqual(X(1, 2, 3), X(1, 2, 3))
        self.assertEqual(X(1, 2, 3), X(1, 2, 6))
        self.assertEqual(X(1, 2, 3), X(1, 5, 6))
        self.assertNotEqual(X(1, 2, 3), X(4, 5, 6))

    def test_xy(self):
        self.assertSetEqual({"x", "y"}, set(XY(1, 2, 3).__fields__()))
        self.assertEqual("XY(x=1, y=2)", XY(1, 2, 3).__str__())
        self.assertEqual(XY(1, 2, 3), XY(1, 2, 3))
        self.assertEqual(XY(1, 2, 3), XY(1, 2, 6))
        self.assertNotEqual(XY(1, 2, 3), XY(1, 5, 6))
        self.assertNotEqual(XY(1, 2, 3), XY(4, 5, 6))

    def test_xyz(self):
        self.assertSetEqual({"x", "y", "z"}, set(XYZ(1, 2, 3).__fields__()))
        self.assertEqual("XYZ(x=1, y=2, z=3)", XYZ(1, 2, 3).__str__())
        self.assertEqual(XYZ(1, 2, 3), XYZ(1, 2, 3))
        self.assertNotEqual(XYZ(1, 2, 3), XYZ(1, 2, 6))
        self.assertNotEqual(XYZ(1, 2, 3), XYZ(1, 5, 6))
        self.assertNotEqual(XYZ(1, 2, 3), XYZ(4, 5, 6))

    def test_default(self):
        self.assertSetEqual({"x", "y", "z"}, set(Default(1, 2, 3).__fields__()))
        self.assertEqual("Default(x=1, y=2, z=3)", Default(1, 2, 3).__str__())
        self.assertEqual(Default(1, 2, 3), Default(1, 2, 3))
        self.assertNotEqual(Default(1, 2, 3), Default(1, 2, 6))
        self.assertNotEqual(Default(1, 2, 3), Default(1, 5, 6))
        self.assertNotEqual(Default(1, 2, 3), Default(4, 5, 6))
