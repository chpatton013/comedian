"""
Command API for generating shell commands to be run on a system.
"""

import shlex
from abc import ABC, abstractmethod
from typing import Dict, Iterator, List, Optional

from comedian.configuration import Configuration
from comedian.graph import Graph
from comedian.traits import DebugMixin, EqMixin


class Command(DebugMixin, EqMixin):
    """
    A container for the arguments of a shell command.
    """

    def __init__(self, cmd: List[str], capture: Optional[str] = None):
        self.cmd = cmd
        self.capture = capture

    def join(self) -> str:
        return " ".join(self.cmd)


class CommandContext(DebugMixin):
    """
    A structure holding the arguments necessary for generating Commands.
    """

    def __init__(
        self,
        config: Configuration,
        graph: Graph,
    ):
        self.config = config
        self.graph = graph
        self.env: Dict[str, str] = dict()


class CommandGenerator(ABC):
    """
    Abstract base class for a Callable that generates a series of Commands.
    """

    @abstractmethod
    def __call__(self, context: CommandContext) -> Iterator[Command]:
        pass


def quote_argument(arg: str) -> str:
    return arg if shlex.quote(arg) == arg else f'"{arg}"'


def quote_subcommand(sub: str) -> str:
    return f"'{sub}'"


def cp(source: str, destination: str) -> Command:
    return Command(
        [
            "cp",
            quote_argument(source),
            quote_argument(destination),
            "--preserve=mode,ownership",
        ]
    )


def chmod(mode: str, *paths: str) -> Command:
    return Command(["chmod", mode] + [quote_argument(path) for path in paths])


def chown(
    owner: Optional[str],
    group: Optional[str],
    *paths: str,
) -> Command:
    own = ""
    if owner:
        own += owner
    if group:
        own += f":{group}"
    return Command(["chown", own] + [quote_argument(path) for path in paths])


def crypttab_append(context: CommandContext, crypttab_entry: str) -> Command:
    crypttab_filepath = context.config.tmp_path("/etc/crypttab")
    return Command(
        [
            context.config.shell,
            "-c",
            f'echo -e "{crypttab_entry}" >> {crypttab_filepath}',
        ]
    )


def fstab_append(context: CommandContext, fstab_entry: str) -> Command:
    fstab_filepath = context.config.tmp_path("/etc/fstab")
    return Command(
        [context.config.shell, "-c", f'echo -e "{fstab_entry}" >> {fstab_filepath}']
    )


def identify_device_path(identify: str, device_path: str) -> str:
    if identify == "device":
        return device_path
    elif identify == "uuid":
        return "UUID=$({})".format(
            _identify_device_node_cmd(device_path, "/dev/disk/by-uuid/")
        )
    elif identify == "partuuid":
        return "PARTUUID=$({})".format(
            _identify_device_node_cmd(device_path, "/dev/disk/by-partuuid/")
        )
    elif identify == "label":
        return "LABEL=$({})".format(
            _identify_device_node_cmd(device_path, "/dev/disk/by-label/")
        )
    elif identify == "path":
        return "$({})".format(
            _identify_device_path_cmd(device_path, "/dev/disk/by-path/")
        )
    elif identify == "id":
        return "$({})".format(
            _identify_device_path_cmd(device_path, "/dev/disk/by-id/")
        )
    else:
        raise RuntimeError(f"Unexpected value for identify: '{identify}'")


def ln(source: str, dest: str, symbolic: bool = False) -> Command:
    cmd = ["ln", "--force"]
    if symbolic:
        cmd.append("--symbolic")
    cmd += [quote_argument(source), quote_argument(dest)]
    return Command(cmd)


def mkdir(*paths: str) -> Command:
    return Command(["mkdir", "--parents"] + [quote_argument(path) for path in paths])


def parted(*args: str, align: Optional[str] = None) -> Command:
    cmd = ["parted", "--script"]
    if align:
        cmd.append(f"--align={align}")
    cmd.append("--")
    return Command(cmd + list(args))


def _identify_device_path_cmd(device_path: str, root: str) -> str:
    return f"find {root} -type l -ilname {quote_argument(device_path)}"


def _identify_device_node_cmd(device_path: str, root: str) -> str:
    return " | ".join(
        [
            _identify_device_path_cmd(device_path, root),
            f"sed --expression='s#{root}##'",
        ]
    )
