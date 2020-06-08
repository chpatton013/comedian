import unittest
from unittest.mock import patch

from context import comedian

from comedian.command import Command
from comedian.mode import make_mode, ExecMode, DryrunMode, ShellMode
from comedian.specifications import Specification


class ModeTest(unittest.TestCase):
    def setUp(self):
        self.spec = Specification("spec", [])
        self.command = Command(["command"])

        logging_info = patch("comedian.mode.logging.info")
        subprocess_check_call = patch("comedian.mode.subprocess.check_call")
        print = patch("comedian.mode.print")

        self.logging_info = logging_info.start()
        self.subprocess_check_call = subprocess_check_call.start()
        self.print = print.start()

        self.addCleanup(logging_info.stop)
        self.addCleanup(subprocess_check_call.start)
        self.addCleanup(print.start)

    def test_exec_mode_on_specification(self):
        mode = ExecMode()

        mode.on_specification(self.spec)
        self.logging_info.assert_called_once_with("%s", self.spec)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_exec_mode_on_command(self):
        mode = ExecMode()

        mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_called_once_with(
            "command", shell=True
        )
        self.print.assert_not_called()

    def test_dryrun_mode_on_specification(self):
        mode = DryrunMode()

        mode.on_specification(self.spec)
        self.logging_info.assert_called_once_with("%s", self.spec)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_dryrun_mode_on_command(self):
        mode = DryrunMode()

        mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_not_called()

    def test_shell_mode_on_specification(self):
        mode = ShellMode()

        mode.on_specification(self.spec)
        self.logging_info.assert_called_once_with("%s", self.spec)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called_once_with("#", self.spec)

    def test_shell_mode_on_command(self):
        mode = ShellMode()

        mode.on_command(self.command)
        self.logging_info.assert_called_once_with("%s", self.command)
        self.subprocess_check_call.assert_not_called()
        self.print.assert_called_once_with(" ".join(self.command.cmd))

    def test_make_mode(self):
        self.assertEqual(ExecMode, make_mode("exec").__class__)
        self.assertEqual(DryrunMode, make_mode("dryrun").__class__)
        self.assertEqual(ShellMode, make_mode("shell").__class__)
