#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
from typing import Any, Dict, Optional, List

from comedian import run
from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.parse import parse


def parse_args(default_config_path: str, argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="comedian",
        description="Configuration-driven media preparation",
    )
    parser.add_argument(
        "action",
        choices=("apply", "up", "down"),
        help="Action to perform",
    )
    parser.add_argument(
        "specification",
        default=None,
        help="Path to specification file (default: stdin)",
    )
    parser.add_argument(
        "--config",
        default=default_config_path,
        help=f"Path to configuration file (default: {default_config_path})",
    )
    parser.add_argument(
        "--mode",
        choices=("exec", "dryrun", "shell"),
        default="shell",
        help="Operational mode for the chosen action (default: shell)",
    )
    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument(
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="Show debug log messages (default: info, warning, and error)",
    )
    log_level_group.add_argument(
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="log_level",
        help=
        "Only show warning and error log messages (default: info, warning, and error)",
    )
    parser.set_defaults(log_level=logging.INFO)
    return parser.parse_args(argv)


def load_config(configuration: str) -> Configuration:
    with open(configuration, "r") as f:
        return Configuration(**json.load(f))


def load_spec(specification: Optional[str]) -> Dict[str, Any]:
    if not specification or specification == "-":
        return json.load(sys.stdin)
    with open(specification, "r") as f:
        return json.load(f)


def main(argv):
    default_config_path = os.path.join(
        os.path.dirname(__file__),
        "default.config.json",
    )
    args = parse_args(default_config_path, argv)

    logging.basicConfig(level=args.log_level)

    config = load_config(args.config)
    graph = Graph(parse(load_spec(args.specification)))

    run(config, graph, args.action, args.mode)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
