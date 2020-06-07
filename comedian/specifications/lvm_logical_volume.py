from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink


class LvmLogicalVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmLogicalVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        lvm_physical_volume_paths = [
            context.graph.resolve_device(lvm_physical_volume)
            for lvm_physical_volume in self.specification.lvm_physical_volumes
        ]

        cmd = [
            "lvcreate",
            "--name",
            self.specification.name,
            "--size",
            self.specification.size,
        ]
        cmd += self.specification.args
        cmd.append(self.specification.lvm_volume_group)
        cmd += lvm_physical_volume_paths

        yield Command(cmd)


class LvmLogicalVolume(Specification):
    def __init__(
        self,
        name: str,
        lvm_volume_group: str,
        size: str,
        lvm_physical_volumes: List[str],
        args: List[str],
    ):
        super().__init__(
            name,
            [lvm_volume_group] + lvm_physical_volumes,
            apply=LvmLogicalVolumeApplyCommandGenerator(self),
        )
        self.lvm_volume_group = lvm_volume_group
        self.size = size
        self.lvm_physical_volumes = lvm_physical_volumes
        self.args = args

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.lvm_volume_group, self.name)
