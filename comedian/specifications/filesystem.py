from typing import Iterator, List, Optional, Tuple

from .specification import Specification
from ..command import Command, CommandGenerator


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

    def resolve(self) -> Tuple[Optional[str], Optional[str]]:
        return self.mountpoint, None
