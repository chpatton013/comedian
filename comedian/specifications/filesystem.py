from typing import Iterator, List

from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink
from ..specification import Specification


class FilesystemApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)
        mountpoint_path = context.config.media_path(
            context.graph.resolve_path(self.specification.mountpoint)
        )

        yield Command(["mkfs", "--type", self.specification.type] +
                      self.specification.options + [device_path])
        yield Command(_mount_fs(device_path, mountpoint_path))


class FilesystemUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_path(self.specification.device)
        mountpoint_path = context.config.media_path(
            context.graph.resolve_path(self.specification.mountpoint)
        )

        yield Command(_mount_fs(device_path, mountpoint_path))


class FilesystemDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_path(self.specification.device)

        yield Command(_umount_fs(device_path))


class Filesystem(Specification):
    def __init__(
        self,
        name: str,
        device: str,
        mountpoint: str,
        type: str,
        options: List[str],
    ):
        super().__init__(
            name,
            [device, mountpoint],
            apply=FilesystemApplyCommandGenerator(self),
            up=FilesystemUpCommandGenerator(self),
            down=FilesystemDownCommandGenerator(self),
        )
        self.device = device
        self.mountpoint = mountpoint
        self.type = type
        self.options = options

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.mountpoint, None)


def _mount_fs(device: str, mountpoint: str) -> List[str]:
    return ["mount", device, mountpoint]


def _umount_fs(device: str) -> List[str]:
    return ["umount", device]
