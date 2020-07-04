from typing import Iterator, Optional

from comedian.command import Command, CommandContext, CommandGenerator, parted
from comedian.graph import ResolveLink
from comedian.specification import Specification


class GptPartitionTableApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "GptPartitionTable"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)
        yield parted(device_path, "mklabel", "gpt")


class GptPartitionTable(Specification):
    def __init__(self, name: str, device: str, glue: Optional[str]):
        super().__init__(
            name,
            [device],
            apply=GptPartitionTableApplyCommandGenerator(self),
        )
        self.device = device
        self.glue = glue

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None, lambda x, y: self._join(x, y))

    def _join(self, partition_table: str, partition_number: str) -> str:
        glue = self.glue if self.glue else ""
        return f"{partition_table}{glue}{partition_number}"
