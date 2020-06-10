#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

from comedian.action import make_action
from comedian.command import Command, CommandContext
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.mode import make_mode
from comedian.parse import parse


def load_config(configuration: str) -> Configuration:
    with open(configuration, "r") as f:
        return Configuration(**json.load(f))


def load_spec(specification: Optional[str]) -> Dict[str, Any]:
    if not specification or specification == "-":
        return json.load(sys.stdin)
    with open(specification, "r") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action",
        choices=("apply", "up", "down"),
        help="Action to perform",
    )
    parser.add_argument(
        "specification",
        default=None,
        help="Path to specification file",
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(__file__), "default.config.json"),
        help="Path to configuration file",
    )
    parser.add_argument(
        "--mode",
        choices=("exec", "dryrun", "shell"),
        default="shell",
        help="Operational mode of comedian tool",
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
    parser.set_defaults(log_level=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)

    config = load_config(args.config)

    spec = load_spec(args.specification)
    specifications = list(parse(spec))

    graph = Graph(specifications)

    context = CommandContext(config, graph)
    action = make_action(args.action, context)

    mode = make_mode(args.mode)

    for specification in graph.walk():
        mode.on_specification(specification)
        for command in action(specification):
            mode.on_command(command)


if __name__ == "__main__":
    main()
