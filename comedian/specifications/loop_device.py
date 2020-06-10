from typing import Iterator, List

from ..command import Command, CommandContext, CommandGenerator
from ..graph import ResolveLink
from ..specification import Specification


class LoopDeviceUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.graph.resolve_path(self.specification.file)

        cmd = ["losetup"]
        cmd += self.specification.args
        cmd += [
            _loop_device(self.specification.name),
            file_path,
        ]

        yield Command(cmd)


class LoopDeviceDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command([
            "losetup", "--detach",
            _loop_device(self.specification.name)
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

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, _loop_device(self.name))


def _loop_device(name: str) -> str:
    return f"/dev/{name}"
