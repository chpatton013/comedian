import unittest
from unittest.mock import MagicMock, call, patch
from typing import Any, Iterator, List

from context import comedian

from comedian import run
from comedian.action import Action
from comedian.command import Command
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.specification import Specification


class AnyType:
    def __eq__(self, other: Any) -> bool:
        return True


class TestSpecification(Specification):
    def __init__(self, name: str, commands: List[Command]):
        super().__init__(name, [])
        self.name = name
        self.commands = commands


class TestAction(Action):
    def __call__(self, spec: TestSpecification) -> Iterator[Command]:
        yield from spec.commands


class RunTest(unittest.TestCase):
    @patch("comedian.make_action")
    @patch("comedian.make_mode")
    def test_run(self, make_mode, make_action):
        spec1 = TestSpecification("spec1", [Command(["1"]), Command(["2"])])
        spec2 = TestSpecification("spec2", [Command(["3"]), Command(["4"])])

        config = Configuration(
            shell="",
            dd_bs="",
            random_device="",
            media_dir="",
            tmp_dir="",
        )
        graph = Graph([spec1, spec2])

        mode = MagicMock()
        action = MagicMock()
        action.side_effect = TestAction()

        make_mode.return_value = mode
        make_action.return_value = action

        run(config, graph, "action", "mode")

        mode.on_begin.assert_called_once_with()
        mode.on_specification.assert_has_calls([call(spec1), call(spec2)])
        action.assert_has_calls([call(spec1), call(spec2)])
        mode.on_command.assert_has_calls([
            call(Command(["1"])),
            call(Command(["2"])),
            call(Command(["3"])),
            call(Command(["4"])),
        ])
        mode.on_end.assert_called_once_with()
        make_action.assert_called_once_with("action", AnyType())
        make_mode.assert_called_once_with("mode")
