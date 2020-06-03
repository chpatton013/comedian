from typing import Optional

from ..declaration import Declaration


class Directory(Declaration):
    def __init__(
        self,
        name: str,
        filesystem: str,
        relative_path: str,
        owner: Optional[str],
        group: Optional[str],
        mode: Optional[str],
    ):
        super().__init__(name, [filesystem])
        self.filesystem = filesystem
        self.relative_path = relative_path
        self.owner = owner
        self.group = group
        self.mode = mode
