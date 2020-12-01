import unittest
from unittest.mock import MagicMock, call, patch
from typing import Any, Iterable, Iterator, List

from context import comedian

from comedian import run
from comedian.command import Command
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.specification import Specification


class AnyType:
    def __eq__(self, other: Any) -> bool:
        return True


class AnyIter:
    def __init__(self, iterable: Iterable[Any]):
        self.iterator = iter(iterable)

    def __iter__(self) -> Iterator[Any]:
        return self

    def __next__(self) -> Any:
        return next(self.iterator)

    def __eq__(self, other: Any) -> bool:
        return list(self) == list(other)


class TestSpecification(Specification):
    def __init__(self, name: str, commands: List[Command]):
        super().__init__(name, [])
        self.name = name
        self.commands = commands


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

        make_mode.return_value = mode
        make_action.return_value = action

        run(config, graph, "action", "mode")

        action.assert_called_once_with(mode, AnyIter([spec1, spec2]))

        make_action.assert_called_once_with("action", AnyType())
        make_mode.assert_called_once_with("mode")
