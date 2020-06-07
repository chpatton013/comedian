from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandGenerator


class LvmLogicalVolume(Specification):
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
