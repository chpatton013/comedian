import argparse
import json
import logging
import sys
from typing import Any, Dict, Optional

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
    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument(
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="Show debug log messages",
    )
    log_level_group.add_argument(
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="log_level",
        help="Only show warning and error log messages",
    )
    parser.set_defaults(level=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

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
