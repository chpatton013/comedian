from typing import Iterator, Optional

from comedian.command import Command, CommandGenerator
from comedian.graph import ResolveLink
from comedian.specification import Specification


class PhysicalDevice(Specification):
    def __init__(self, name: str):
        super().__init__(name, [])

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, f"/dev/{self.name}")
