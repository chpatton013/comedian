from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandGenerator
from ..graph import ResolveLink


class Filesystem(Specification):
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

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.mountpoint, None)
