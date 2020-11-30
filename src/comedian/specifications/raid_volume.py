from typing import Iterator, List

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


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
            f"--name={self.specification.name}",
            f"--level={self.specification.level}",
            f"--metadata={self.specification.metadata}",
            f"--raid-devices={len(self.specification.devices)}",
            quote_argument(_raid_device(self.specification.name)),
        ]

        yield Command(cmd + [quote_argument(path) for path in device_paths])


class RaidVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "RaidVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_paths = [
            context.graph.resolve_device(device)
            for device in self.specification.devices
        ]

        cmd = [
            "mdadm",
            "--assemble",
            quote_argument(_raid_device(self.specification.name)),
        ]

        yield Command(cmd + [quote_argument(path) for path in device_paths])


class RaidVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "RaidVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command(
            [
                "mdadm",
                "--stop",
                quote_argument(_raid_device(self.specification.name)),
            ]
        )


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
