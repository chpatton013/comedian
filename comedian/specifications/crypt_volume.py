from typing import Iterator, Optional

from ..command import Command, CommandGenerator
from ..declaration import Declaration


class CryptVolume(CommandGenerator, Declaration):
    def __init__(
        self,
        name: str,
        device: str,
        type: str,
        keyfile: Optional[str],
        keysize: Optional[str],
        password: Optional[str],
    ):
        dependencies = [device]
        if keyfile:
            dependencies.append(keyfile)
        super().__init__(name, dependencies)

        self.device = device
        self.type = type
        self.keyfile = keyfile
        self.keysize = keysize
        self.password = password

    def generate_commands(self) -> Iterator[Command]:
        yield from ()
