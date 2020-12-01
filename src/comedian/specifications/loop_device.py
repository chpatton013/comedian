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


def _file_path(file: str, context: CommandContext) -> str:
    file_path = context.graph.resolve_path(file)
    if not file_path:
        raise ValueError("Failed to find file path {}".format(file))
    return file_path


class LoopDeviceUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = _file_path(self.specification.file, context)
        media_file_path = context.config.media_path(file_path)

        cmd = [
            "losetup",
            *self.specification.args,
            "--find",
            "--show",
            quote_argument(media_file_path),
        ]

        yield Command(cmd, capture=self.specification.capture)


class LoopDevicePreDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = _file_path(self.specification.file, context)
        media_file_path = context.config.media_path(file_path)

        cmd = [
            context.config.shell,
            "-c",
            quote_subcommand(_find_loop_device(media_file_path)),
        ]
        yield Command(cmd, capture=self.specification.capture)


class LoopDeviceDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "LoopDevice"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command(
            ["losetup", "--detach", quote_argument(f"${self.specification.capture}")]
        )


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
