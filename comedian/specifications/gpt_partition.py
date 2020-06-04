from typing import Iterator, List

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class GptPartition(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        partition_table: str,
        number: int,
        start: str,
        end: str,
        flags: List[str],
    ):
        super().__init__(name, [partition_table])
        self.partition_table = partition_table
        self.number = number
        self.start = start
        self.end = end
        self.flags = flags

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
