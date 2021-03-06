from typing import Iterator, Optional

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


class DirectoryApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Directory"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        directory_path = context.graph.resolve_path(self.specification.name)
        if not directory_path:
            raise ValueError(
                "Failed to find directory path {}".format(self.specification.name)
            )
        media_directory_path = context.config.media_path(directory_path)

        yield mkdir(media_directory_path)
        if self.specification.owner or self.specification.group:
            yield chown(
                self.specification.owner,
                self.specification.group,
                media_directory_path,
            )
        if self.specification.mode:
            yield chmod(self.specification.mode, media_directory_path)


class Directory(Specification):
    def __init__(
        self,
        name: str,
        mount: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
    ):
        super().__init__(
            name,
            [mount],
            apply=DirectoryApplyCommandGenerator(self),
        )
        self.mount = mount
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.mount, self.relative_path)
