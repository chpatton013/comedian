import os
from typing import Iterable, Iterator, List, Optional

from comedian.command import Command, CommandContext, CommandGenerator, mkdir
from comedian.graph import ResolveLink
from comedian.specification import Specification


class CryptVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = context.graph.resolve_device(self.specification.device)
        tmp_keyfile = context.config.tmp_path(
            context.graph.resolve_path(self.specification.keyfile)
        )

        yield from _randomize_device(self.specification.name, device_path, context)
        yield from _create_keyfile(tmp_keyfile, self.specification.keysize, context)
        yield from _format_crypt(
            self.specification.name,
            device_path,
            tmp_keyfile,
            self.specification.type,
            self.specification.password,
            context,
        )


class CryptVolumePostApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        tmp_keyfile = context.config.tmp_path(self.specification.keyfile)
        dest_keyfile = context.config.media_path(
            context.graph.resolve_path(self.specification.keyfile)
        )

        yield Command(["cp", tmp_keyfile, dest_keyfile, "--preserve=mode,ownership"])


class CryptVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        dest_keyfile = context.config.media_path(
            context.graph.resolve_path(self.specification.keyfile)
        )

        yield Command(
            _open_crypt(
                self.specification.name, self.specification.device, dest_keyfile
            )
        )


class CryptVolumeDownCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        yield Command(_close_crypt(self.specification.name))


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
        return ResolveLink(None, _crypt_device(self.name))


def _crypt_device(name: str) -> str:
    return f"/dev/mapper/{name}"


def _dd(*args: Iterable[str]) -> List[str]:
    return ["dd", "status=progress", "conv=sync,noerror"] + list(args)


def _cryptsetup(*args: Iterable[str]) -> List[str]:
    return ["cryptsetup", "--batch-mode"] + list(args)


def _open_crypt(
    name: str,
    device: str,
    keyfile: str,
    *args: Iterable[str],
) -> List[str]:
    return _cryptsetup(
        f"--key-file={keyfile}",
        "open",
        device,
        name,
        *args,
    )


def _close_crypt(name: str) -> List[str]:
    return _cryptsetup("close", name)


def _randomize_device(
    name: str,
    device: str,
    context: CommandContext,
) -> Iterator[Command]:
    cryptname = f"randomize_{name}"

    yield Command(
        _open_crypt(
            cryptname,
            device,
            context.config.random_device,
            "--type=plain",
        )
    )
    dd_cmd = " ".join(
        _dd(
            f"if=/dev/zero",
            f"of={_crypt_device(cryptname)}",
            f"bs={context.config.dd_bs}",
        )
    )
    yield Command([context.config.shell, "-c", f"{dd_cmd} || true"])
    yield Command(["sync"])
    yield Command(_close_crypt(cryptname))


def _create_keyfile(
    keyfile: str,
    keysize: str,
    context: CommandContext,
) -> Iterator[Command]:
    yield mkdir(os.path.dirname(keyfile))
    yield Command(
        _dd(
            f"if={context.config.random_device}",
            f"of={keyfile}",
            f"bs={keysize}",
            "count=1",
        )
    )


def _format_crypt(
    name: str,
    device: str,
    keyfile: str,
    type: str,
    password: Optional[str],
    context: CommandContext,
) -> Iterator[Command]:
    yield Command(
        _cryptsetup(
            f"--key-file={keyfile}",
            "luksFormat",
            f"--type={type}",
            device,
        )
    )
    if password:
        add_key_cmd = " ".join(
            _cryptsetup(
                f"--key-file={keyfile}",
                "luksAddKey",
                device,
            )
        )
        yield Command([context.config.shell, "-c", f"echo {password} | {add_key_cmd}"])
    yield Command(_open_crypt(name, device, keyfile))
