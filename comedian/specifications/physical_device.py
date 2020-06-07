from typing import Iterator, Optional

from .specification import Specification
from ..command import Command, CommandGenerator


class PhysicalDevice(Specification):
    def __init__(self, name: str):
        super().__init__(name, [])
