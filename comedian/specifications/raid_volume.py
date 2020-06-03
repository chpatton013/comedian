from typing import List

from ..declaration import Declaration


class RaidVolume(Declaration):
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
