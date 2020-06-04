from abc import ABC, abstractmethod
from typing import Iterator

from .traits import __Debug__, __Eq__


class Command(__Debug__, __Eq__):
    def __init__(self, cmd: str, cwd: str = None):
        self.cmd = cmd
        self.cwd = cwd


class CommandGenerator(ABC):
    @abstractmethod
    def generate_commands(self) -> Iterator[Command]:
        pass
