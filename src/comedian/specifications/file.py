import os
from typing import Iterator, Optional, Tuple

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    chmod,
    chown,
    mkdir,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class FileApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "File"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.config.media_path(
            context.graph.resolve_path(self.specification.name)
        )

        yield mkdir(os.path.dirname(file_path))
        if self.specification.size:
            yield Command([
                "fallocate",
                "--length",
                self.specification.size,
                file_path,
            ])
        if self.specification.owner or self.specification.group:
            yield chown(
                self.specification.owner,
                self.specification.group,
                file_path,
            )
        if self.specification.mode:
            yield chmod(self.specification.mode, file_path)


class File(Specification):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
        size: Optional[str],
    ):
        super().__init__(
            name,
            [filesystem],
            apply=FileApplyCommandGenerator(self),
        )
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode
        self.size = size

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.filesystem, self.relative_path)