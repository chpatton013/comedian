from typing import List, Optional

from ..action import ActionCommandGenerator
from ..command import CommandGenerator
from ..graph import GraphNode


class Specification(ActionCommandGenerator, GraphNode):
    """
    Composite base class for all Specifications.
    """
    def __init__(
        self,
        name: str,
        dependencies: List[str],
        references: List[str] = [],
        apply: Optional[CommandGenerator] = None,
        post_apply: Optional[CommandGenerator] = None,
        up: Optional[CommandGenerator] = None,
        down: Optional[CommandGenerator] = None,
    ):
        ActionCommandGenerator.__init__(
            self,
            apply=apply,
            post_apply=post_apply,
            up=up,
            down=down,
        )
        GraphNode.__init__(self, name, dependencies, references=references)
