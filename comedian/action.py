"""
Action API for encapsulating the command-generation of different named tasks.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional

from comedian.command import Command, CommandContext, CommandGenerator


class ActionCommandGenerator:
    """
    Base class for all objects that will generate commands for Actions.
    """
    def __init__(
        self,
        apply: Optional[CommandGenerator] = None,
        post_apply: Optional[CommandGenerator] = None,
        up: Optional[CommandGenerator] = None,
        down: Optional[CommandGenerator] = None,
    ):
        self.apply = apply
        self.post_apply = post_apply
        self.up = up
        self.down = down

    def generate_apply_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.apply:
            yield from self.apply(context)

    def generate_post_apply_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.post_apply:
            yield from self.post_apply(context)

    def generate_up_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.up:
            yield from self.up(context)

    def generate_down_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.down:
            yield from self.down(context)


class Action(ABC):
    """
    Base class for all objects that will encapsule command-generation.
    """
    @abstractmethod
    def __call__(self, generator: ActionCommandGenerator) -> Iterator[Command]:
        pass


def make_action(name: str, context: CommandContext) -> Action:
    """
    Instantiate the appropriate Action based on the specified name.
    """
    if name == "apply":
        return ApplyAction(context)
    elif name == "up":
        return UpAction(context)
    elif name == "down":
        return DownAction(context)
    else:
        raise ValueError(f"Unknown action '{name}'")


class ApplyAction(Action):
    """
    Object encapsulating the command-generation for the "apply" action.
    """
    def __init__(self, context: CommandContext):
        self.context = context

    def __call__(self, generator: ActionCommandGenerator) -> Iterator[Command]:
        yield from generator.generate_apply_commands(self.context)
        yield from generator.generate_post_apply_commands(self.context)


class UpAction(Action):
    """
    Object encapsulating the command-generation for the "up" action.
    """
    def __init__(self, context: CommandContext):
        self.context = context

    def __call__(self, generator: ActionCommandGenerator) -> Iterator[Command]:
        yield from generator.generate_up_commands(self.context)


class DownAction(Action):
    """
    Object encapsulating the command-generation for the "down" action.
    """
    def __init__(self, context: CommandContext):
        self.context = context

    def __call__(self, generator: ActionCommandGenerator) -> Iterator[Command]:
        yield from generator.generate_down_commands(self.context)
