from typing import List

from ..declaration import Declaration


class Filesystem(Declaration):
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
