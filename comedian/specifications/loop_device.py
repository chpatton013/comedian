from typing import Iterator, List

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class LoopDevice(CommandGenerator, Declaration):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(name, [file])
        self.file = file
        self.args = args

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
