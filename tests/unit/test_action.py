import unittest
from unittest.mock import MagicMock, call
from typing import Any, Iterable, Iterator, Mapping

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
from comedian.traits import __Debug__, __Eq__


class TestActionCommandGenerator(ActionCommandGenerator, __Debug__, __Eq__):
    def __init__(self, name: str, **kwargs: Mapping[str, Any]):
        super().__init__(**kwargs)
        self.name = name

    def __fields__(self) -> Iterator[str]:
        yield "name"


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

        self.generators = [
            TestActionCommandGenerator(
                "gen_1",
                apply=TestCommandGenerator(
                    [
                        Command(["apply_1"]),
                        Command(["apply_2"]),
                    ]
                ),
                post_apply=TestCommandGenerator(
                    [
                        Command(["post_apply_1"]),
                        Command(["post_apply_2"]),
                    ]
                ),
                up=TestCommandGenerator(
                    [
                        Command(["up_1"]),
                        Command(["up_2"]),
                    ]
                ),
                pre_down=TestCommandGenerator(
                    [
                        Command(["pre_down_1"]),
                        Command(["pre_down_2"]),
                    ]
                ),
                down=TestCommandGenerator(
                    [
                        Command(["down_1"]),
                        Command(["down_2"]),
                    ]
                ),
            ),
            TestActionCommandGenerator(
                "gen_2",
                apply=TestCommandGenerator(
                    [
                        Command(["apply_3"]),
                        Command(["apply_4"]),
                    ]
                ),
                post_apply=TestCommandGenerator(
                    [
                        Command(["post_apply_3"]),
                        Command(["post_apply_4"]),
                    ]
                ),
                up=TestCommandGenerator(
                    [
                        Command(["up_3"]),
                        Command(["up_4"]),
                    ]
                ),
                pre_down=TestCommandGenerator(
                    [
                        Command(["pre_down_3"]),
                        Command(["pre_down_4"]),
                    ]
                ),
                down=TestCommandGenerator(
                    [
                        Command(["down_3"]),
                        Command(["down_4"]),
                    ]
                ),
            ),
        ]

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

    def test_non_empty_generator(self):
        self.assertListEqual(
            [Command(["apply_1"]), Command(["apply_2"])],
            list(self.generators[0].generate_apply_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["post_apply_1"]), Command(["post_apply_2"])],
            list(self.generators[0].generate_post_apply_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["up_1"]), Command(["up_2"])],
            list(self.generators[0].generate_up_commands(self.context)),
        )
        self.assertListEqual(
            [Command(["down_1"]), Command(["down_2"])],
            list(self.generators[0].generate_down_commands(self.context)),
        )

    def test_apply_commands(self):
        handler = MagicMock()

        ApplyAction(self.context)(handler, self.generators)

        handler.on_begin.assert_called_once_with(self.context)
        handler.on_generator.assert_has_calls(
            [
                call(self.context, TestActionCommandGenerator("gen_1")),
                call(self.context, TestActionCommandGenerator("gen_2")),
                call(self.context, TestActionCommandGenerator("gen_1")),
                call(self.context, TestActionCommandGenerator("gen_2")),
            ]
        )
        handler.on_command.assert_has_calls(
            [
                call(self.context, Command(["apply_1"])),
                call(self.context, Command(["apply_2"])),
                call(self.context, Command(["apply_3"])),
                call(self.context, Command(["apply_4"])),
                call(self.context, Command(["post_apply_1"])),
                call(self.context, Command(["post_apply_2"])),
                call(self.context, Command(["post_apply_3"])),
                call(self.context, Command(["post_apply_4"])),
            ]
        )
        handler.on_end.assert_called_once_with(self.context)

    def test_up_commands(self):
        handler = MagicMock()

        UpAction(self.context)(handler, self.generators)

        handler.on_begin.assert_called_once_with(self.context)
        handler.on_generator.assert_has_calls(
            [
                call(self.context, TestActionCommandGenerator("gen_1")),
                call(self.context, TestActionCommandGenerator("gen_2")),
            ]
        )
        handler.on_command.assert_has_calls(
            [
                call(self.context, Command(["up_1"])),
                call(self.context, Command(["up_2"])),
                call(self.context, Command(["up_3"])),
                call(self.context, Command(["up_4"])),
            ]
        )
        handler.on_end.assert_called_once_with(self.context)

    def test_down_commands(self):
        handler = MagicMock()

        DownAction(self.context)(handler, self.generators)

        handler.on_begin.assert_called_once_with(self.context)
        handler.on_generator.assert_has_calls(
            [
                call(self.context, TestActionCommandGenerator("gen_2")),
                call(self.context, TestActionCommandGenerator("gen_1")),
            ]
        )
        handler.on_command.assert_has_calls(
            [
                call(self.context, Command(["pre_down_3"])),
                call(self.context, Command(["pre_down_4"])),
                call(self.context, Command(["pre_down_1"])),
                call(self.context, Command(["pre_down_2"])),
                call(self.context, Command(["down_3"])),
                call(self.context, Command(["down_4"])),
                call(self.context, Command(["down_1"])),
                call(self.context, Command(["down_2"])),
            ]
        )
        handler.on_end.assert_called_once_with(self.context)

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
