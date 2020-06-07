import argparse
import json
import sys
from typing import Any, Callable, Dict, Iterator, Optional

from .action import make_action
from .command import Command, CommandContext
from .configuration import Configuration
from .graph import Graph
from .parse import parse


def load_spec(configuration: Optional[str]) -> Dict[str, Any]:
    if not configuration or configuration == "-":
        return json.load(sys.stdin)
    with open(configuration, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=("apply", "up", "down"),
        help="Action to perform",
    )
    parser.add_argument(
        "configuration",
        default=None,
        help="Path to input configuration file",
    )
    args = parser.parse_args()

    config = Configuration()

    spec = load_spec(args.configuration)
    specifications = parse(spec)

    graph = Graph(specifications)

    context = CommandContext(config, graph)
    action = make_action(args.action, context)

    for specification in graph.walk():
        print(specification)
        for command in action(specification):
            print(" ", command)


main()
