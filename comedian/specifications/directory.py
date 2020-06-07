from typing import Iterator, Optional

from .specification import Specification
from ..command import (
    Command,
    CommandContext,
    CommandGenerator,
    chmod,
    chown,
    mkdir,
)
from ..graph import ResolveLink


class DirectoryApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Directory"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        directory_path = context.config.media_path(
            context.graph.resolve_path(self.specification.name)
        )

        yield mkdir(directory_path)
        if self.specification.owner or self.specification.group:
            yield chown(
                self.specification.owner,
                self.specification.group,
                directory_path,
            )
        if self.specification.mode:
            yield chmod(self.specification.mode, directory_path)


class Directory(Specification):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
    ):
        super().__init__(
            name,
            [filesystem],
            apply=DirectoryApplyCommandGenerator(self),
        )
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.filesystem, self.relative_path)
