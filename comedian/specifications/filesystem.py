from typing import Iterator, List

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class Filesystem(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        device: str,
        mountpoint: str,
        type: str,
        options: List[str],
    ):
        super().__init__(name, [device, mountpoint])
        self.device = device
        self.mountpoint = mountpoint
        self.type = type
        self.options = options

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
