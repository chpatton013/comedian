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


def runtime_dir():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    if getattr(sys, "frozen", False):
        return script_dir
    else:
        return os.path.join(script_dir, "..")


COMEDIAN_VERSION = "0.0.1"

README_PATH = os.path.join(runtime_dir(), "README.md")

DEFAULT_CONFIG_PATH = os.path.join(runtime_dir(), "data", "default.config.json")


class DocumentationAction(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        with open(README_PATH, "r") as f:
            print(f.read().rstrip())
        parser.exit()


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="comedian",
        description="Configuration-driven media preparation",
    )
    parser.register("action", "doc", DocumentationAction)
    parser.add_argument("--doc", action="doc")
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {COMEDIAN_VERSION}",
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
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to configuration file (default: {DEFAULT_CONFIG_PATH})",
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
    args = parse_args(argv)

    logging.basicConfig(level=args.log_level)

    config = load_config(args.config)
    graph = Graph(parse(load_spec(args.specification)))

    run(config, graph, args.action, args.mode)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
