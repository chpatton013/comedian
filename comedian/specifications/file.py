from typing import Iterator, Optional

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class File(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
        size: Optional[str],
    ):
        super().__init__(name, [filesystem])
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode
        self.size = size

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
