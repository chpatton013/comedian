from typing import Iterator, List

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class RaidVolume(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        devices: List[str],
        level: str,
        metadata: str,
    ):
        super().__init__(name, devices)
        self.devices = devices
        self.level = level
        self.metadata = metadata

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
