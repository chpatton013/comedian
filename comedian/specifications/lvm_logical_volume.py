from typing import List

from ..declaration import Declaration


class LvmLogicalVolume(Declaration):
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
