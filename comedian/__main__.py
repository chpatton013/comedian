import argparse
import json

from .graph import Graph
from .parse import parse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "configuration",
        help="Path to input configuration file",
    )
    args = parser.parse_args()

    with open(args.configuration, "r") as f:
        spec = json.load(f)

    declarations = parse(spec)
    graph = Graph(declarations)

    for declaration in graph.walk():
        print(declaration)
        for command in declaration.generate_commands():
            print(command)


main()
