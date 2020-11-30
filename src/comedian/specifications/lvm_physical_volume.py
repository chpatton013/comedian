from typing import Iterator

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


class LvmPhysicalVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmPhysicalVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)

        yield Command(["pvcreate", quote_argument(device_path)])


class LvmPhysicalVolume(Specification):
    def __init__(self, name: str, device: str):
        super().__init__(
            name,
            [device],
            apply=LvmPhysicalVolumeApplyCommandGenerator(self),
        )
        self.device = device

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)
