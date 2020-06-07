from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandGenerator


class RaidVolume(Specification):
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
