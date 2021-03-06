from typing import Iterator, List, Optional

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    fstab_append,
    identify_device_path,
    quote_argument,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class MountUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Mount"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mount_cmd = ["mount"]
        if self.specification.type:
            mount_cmd += ["--types", quote_argument(self.specification.type)]
        if self.specification.options:
            mount_cmd += ["-o", quote_argument(",".join(self.specification.options))]

        if self.specification.device:
            device_path = _device_path(self.specification.device, context)
            mount_cmd.append(quote_argument(device_path))
        else:
            mount_cmd.append(quote_argument(self.specification.type))

        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)
        mount_cmd.append(quote_argument(media_mountpoint_path))

        yield Command(mount_cmd)


class MountDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Mount"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)
        media_mountpoint_path = context.config.media_path(mountpoint_path)

        yield Command(["umount", quote_argument(media_mountpoint_path)])


class MountApplyCommandGenerator(MountUpCommandGenerator):
    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield from super().__call__(context)

        identify_path = None
        if self.specification.device:
            device_path = _device_path(self.specification.device, context)
            command = f"# {self.specification.name} (originally {device_path})"
            identify_path = identify_device_path(
                self.specification.identify, device_path
            )
        else:
            command = f"# {self.specification.name}"
            identify_path = self.specification.type
        mountpoint_path = _mountpoint_path(self.specification.mountpoint, context)

        fstab_entry = [
            "",
            command,
            "\\t".join(
                [
                    quote_argument(identify_path),
                    quote_argument(mountpoint_path),
                    quote_argument(self.specification.type),
                    quote_argument(",".join(self.specification.options)),
                    str(self.specification.dump_frequency or 0),
                    str(self.specification.fsck_order or 0),
                ]
            ),
        ]
        yield fstab_append(context, "\\n".join(fstab_entry))


class Mount(Specification):
    def __init__(
        self,
        name: str,
        device: Optional[str],
        identify: str,
        mountpoint: str,
        type: str,
        options: List[str],
        dump_frequency: Optional[int],
        fsck_order: Optional[int],
    ):
        dependencies = [mountpoint]
        if device:
            dependencies.append(device)
        super().__init__(
            name,
            dependencies,
            apply=MountApplyCommandGenerator(self),
            up=MountUpCommandGenerator(self),
            down=MountDownCommandGenerator(self),
        )
        self.device = device
        self.identify = identify
        self.mountpoint = mountpoint
        self.type = type
        self.options = options
        self.dump_frequency = dump_frequency
        self.fsck_order = fsck_order

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(self.device, None)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.mountpoint, None)


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
