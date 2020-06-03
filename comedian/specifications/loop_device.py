from typing import List

from ..declaration import Declaration


class LoopDevice(Declaration):
    def __init__(self, name: str, file: str, args: List[str]):
        super().__init__(name, [file])
        self.file = file
        self.args = args
