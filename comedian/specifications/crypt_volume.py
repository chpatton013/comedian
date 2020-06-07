from typing import Iterator, Optional

from .specification import Specification
from ..graph import ResolveLink


class CryptVolume(Specification):
    def __init__(
        self,
        name: str,
        device: str,
        type: str,
        keyfile: str,
        keysize: str,
        password: Optional[str],
    ):
        super().__init__(
            name,
            [device],
            references=[keyfile],
            apply=CryptVolumeApplyCommandGenerator(self),
            post_apply=CryptVolumePostApplyCommandGenerator(self),
            up=CryptVolumeUpCommandGenerator(self),
            down=CryptVolumeDownCommandGenerator(self),
        )
        self.device = device
        self.type = type
        self.keyfile = keyfile
        self.keysize = keysize
        self.password = password

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, _cryptdevice(self.name))


def _cryptdevice(name: str) -> str:
    return f"/dev/mapper/{name}"
