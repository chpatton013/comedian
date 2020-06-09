"""
Mode API for encapsulating the Specification and Command handling of different
named operational modes.
"""

import logging
import shlex
import subprocess
from abc import ABC, abstractmethod
from typing import Iterable

from .command import Command
from .specification import Specification

__all__ = ("make_mode")


class Mode(ABC):
    """
    Base class for all objects that will handle Specifications and Commands.
    """
    @abstractmethod
    def on_specification(spec: Specification):
        pass

    @abstractmethod
    def on_command(command: Command):
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
    def on_specification(self, spec: Specification):
        logging.info("%s", spec)

    def on_command(self, command: Command):
        logging.info("%s", command)
        subprocess.check_call(_shlex_join(command.cmd), shell=True)


class DryrunMode(Mode):
    """
    Object encapsulating the handlers for the "dryrun" mode.
    """
    def on_specification(self, spec: Specification):
        logging.info("%s", spec)

    def on_command(self, command: Command):
        logging.info("%s", command)


class ShellMode(Mode):
    """
    Object encapsulating the handlers for the "shell" mode.
    """
    def on_specification(self, spec: Specification):
        logging.info("%s", spec)
        print("#", spec)

    def on_command(self, command: Command):
        logging.info("%s", command)
        print(_shlex_join(command.cmd))


def _shlex_join(args: Iterable[str]) -> str:
    return " ".join([shlex.quote(arg) for arg in args])
