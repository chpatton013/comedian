from typing import Iterator, Optional

from .specification import Specification


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

    def debug_fields(self) -> Iterator[str]:
        yield from (
            "name",
            "dependencies",
            "references",
            "device",
            "type",
            "keyfile",
            "keysize",
            "password",
        )

    def eq_fields(self) -> Iterator[str]:
        yield from (
            "name",
            "dependencies",
            "references",
            "device",
            "type",
            "keyfile",
            "keysize",
            "password",
        )
