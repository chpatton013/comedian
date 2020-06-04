from typing import Iterator

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class GptPartitionTable(CommandGenerator, Declaration):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
        self.device = device

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
