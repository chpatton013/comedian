from typing import Iterator, Optional

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    parted,
    quote_argument,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class PartitionTableApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "PartitionTable"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)
        if not device_path:
            raise ValueError(
                "Failed to find device path {}".format(self.specification.device)
            )
        yield parted(quote_argument(device_path), "mklabel", self.specification.type)


class PartitionTable(Specification):
    def __init__(self, name: str, device: str, type: str, glue: Optional[str]):
        super().__init__(
            name,
            [device],
            apply=PartitionTableApplyCommandGenerator(self),
        )
        self.device = device
        self.type = type
        self.glue = glue

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None, self._join)

    def _join(self, partition_table: str, partition_number: str) -> str:
        glue = self.glue if self.glue else ""
        return f"{partition_table}{glue}{partition_number}"
