from typing import Iterator, List

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink


class RaidVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "RaidVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_paths = [
            context.graph.resolve_device(device)
            for device in self.specification.devices
        ]

        cmd = [
            "mdadm",
            "--create",
            "--name",
            self.specification.name,
            "--level",
            self.specification.level,
            "--metadata",
            self.specification.metadata,
            "--raid-devices",
            str(len(self.specification.devices)),
            _raid_device(self.specification.name),
        ]

        yield Command(cmd + device_paths)


class RaidVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "RaidVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command([
            "mdadm",
            "--assemble",
            _raid_device(self.specification.name),
        ])


class RaidVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "RaidVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command([
            "mdadm",
            "--stop",
            _raid_device(self.specification.name),
        ])


class RaidVolume(Specification):
    def __init__(
        self,
        name: str,
        devices: List[str],
        level: str,
        metadata: str,
    ):
        super().__init__(
            name,
            devices,
            apply=RaidVolumeApplyCommandGenerator(self),
            up=RaidVolumeUpCommandGenerator(self),
            down=RaidVolumeDownCommandGenerator(self),
        )
        self.devices = devices
        self.level = level
        self.metadata = metadata

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, _raid_device(self.name))


def _raid_device(name: str) -> str:
    return f"/dev/md/{name}"
