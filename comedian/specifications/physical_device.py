from typing import Iterator, Optional

from .specification import Specification
from ..command import Command, CommandGenerator
from ..graph import ResolveLink


class PhysicalDevice(Specification):
    def __init__(self, name: str):
        super().__init__(name, [])

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, f"/dev/{self.name}")
