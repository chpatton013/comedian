from typing import Iterator, List, Optional, Set

from comedian.action import ActionCommandGenerator
from comedian.command import CommandGenerator
from comedian.graph import GraphNode


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

    def __fields__(self) -> Iterator[str]:
        excluded_fields: Set[str] = {"apply", "post_apply", "up", "down"}
        for field in GraphNode.__fields__(self):
            if field not in excluded_fields:
                yield field
