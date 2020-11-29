import unittest
from unittest.mock import patch

from context import comedian

from comedian.action import ActionCommandGenerator
from comedian.command import Command, CommandContext
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.mode import DryrunMode, ExecMode, ShellMode, make_mode


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
        self.configuration = Configuration(
            shell="shell",
            dd_bs="dd_bs",
            random_device="random_device",
            media_dir="media_dir",
            tmp_dir="tmp_dir",
        )
        self.graph = Graph([])
        self.generator = TestActionCommandGenerator("gen")
        self.command = Command(["command"])
        self.capture_command = Command(["command"], capture="capture")
        self.mock_print = MockPrint()

        logging_info = patch("comedian.mode.logging.info")
        subprocess_check_call = patch("comedian.mode.subprocess.check_call")
        subprocess_check_output = patch("comedian.mode.subprocess.check_output")
        print = patch("comedian.mode.print")

        self.logging_info = logging_info.start()
        self.subprocess_check_call = subprocess_check_call.start()
        self.subprocess_check_output = subprocess_check_output.start()
        self.print = print.start()

        self.print.side_effect = self.mock_print

        self.addCleanup(logging_info.stop)
        self.addCleanup(subprocess_check_call.stop)
        self.addCleanup(subprocess_check_output.stop)
        self.addCleanup(print.stop)


class ExecModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ExecMode()

    def test_on_begin(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_begin(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_generator(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_generator(context, self.generator)

        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_command(context, self.command)

        self.assertDictEqual(context.env, {})
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_called_once_with(
            "command", env={}, shell=True
        )
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_capture_command(self):
        context = CommandContext(self.configuration, self.graph)
        context.env["foo"] = "bar"
        self.subprocess_check_output.return_value = b"result"

        self.mode.on_command(context, self.capture_command)

        self.assertDictEqual(context.env, {"foo": "bar", "capture": "result"})
        self.logging_info.assert_called_once_with("%s", self.capture_command)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_called_once_with(
            "command", env={"foo": "bar"}, shell=True
        )
        self.print.assert_not_called()

    def test_on_end(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_end(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()


class DryrunModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = DryrunMode()

    def test_on_begin(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_begin(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_generator(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_generator(context, self.generator)

        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_command(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_command(context, self.command)

        self.assertDictEqual(context.env, {})
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_capture_command(self):
        context = CommandContext(self.configuration, self.graph)
        context.env["foo"] = "bar"

        self.mode.on_command(context, self.capture_command)

        self.assertDictEqual(context.env, {"foo": "bar"})
        self.logging_info.assert_called_once_with("%s", self.capture_command)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()

    def test_on_end(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_end(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()


class ShellModeTest(ModeTest):
    def setUp(self):
        super().setUp()
        self.mode = ShellMode()

    def test_on_begin(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_begin(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"#!/usr/bin/bash\nset -xeuo pipefail\n",
            self.print.side_effect.buffer,
        )

    def test_on_generator(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_generator(context, self.generator)

        self.logging_info.assert_called_once_with("%s", self.generator)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_called()
        self.assertEqual(
            f"\n# {self.generator}\n",
            self.print.side_effect.buffer,
        )

    def test_on_command(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_command(context, self.command)

        self.assertDictEqual(context.env, {})
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_called_once_with(" ".join(self.command.cmd))

    def test_on_capture_command(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_command(context, self.capture_command)

        self.assertDictEqual(context.env, {})
        self.logging_info.assert_called_once_with("%s", self.capture_command)
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_called_once_with(
            '{}="$({})"'.format(
                self.capture_command.capture,
                " ".join(self.capture_command.cmd),
            )
        )

    def test_on_end(self):
        context = CommandContext(self.configuration, self.graph)

        self.mode.on_end(context)

        self.logging_info.assert_not_called()
        self.subprocess_check_call.assert_not_called()
        self.subprocess_check_output.assert_not_called()
        self.print.assert_not_called()


class MakeModeTest(unittest.TestCase):
    def test_make_mode(self):
        self.assertEqual(ExecMode, make_mode("exec").__class__)
        self.assertEqual(DryrunMode, make_mode("dryrun").__class__)
        self.assertEqual(ShellMode, make_mode("shell").__class__)
