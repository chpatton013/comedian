import unittest
from typing import Iterator

from context import comedian

from comedian.command import Command, CommandContext, CommandGenerator
from comedian.specification import Specification
from comedian.traits import __Debug__, __Eq__


class TestCommandGenerator(CommandGenerator, __Debug__, __Eq__):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield from ()


class SpecificationTest(unittest.TestCase):
    def test_fields(self):
        self.assertSetEqual(
            {"name", "dependencies", "references"},
            set(Specification("", []).__fields__()),
        )

    def test_properties(self):
        specification = Specification(
            "name",
            ["dependency"],
            ["reference"],
            apply=TestCommandGenerator("apply"),
            post_apply=TestCommandGenerator("post_apply"),
            up=TestCommandGenerator("up"),
            down=TestCommandGenerator("down"),
        )

        self.assertEqual("name", specification.name)
        self.assertListEqual(["dependency"], specification.dependencies)
        self.assertListEqual(["reference"], specification.references)
        self.assertEqual(TestCommandGenerator("apply"), specification.apply)
        self.assertEqual(
            TestCommandGenerator("post_apply"),
            specification.post_apply,
        )
        self.assertEqual(TestCommandGenerator("up"), specification.up)
        self.assertEqual(TestCommandGenerator("down"), specification.down)
