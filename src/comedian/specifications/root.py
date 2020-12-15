import os

from comedian.graph import ResolveLink
from comedian.specification import Specification


def _join(root: str, child: str) -> str:
    if child.startswith(root):
        return child
    else:
        return os.path.join(root, child)


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, "/", _join)
