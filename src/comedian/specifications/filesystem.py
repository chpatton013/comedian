from typing import Iterator, List, Optional

from comedian.command import Command, CommandContext, CommandGenerator, quote_argument
from comedian.graph import ResolveLink
from comedian.specification import Specification


class FilesystemApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        mount_cmd = ["mount", "--types", self.specification.type]
        if self.specification.mount_options:
            mount_cmd += ["-o", ",".join(self.specification.mount_options)]

        if self.specification.device:
            device_path = _device_path(self.specification.device, context)
            mount_cmd.append(quote_argument(device_path))

            yield Command(
                ["mkfs", "--type", self.specification.type]
                + list(self.specification.options)
                + [quote_argument(device_path)]
            )

        mount_cmd.append(quote_argument(media_mountpoint_path))
        yield Command(mount_cmd)


class FilesystemUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        mount_cmd = ["mount", "--types", self.specification.type]
        if self.specification.mount_options:
            mount_cmd += ["-o", ",".join(self.specification.mount_options)]

        if self.specification.device:
            device_path = _device_path(self.specification.device, context)
            mount_cmd.append(quote_argument(device_path))

        mount_cmd.append(quote_argument(media_mountpoint_path))
        yield Command(mount_cmd)


class FilesystemDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Filesystem"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        yield Command(["umount", quote_argument(media_mountpoint_path)])


class Filesystem(Specification):
    def __init__(
        self,
        name: str,
        device: Optional[str],
        mountpoint: str,
        type: str,
        options: List[str],
        mount_options: List[str],
        dump_frequency: Optional[int],
        fsck_order: Optional[int],
    ):
        dependencies = [mountpoint]
        if device:
            dependencies.append(device)
        super().__init__(
            name,
            dependencies,
            apply=FilesystemApplyCommandGenerator(self),
            up=FilesystemUpCommandGenerator(self),
            down=FilesystemDownCommandGenerator(self),
        )
        self.device = device
        self.mountpoint = mountpoint
        self.type = type
        self.options = options
        self.mount_options = mount_options
        self.dump_frequency = dump_frequency
        self.fsck_order = fsck_order

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.mountpoint, None)


def _mount_fs(device: str, mountpoint: str) -> List[str]:
    return ["mount", quote_argument(device), quote_argument(mountpoint)]


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
