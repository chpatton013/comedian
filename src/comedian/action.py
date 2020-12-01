"""
Action API for encapsulating the command-generation of different named tasks.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Optional

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
        pre_down: Optional[CommandGenerator] = None,
        down: Optional[CommandGenerator] = None,
    ):
        self.apply = apply
        self.post_apply = post_apply
        self.up = up
        self.pre_down = pre_down
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

    def generate_pre_down_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.pre_down:
            yield from self.pre_down(context)

    def generate_down_commands(
        self,
        context: CommandContext,
    ) -> Iterator[Command]:
        if self.down:
            yield from self.down(context)


class ActionCommandHandler(ABC):
    """
    Base class for all objects that will handle commands for Actions.
    """

    @abstractmethod
    def on_begin(self, context: CommandContext):
        pass

    @abstractmethod
    def on_generator(self, context: CommandContext, generator: ActionCommandGenerator):
        pass

    @abstractmethod
    def on_command(self, context: CommandContext, command: Command):
        pass

    @abstractmethod
    def on_end(self, context: CommandContext):
        pass


class Action(ABC):
    """
    Base class for all objects that will encapsule command-generation.
    """

    @abstractmethod
    def __call__(
        self,
        handler: ActionCommandHandler,
        generators: Iterable[ActionCommandGenerator],
    ):
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

    def __call__(
        self,
        handler: ActionCommandHandler,
        generators: Iterable[ActionCommandGenerator],
    ):
        generators_sequence = list(generators)

        handler.on_begin(self.context)

        for specification in generators_sequence:
            handler.on_generator(self.context, specification)
            for command in specification.generate_apply_commands(self.context):
                handler.on_command(self.context, command)

        for specification in generators_sequence:
            handler.on_generator(self.context, specification)
            for command in specification.generate_post_apply_commands(self.context):
                handler.on_command(self.context, command)

        handler.on_end(self.context)


class UpAction(Action):
    """
    Object encapsulating the command-generation for the "up" action.
    """

    def __init__(self, context: CommandContext):
        self.context = context

    def __call__(
        self,
        handler: ActionCommandHandler,
        generators: Iterable[ActionCommandGenerator],
    ):
        handler.on_begin(self.context)

        for generator in generators:
            handler.on_generator(self.context, generator)
            for command in generator.generate_up_commands(self.context):
                handler.on_command(self.context, command)

        handler.on_end(self.context)


class DownAction(Action):
    """
    Object encapsulating the command-generation for the "down" action.
    """

    def __init__(self, context: CommandContext):
        self.context = context

    def __call__(
        self,
        handler: ActionCommandHandler,
        generators: Iterable[ActionCommandGenerator],
    ):
        generators_sequence = list(reversed(list(generators)))

        handler.on_begin(self.context)

        for generator in generators_sequence:
            handler.on_generator(self.context, generator)
            for command in generator.generate_pre_down_commands(self.context):
                handler.on_command(self.context, command)

        for generator in generators_sequence:
            handler.on_generator(self.context, generator)
            for command in generator.generate_down_commands(self.context):
                handler.on_command(self.context, command)

        handler.on_end(self.context)
