from typing import Iterator, List

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


class LvmVolumeGroupApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmVolumeGroup"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        lvm_physical_volume_paths = [
            context.graph.resolve_device(lvm_physical_volume)
            for lvm_physical_volume in self.specification.lvm_physical_volumes
        ]

        yield Command(
            ["vgcreate", self.specification.name]
            + [quote_argument(path) for path in lvm_physical_volume_paths]
        )


class LvmVolumeGroupUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmVolumeGroup"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command(["vgchange", "--activate", "y", self.specification.name])


class LvmVolumeGroupDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LvmVolumeGroup"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command(["vgchange", "--activate", "n", self.specification.name])


class LvmVolumeGroup(Specification):
    def __init__(
        self,
        name: str,
        lvm_physical_volumes: List[str],
    ):
        super().__init__(
            name,
            lvm_physical_volumes,
            apply=LvmVolumeGroupApplyCommandGenerator(self),
            up=LvmVolumeGroupUpCommandGenerator(self),
            down=LvmVolumeGroupDownCommandGenerator(self),
        )
        self.lvm_physical_volumes = lvm_physical_volumes

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, f"/dev/{self.name}")
