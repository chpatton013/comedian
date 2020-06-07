from typing import Iterator, Optional, Tuple

from .specification import Specification
from ..command import Command, CommandGenerator


class Directory(Specification):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
    ):
        super().__init__(name, [filesystem])
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode

    def resolve(self) -> Tuple[Optional[str], Optional[str]]:
        return self.filesystem, self.relative_path