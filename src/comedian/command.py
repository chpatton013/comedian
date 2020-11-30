"""
Command API for generating shell commands to be run on a system.
"""

import shlex
from abc import ABC, abstractmethod
from typing import Dict, Iterable, Iterator, List, Optional

from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.traits import __Debug__, __Eq__


class Command(__Debug__, __Eq__):
    """
    A container for the arguments of a shell command.
    """

    def __init__(self, cmd: List[str], capture: Optional[str] = None):
        self.cmd = cmd
        self.capture = capture

    def join(self) -> str:
        return " ".join(self.cmd)


class CommandContext(__Debug__):
    """
    A structure holding the arguments necessary for generating Commands.
    """

    def __init__(
        self,
        config: Configuration,
        graph: Graph,
    ):
        self.config = config
        self.graph = graph
        self.env: Dict[str, str] = dict()


class CommandGenerator(ABC):
    """
    Abstract base class for a Callable that generates a series of Commands.
    """

    @abstractmethod
    def __call__(self, context: CommandContext) -> Iterator[Command]:
        pass


def quote_argument(arg: str) -> str:
    return arg if shlex.quote(arg) == arg else f'"{arg}"'


def quote_subcommand(sub: str) -> str:
    return f"'{sub}'"


def chmod(mode: str, *paths: Iterable[str]) -> Command:
    return Command(["chmod", mode] + [quote_argument(path) for path in paths])


def chown(
    owner: Optional[str],
    group: Optional[str],
    *paths: Iterable[str],
) -> Command:
    own = ""
    if owner:
        own += owner
    if group:
        own += f":{group}"
    return Command(["chown", own] + [quote_argument(path) for path in paths])


def mkdir(*paths: Iterable[str]) -> Command:
    return Command(["mkdir", "--parents"] + [quote_argument(path) for path in paths])


def parted(*args: Iterable[str], align: Optional[str] = None) -> Command:
    cmd = ["parted", "--script"]
    if align:
        cmd.append(f"--align={align}")
    cmd.append("--")
    return Command(cmd + list(args))
