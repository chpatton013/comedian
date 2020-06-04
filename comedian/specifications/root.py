from typing import Iterator

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class Root(CommandGenerator, Declaration):
    def __init__(self):
        super().__init__("/", [])

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
