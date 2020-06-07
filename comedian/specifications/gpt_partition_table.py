from typing import Iterator

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink


class GptPartitionTableApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "GptPartitionTable"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)
        yield Command(["parted", "--script", device_path, "mklabel", "gpt"])


class GptPartitionTable(Specification):
    def __init__(self, name: str, device: str):
        super().__init__(
            name,
            [device],
            apply=GptPartitionTableApplyCommandGenerator(self),
        )
        self.device = device

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)
