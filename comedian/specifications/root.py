from comedian.command import Command, CommandGenerator
from comedian.graph import ResolveLink
from comedian.specification import Specification


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, "/")
