import os
from typing import Iterator

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    cp,
    chmod,
    chown,
    mkdir,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class RootApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Root"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield mkdir(context.config.tmp_path("/etc"))

        tmp_fstab_path = context.config.tmp_path("/etc/fstab")
        yield Command(["truncate", "--size=0", tmp_fstab_path])
        yield chmod("0644", tmp_fstab_path)
        yield chown("root", "root", tmp_fstab_path)

        tmp_crypttab_path = context.config.tmp_path("/etc/crypttab")
        yield Command(["truncate", "--size=0", tmp_crypttab_path])
        yield chmod("0644", tmp_crypttab_path)
        yield chown("root", "root", tmp_crypttab_path)


class RootPostApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "Root"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield mkdir(context.config.media_path("/etc"))

        tmp_fstab_path = context.config.tmp_path("/etc/fstab")
        media_fstab_path = context.config.media_path("/etc/fstab")
        yield cp(tmp_fstab_path, media_fstab_path)

        tmp_crypttab_path = context.config.tmp_path("/etc/crypttab")
        media_crypttab_path = context.config.media_path("/etc/crypttab")
        yield cp(tmp_crypttab_path, media_crypttab_path)


class Root(Specification):
    def __init__(self):
        super().__init__(
            "//",
            [],
            apply=RootApplyCommandGenerator(self),
            post_apply=RootPostApplyCommandGenerator(self),
        )

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, "/", _join)


def _join(root: str, child: str) -> str:
    if child.startswith(root):
        return child
    else:
        return os.path.join(root, child)
