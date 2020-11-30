from typing import Iterator, List, Optional

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


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
            f"--name={self.specification.name}",
        ]
        if self.specification.size:
            cmd.append(f"--size={self.specification.size}")
        if self.specification.extents:
            cmd.append(f"--extents={self.specification.extents}")
        if self.specification.type:
            cmd.append(f"--type={self.specification.type}")
        if self.specification.lvm_poolmetadata_volume:
            cmd.append(
                f"--poolmetadata={self.specification.lvm_poolmetadata_volume}",
            )
        if self.specification.lvm_cachepool_volume:
            cmd.append(f"--cachepool={self.specification.lvm_cachepool_volume}")
        if self.specification.lvm_thinpool_volume:
            cmd.append(f"--thinpool={self.specification.lvm_thinpool_volume}")
        cmd += self.specification.args
        cmd.append(self.specification.lvm_volume_group)
        cmd += [quote_argument(path) for path in lvm_physical_volume_paths]

        yield Command(cmd)


class LvmLogicalVolume(Specification):
    def __init__(
        self,
        name: str,
        size: Optional[str],
        extents: Optional[str],
        type: Optional[str],
        args: List[str],
        lvm_volume_group: str,
        lvm_physical_volumes: List[str],
        lvm_poolmetadata_volume: Optional[str],
        lvm_cachepool_volume: Optional[str],
        lvm_thinpool_volume: Optional[str],
    ):
        dependencies = [lvm_volume_group] + lvm_physical_volumes
        if lvm_poolmetadata_volume:
            dependencies.append(lvm_poolmetadata_volume)
        if lvm_cachepool_volume:
            dependencies.append(lvm_cachepool_volume)
        if lvm_thinpool_volume:
            dependencies.append(lvm_thinpool_volume)
        super().__init__(
            name,
            dependencies,
            apply=LvmLogicalVolumeApplyCommandGenerator(self),
        )
        self.size = size
        self.extents = extents
        self.type = type
        self.args = args
        self.lvm_volume_group = lvm_volume_group
        self.lvm_physical_volumes = lvm_physical_volumes
        self.lvm_poolmetadata_volume = lvm_poolmetadata_volume
        self.lvm_cachepool_volume = lvm_cachepool_volume
        self.lvm_thinpool_volume = lvm_thinpool_volume

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.lvm_volume_group, self.name)
