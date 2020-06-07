from typing import Iterator

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink


class LvmPhysicalVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmPhysicalVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)

        yield Command(["pvcreate", device_path])


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
