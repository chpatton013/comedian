import unittest
from unittest.mock import patch

from context import comedian

from comedian.action import ActionCommandGenerator
from comedian.command import Command
from comedian.mode import make_mode, ExecMode, DryrunMode, ShellMode


class MockPrint:
    def __init__(self):
        self.buffer = ""

    def __call__(self, *args):
        self.buffer += " ".join([str(arg) for arg in args])
        self.buffer += "\n"


class TestActionCommandGenerator(ActionCommandGenerator):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class ModeTest(unittest.TestCase):
    def setUp(self):
        self.generator = TestActionCommandGenerator("gen")
        self.command = Command(["command"])
        self.mock_print = MockPrint()

        logging_info = patch("comedian.mode.logging.info")
        subprocess_check_call = patch("comedian.mode.subprocess.check_call")
        print = patch("comedian.mode.print")

        self.logging_info = logging_info.start()
        self.subprocess_check_call = subprocess_check_call.start()
        self.print = print.start()

        self.print.side_effect = self.mock_print

        self.addCleanup(logging_info.stop)
        self.addCleanup(subprocess_check_call.stop)
        self.addCleanup(print.stop)


class ExecModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ExecMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_generator(self):
        self.mode.on_generator(self.generator)
        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        self.mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_called_once_with(
            "command", shell=True
        )
        self.print.assert_not_called()

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class DryrunModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = DryrunMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_generator(self):
        self.mode.on_generator(self.generator)
        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        self.mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class ShellModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ShellMode()

    def test_on_begin(self):
        self.mode.on_begin()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"#!/usr/bin/bash\nset -xeuo pipefail\n",
            self.print.side_effect.buffer,
        )

    def test_on_generator(self):
        self.mode.on_generator(self.generator)
        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"\n# {self.generator}\n",
            self.print.side_effect.buffer,
        )

    def test_on_command(self):
        self.mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called_once_with(" ".join(self.command.cmd))

    def test_on_end(self):
        self.mode.on_end()
        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()


class MakeModeTest(unittest.TestCase):
    def test_make_mode(self):
        self.assertEqual(ExecMode, make_mode("exec").__class__)
        self.assertEqual(DryrunMode, make_mode("dryrun").__class__)
        self.assertEqual(ShellMode, make_mode("shell").__class__)
