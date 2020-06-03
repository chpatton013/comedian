from typing import List

from ..declaration import Declaration


class LvmVolumeGroup(Declaration):
    def __init__(
        self,
        name: str,
        lvm_physical_volumes: List[str],
    ):
        super().__init__(name, lvm_physical_volumes)
        self.lvm_physical_volumes = lvm_physical_volumes
