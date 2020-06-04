from typing import Iterator, List

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class LvmLogicalVolume(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        lvm_volume_group: str,
        size: str,
        args: List[str],
    ):
        super().__init__(name, [lvm_volume_group])
        self.lvm_volume_group = lvm_volume_group
        self.size = size
        self.args = args

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
