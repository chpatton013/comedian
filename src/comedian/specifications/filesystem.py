from typing import Iterable, Iterator, List

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


class FilesystemApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        yield Command(
            _mkfs(
                device_path,
                self.specification.type,
                self.specification.options,
            )
        )
        yield Command(_mount_fs(device_path, media_mountpoint_path))


class FilesystemUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        yield Command(_mount_fs(device_path, media_mountpoint_path))


class FilesystemDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        yield Command(_umount_fs(media_mountpoint_path))


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


def _mkfs(device: str, type: str, options: Iterable[str]) -> List[str]:
    return ["mkfs", "--type", type] + list(options) + [quote_argument(device)]


def _mount_fs(device: str, mountpoint: str) -> List[str]:
    return ["mount", quote_argument(device), quote_argument(mountpoint)]


def _umount_fs(device: str) -> List[str]:
    return ["umount", quote_argument(device)]


def _device_path(device: str, context: CommandContext) -> str:
    device_path = context.graph.resolve_device(device)
    if not device_path:
        raise ValueError("Failed to find device path {}".format(device))
    return device_path


def _mountpoint_path(mountpoint: str, context: CommandContext) -> str:
    mountpoint_path = context.graph.resolve_path(mountpoint)
    if not mountpoint_path:
        raise ValueError("Failed to find mountpoint path {}".format(mountpoint))
    return mountpoint_path
