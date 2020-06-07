from typing import Iterator, List, Optional

from .specification import Specification
from ..command import Command, CommandGenerator
from ..graph import ResolveLink


class GptPartition(Specification):
    def __init__(
        self,
        name: str,
        partition_table: str,
        number: int,
        type: str,
        start: str,
        end: str,
        label: Optional[str],
        unit: Optional[str],
        flags: List[str],
    ):
        super().__init__(name, [partition_table])
        self.partition_table = partition_table
        self.number = number
        self.type = type
        self.start = start
        self.end = end
        self.label = label
        self.unit = unit
        self.flags = flags

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(
            self.partition_table, str(self.number), lambda x, y: x + y
        )
