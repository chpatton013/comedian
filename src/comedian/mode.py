"""
Mode API for encapsulating the Generator and Command handling of different named
operational modes.
"""

import logging
import shlex
import subprocess
from abc import ABC, abstractmethod
from typing import Iterable, Optional

from comedian.action import ActionCommandHandler, ActionCommandGenerator
from comedian.command import Command, CommandContext
from comedian.traits import __Debug__, __Eq__

__all__ = ["make_mode"]


class Mode(ActionCommandHandler):
    """
    Base class for all objects that will handle Generators and Commands.
    """
    pass


def make_mode(name: str) -> Mode:
    """
    Instantiate the appropriate Mode based on the specified name.
    """
    if name == "exec":
        return ExecMode()
    elif name == "dryrun":
        return DryrunMode()
    elif name == "shell":
        return ShellMode()
    else:
        raise ValueError(f"Unknown mode '{name}'")


class ExecMode(Mode):
    """
    Object encapsulating the handlers for the "exec" mode.
    """
    def on_begin(self, context: CommandContext):
        pass

    def on_generator(context: CommandContext, self, generator: ActionCommandGenerator):
        logging.info("%s", generator)

    def on_command(self, context: CommandContext, command: Command):
        logging.info("%s", command)
        if command.capture:
            result = subprocess.check_output(
                _shlex_join(command.cmd),
                env=context.env.copy(),
                shell=True,
            )
            context.env[command.capture] = result.decode()
        else:
            subprocess.check_call(
                _shlex_join(command.cmd),
                env=context.env,
                shell=True,
            )

    def on_end(self, context: CommandContext):
        pass


class DryrunMode(Mode):
    """
    Object encapsulating the handlers for the "dryrun" mode.
    """
    def on_begin(self, context: CommandContext):
        pass

    def on_generator(self, context: CommandContext, generator: ActionCommandGenerator):
        logging.info("%s", generator)

    def on_command(self, context: CommandContext, command: Command):
        logging.info("%s", command)

    def on_end(self, context: CommandContext):
        pass


class ShellMode(Mode):
    """
    Object encapsulating the handlers for the "shell" mode.
    """
    def on_begin(self, context: CommandContext):
        print("#!/usr/bin/bash")
        print("set -xeuo pipefail")

    def on_generator(self, context: CommandContext, generator: ActionCommandGenerator):
        logging.info("%s", generator)
        print()
        print("#", generator)

    def on_command(self, context: CommandContext, command: Command):
        logging.info("%s", command)
        cmd_str = _shlex_join(command.cmd)
        if command.capture:
            print(f"{command.capture}=\"$({cmd_str})\"")
        else:
            print(cmd_str)

    def on_end(self, context: CommandContext):
        pass


def _shlex_join(args: Iterable[str]) -> str:
    return " ".join([arg if "$" in arg else shlex.quote(arg) for arg in args])
