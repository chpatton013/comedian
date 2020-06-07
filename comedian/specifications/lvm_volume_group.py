from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandGenerator


class LvmVolumeGroup(Specification):
    def __init__(
        self,
        name: str,
        lvm_physical_volumes: List[str],
    ):
        super().__init__(name, lvm_physical_volumes)
        self.lvm_physical_volumes = lvm_physical_volumes
