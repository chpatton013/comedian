from typing import Iterator, Optional, Tuple

from .specification import Specification
from ..command import Command, CommandGenerator


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

    def resolve(self) -> Tuple[Optional[str], Optional[str]]:
        return None, "/"
