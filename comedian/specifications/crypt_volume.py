from typing import Optional

from ..declaration import Declaration


class CryptVolume(Declaration):
    def __init__(
        self,
        name: str,
        device: str,
        type: str,
        keysize: Optional[str],
        password: Optional[str],
    ):
        super().__init__(name, [device])
        self.device = device
        self.type = type
        self.keysize = keysize
        self.password = password
