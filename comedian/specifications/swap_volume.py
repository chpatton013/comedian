from typing import Iterator

from .specification import Specification
from ..command import Command, CommandContext, CommandGenerator


class SwapVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_path(self.specification.device)

        yield Command(["mkswap", device_path])


class SwapVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_path(self.specification.device)

        yield Command(["swapon", device_path])


class SwapVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "SwapVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_path(self.specification.device)

        yield Command(["swapoff", device_path])


class SwapVolume(Specification):
    def __init__(self, name: str, device: str):
        super().__init__(
            name,
            [device],
            apply=SwapVolumeApplyCommandGenerator(self),
            up=SwapVolumeUpCommandGenerator(self),
            down=SwapVolumeDownCommandGenerator(self),
        )
        self.device = device
