from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandGenerator
from ..graph import ResolveLink


class LoopDevice(Specification):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(name, [file])
        self.file = file
        self.args = args

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, "/dev/{self.name}")
