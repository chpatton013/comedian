import os
from typing import Iterator, List, Optional

from comedian.command import (
    Command,
    CommandContext,
    CommandGenerator,
    mkdir,
    quote_argument,
    quote_subcommand,
)
from comedian.graph import ResolveLink
from comedian.specification import Specification


class CryptVolumeApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        keyfile_path = _keyfile_path(self.specification.keyfile, context)
        tmp_keyfile_path = context.config.tmp_path(keyfile_path)

        yield from _randomize_device(self.specification.name, device_path, context)
        yield from _create_keyfile(
            tmp_keyfile_path, self.specification.keysize, context
        )
        yield from _format_crypt(
            self.specification.name,
            device_path,
            tmp_keyfile_path,
            self.specification.type,
            self.specification.password,
            context,
        )


class CryptVolumePostApplyCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        keyfile_path = _keyfile_path(self.specification.keyfile, context)
        tmp_keyfile_path = context.config.tmp_path(keyfile_path)
        media_keyfile_path = context.config.media_path(keyfile_path)

        yield Command(
            [
                "cp",
                quote_argument(tmp_keyfile_path),
                quote_argument(media_keyfile_path),
                "--preserve=mode,ownership",
            ]
        )


class CryptVolumeUpCommandGenerator(CommandGenerator):
    def __init__(self, specification: "CryptVolume"):
        self.specification = specification

    def __call__(self, context: CommandContext) -> Iterator[Command]:
        device_path = _device_path(self.specification.device, context)
        keyfile_path = _keyfile_path(self.specification.keyfile, context)
        tmp_keyfile_path = context.config.tmp_path(keyfile_path)

        yield Command(
            _open_crypt(self.specification.name, device_path, tmp_keyfile_path)
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


def _dd(*args: str) -> List[str]:
    return ["dd", "status=progress", "conv=sync,noerror"] + list(args)


def _cryptsetup(*args: str) -> List[str]:
    return ["cryptsetup", "--batch-mode"] + list(args)


def _open_crypt(
    name: str,
    device: str,
    keyfile: str,
    *args: str,
) -> List[str]:
    return _cryptsetup(
        f"--key-file={quote_argument(keyfile)}",
        "open",
        quote_argument(device),
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
            "if=/dev/zero",
            f"of={quote_argument(_crypt_device(cryptname))}",
            f"bs={context.config.dd_bs}",
        )
    )
    yield Command([context.config.shell, "-c", quote_subcommand(f"{dd_cmd} || true")])
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
            f"if={quote_argument(context.config.random_device)}",
            f"of={quote_argument(keyfile)}",
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
            f"--key-file={quote_argument(keyfile)}",
            "luksFormat",
            f"--type={type}",
            quote_argument(device),
        )
    )
    if password:
        add_key_cmd = " ".join(
            _cryptsetup(
                f"--key-file={quote_argument(keyfile)}",
                "luksAddKey",
                quote_argument(device),
            )
        )
        yield Command(
            [
                quote_argument(context.config.shell),
                "-c",
                quote_subcommand(f"echo {password} | {add_key_cmd}"),
            ]
        )
    yield Command(_open_crypt(name, device, keyfile))


def _device_path(device: str, context: CommandContext) -> str:
    device_path = context.graph.resolve_device(device)
    if not device_path:
        raise ValueError("Failed to find device path {}".format(device))
    return device_path


def _keyfile_path(keyfile: str, context: CommandContext) -> str:
    keyfile_path = context.graph.resolve_path(keyfile)
    if not keyfile_path:
        raise ValueError("Failed to find keyfile path {}".format(keyfile))
    return keyfile_path
