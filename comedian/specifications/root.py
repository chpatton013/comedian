from ..command import Command, CommandGenerator
from ..graph import ResolveLink
from ..specification import Specification


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, "/")
