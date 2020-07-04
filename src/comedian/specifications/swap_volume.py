from typing import Iterator, Optional

from comedian.command import Command, CommandContext, CommandGenerator
from comedian.specification import Specification


class SwapVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(context, self.specification.device)

        cmd = ["mkswap", device_path]
        if self.specification.label:
            cmd.append(f"--label={self.specification.label}")
        if self.specification.pagesize:
            cmd.append(f"--pagesize={self.specification.pagesize}")
        if self.specification.uuid:
            cmd.append(f"--uuid={self.specification.uuid}")

        yield Command(cmd)


class SwapVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(context, self.specification.device)
        yield Command(["swapon", device_path])


class SwapVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(context, self.specification.device)
        yield Command(["swapoff", device_path])


class SwapVolume(Specification):
    def __init__(
        self,
        name: str,
        device: str,
        label: Optional[str],
        pagesize: Optional[str],
        uuid: Optional[str],
    ):
        super().__init__(
            name,
            [device],
            apply=SwapVolumeApplyCommandGenerator(self),
            up=SwapVolumeUpCommandGenerator(self),
            down=SwapVolumeDownCommandGenerator(self),
        )
        self.device = device
        self.label = label
        self.pagesize = pagesize
        self.uuid = uuid


def _device_path(context: CommandContext, device: str) -> Optional[str]:
    device_path = context.graph.resolve_device(device)
    if not device_path:
        device_path = context.config.media_path(
            context.graph.resolve_path(device)
        )
    return device_path
