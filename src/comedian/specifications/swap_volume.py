from typing import Iterator, Optional

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    quote_argument,
    fstab_append,
)
from comedian.specification import Specification


class SwapVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        yield Command(["swapon", quote_argument(device_path)])


class SwapVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        yield Command(["swapoff", quote_argument(device_path)])


class SwapVolumeApplyCommandGenerator(SwapVolumeUpCommandGenerator):
    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)

        cmd = ["mkswap", quote_argument(device_path)]
        if self.specification.label:
            cmd.append(f"--label={self.specification.label}")
        if self.specification.pagesize:
            cmd.append(f"--pagesize={self.specification.pagesize}")
        if self.specification.uuid:
            cmd.append(f"--uuid={self.specification.uuid}")
        yield Command(cmd)

        yield from super().__call__(context)

        fstab_entry = [
            "",
            f"# {self.specification.name}",
            "\\t".join([device_path, "none", "swap", "defaults", "0", "0"]),
        ]
        yield fstab_append(context, "\\n".join(fstab_entry))


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


def _device_path(device: str, context: CommandContext) -> str:
    device_path = context.graph.resolve_device(device)
    if device_path:
        return device_path
    device_path = context.graph.resolve_path(device)
    if not device_path:
        raise ValueError("Failed to find device path {}".format(device))
    return context.config.media_path(device_path)
