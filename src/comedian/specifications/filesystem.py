from typing import Iterator, List

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


class FilesystemApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)

        yield Command(
            ["mkfs", "--type", self.specification.type]
            + list(self.specification.options)
            + [quote_argument(device_path)]
        )


class Filesystem(Specification):
    def __init__(
        self,
        name: str,
        device: str,
        type: str,
        options: List[str],
    ):
        super().__init__(
            name,
            [device],
            apply=FilesystemApplyCommandGenerator(self),
        )
        self.device = device
        self.type = type
        self.options = options

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, None)


def _device_path(device: str, context: CommandContext) -> str:
    device_path = context.graph.resolve_device(device)
    if not device_path:
        raise ValueError("Failed to find device path {}".format(device))
    return device_path
