import os
from typing import Iterator, Optional

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    chmod,
    chown,
    ln,
    mkdir,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class LinkApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Link"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        file_path = context.graph.resolve_path(self.specification.name)
        if not file_path:
            raise ValueError(
                "Failed to find file path {}".format(self.specification.name)
            )
        media_file_path = context.config.media_path(file_path)

        yield mkdir(os.path.dirname(media_file_path))
        yield ln(
            self.specification.source,
            media_file_path,
            symbolic=self.specification.symbolic,
        )

        if self.specification.owner or self.specification.group:
            yield chown(
                self.specification.owner,
                self.specification.group,
                media_file_path,
            )
        if self.specification.mode:
            yield chmod(self.specification.mode, media_file_path)


class Link(Specification):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        source: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
        symbolic: bool,
    ):
        super().__init__(
            name,
            [filesystem],
            apply=LinkApplyCommandGenerator(self),
        )
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.source = source
        self.owner = owner
        self.group = group
        self.mode = mode
        self.symbolic = symbolic

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(self.filesystem, self.relative_path)
