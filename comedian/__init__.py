from comedian.action import make_action
from comedian.command import CommandContext
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.mode import make_mode


def run(
    config: Configuration,
    graph: Graph,
    action_name: str,
    mode_name: str,
):
    action = make_action(action_name, CommandContext(config, graph))
    mode = make_mode(mode_name)

    mode.on_begin()
    for specification in graph.walk():
        mode.on_specification(specification)
        for command in action(specification):
            mode.on_command(command)
    mode.on_end()
