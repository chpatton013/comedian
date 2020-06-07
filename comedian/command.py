"""
Command API for generating shell commands to be run on a system.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, List, Optional

from .configuration import Configuration
from .graph import Graph
from .traits import __Debug__, __Eq__


class Command(__Debug__, __Eq__):
    """
    A container for the arguments and CWD of a shell command.
    """
    def __init__(self, cmd: List[str], cwd: str = None):
        self.cmd = cmd
        self.cwd = cwd


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


class CommandGenerator(ABC):
    """
    Abstract base class for a Callable that generates a series of Commands.
    """
    @abstractmethod
    def __call__(self, context: CommandContext) -> Iterator[Command]:
        pass


def chmod(mode: str, *paths: Iterable[str]) -> Command:
    return Command(["chmod", mode] + list(paths))


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
    return Command(["chown", own] + list(paths))


def mkdir(*paths: Iterable[str]) -> Command:
    return Command(["mkdir", "--parents"] + list(paths))
