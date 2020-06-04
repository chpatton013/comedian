from typing import Iterator, Optional

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class PhysicalDevice(CommandGenerator, Declaration):
    def __init__(self, name: str):
        super().__init__(name, [])

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
