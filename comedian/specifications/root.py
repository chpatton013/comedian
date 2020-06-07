from typing import Iterator

from .specification import Specification
from ..command import Command, CommandGenerator


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

