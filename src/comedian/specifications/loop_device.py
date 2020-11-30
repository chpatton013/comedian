from typing import Iterator, List

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    quote_argument,
    quote_subcommand,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class LoopDeviceUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.config.media_path(
            context.graph.resolve_path(self.specification.file)
        )

        cmd = [
            "losetup",
            *self.specification.args,
            "--find",
            "--show",
            quote_argument(file_path),
        ]

        yield Command(cmd, capture=self.specification.capture)


class LoopDevicePreDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.config.media_path(
            context.graph.resolve_path(self.specification.file)
        )

        cmd = [
            context.config.shell,
            "-c",
            quote_subcommand(_find_loop_device(file_path)),
        ]
        yield Command(cmd, capture=self.specification.capture)


class LoopDeviceDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command([
            "losetup", "--detach", quote_argument(f"${self.specification.capture}")
        ])


class LoopDevice(Specification):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(
            name,
            [file],
            apply=LoopDeviceUpCommandGenerator(self),
            up=LoopDeviceUpCommandGenerator(self),
            pre_down=LoopDevicePreDownCommandGenerator(self),
            down=LoopDeviceDownCommandGenerator(self),
        )
        self.file = file
        self.args = args

    @property
    def capture(self) -> str:
        return f"loop_device_{self.name}"

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, f"${self.capture}")


def _find_loop_device(file_path: str) -> str:
    quoted_file_path = quote_argument(file_path)
    quoted_expression = quote_argument("s#:.*##")
    return f"losetup --associated {quoted_file_path} | sed {quoted_expression}"
