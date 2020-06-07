from .specification import Specification
from ..command import Command, CommandGenerator
from ..graph import ResolveLink


class Root(Specification):
    def __init__(self):
        super().__init__("/", [])

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, "/")
