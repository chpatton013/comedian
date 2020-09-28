import shlex
from typing import Iterator, List

from comedian.command import Command, CommandContext, CommandGenerator
from comedian.graph import ResolveLink
from comedian.specification import Specification


class LoopDeviceUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.config.media_path(
            context.graph.resolve_path(self.specification.file)
        )

        cmd = ["losetup"]
        cmd += self.specification.args
        cmd += ["--find", file_path]

        yield Command(cmd, capture=self.specification.capture)


class LoopDeviceDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command([
            context.config.shell, "-c", f"losetup --detach \"${self.specification.capture}\""
        ])


class LoopDevice(Specification):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(
            name,
            [file],
            apply=LoopDeviceUpCommandGenerator(self),
            up=LoopDeviceUpCommandGenerator(self),
            down=LoopDeviceDownCommandGenerator(self),
        )
        self.file = file
        self.args = args

    @property
    def capture(self) -> str:
        return f"loop_device_{self.name}"

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, f"${self.capture}")
