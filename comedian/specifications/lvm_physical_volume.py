from typing import Iterator

from .specification import Specification
from ..command import Command, CommandGenerator


class LvmPhysicalVolume(Specification):
    def __init__(self, name: str, device: str):
        super().__init__(name, [device])
        self.device = device
