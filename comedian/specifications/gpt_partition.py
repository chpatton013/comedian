from typing import Iterable, Iterator, List, Optional

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink


class GptPartitionApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "GptPartition"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        partition_table_path = context.graph.resolve_device(
            self.specification.partition_table
        )

        cmd = [
            partition_table_path,
            "mkpart",
            self.specification.type,
            self.specification.start,
            self.specification.end,
        ]
        if self.specification.label:
            cmd += ["name", self.specification.number, self.specification.label]
        if self.specification.unit:
            cmd += ["unit", self.specification.unit]
        for flag in self.specification.flags:
            cmd += ["set", self.specification.number, flag, "on"]

        yield Command(_parted(*cmd))


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
        super().__init__(
            name,
            [partition_table],
            apply=GptPartitionApplyCommandGenerator(self),
        )
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


def _parted(*args: Iterable[str]) -> List[str]:
    return ["parted", "--script", "--align=optimal", "--"] + list(args)
