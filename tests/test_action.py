import unittest
from typing import Iterable, Iterator

from context import comedian

from comedian.action import (
    ActionCommandGenerator,
    ApplyAction,
    DownAction,
    UpAction,
    make_action,
)
from comedian.command import Command, CommandContext, CommandGenerator
from comedian.configuration import Configuration
from comedian.graph import Graph


class TestCommandGenerator(CommandGenerator):
    def __init__(self, commands: Iterable[Command]):
        self.commands = commands

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield from self.commands


class ActionTest(unittest.TestCase):
    def setUp(self):
        configuration = Configuration(
            shell="shell",
            dd_bs="dd_bs",
            random_device="random_device",
            media_dir="media_dir",
            tmp_dir="tmp_dir",
        )
        graph = Graph([])
        self.context = CommandContext(configuration, graph)

        self.generator = ActionCommandGenerator(
            apply=TestCommandGenerator([Command(["apply"])]),
            post_apply=TestCommandGenerator([Command(["post_apply"])]),
            up=TestCommandGenerator([Command(["up"])]),
            down=TestCommandGenerator([Command(["down"])]),
        )

    def test_empty_generator(self):
        generator = ActionCommandGenerator()
        with self.assertRaises(StopIteration):
            next(generator.generate_apply_commands(self.context))
        with self.assertRaises(StopIteration):
            next(generator.generate_post_apply_commands(self.context))
        with self.assertRaises(StopIteration):
            next(generator.generate_up_commands(self.context))
        with self.assertRaises(StopIteration):
            next(generator.generate_down_commands(self.context))

    def test_full_generator(self):
        self.assertListEqual(
            [Command(["apply"])],
            list(self.generator.generate_apply_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["post_apply"])],
            list(self.generator.generate_post_apply_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["up"])],
            list(self.generator.generate_up_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["down"])],
            list(self.generator.generate_down_commands(self.context)),
        )

    def test_apply_commands(self):
        self.assertListEqual(
            [Command(["apply"]), Command(["post_apply"])],
            list(ApplyAction(self.context)(self.generator)),
        )

    def test_up_commands(self):
        self.assertListEqual(
            [Command(["up"])],
            list(UpAction(self.context)(self.generator)),
        )

    def test_down_commands(self):
        self.assertListEqual(
            [Command(["down"])],
            list(DownAction(self.context)(self.generator)),
        )

    def test_make_action(self):
        self.assertEqual(
            ApplyAction,
            make_action("apply", self.context).__class__,
        )
        self.assertEqual(
            UpAction,
            make_action("up", self.context).__class__,
        )
        self.assertEqual(
            DownAction,
            make_action("down", self.context).__class__,
        )
