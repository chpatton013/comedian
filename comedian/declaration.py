from typing import List, Optional

from .traits import __Debug__, __Eq__


class Declaration(__Debug__, __Eq__):
    def __init__(self, name: str, dependencies: List[str]):
        self.name = name
        self.dependencies = dependencies
