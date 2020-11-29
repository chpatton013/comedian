"""
Parsing API for specification (or spec) dicts.

Invoke the `parse()` function to generate a collection of Specifications, or
raise errors on invalid input.
"""

import logging
from typing import Any, Dict, Iterator, Mapping, Set, Tuple

from comedian.specification import Specification
from comedian.specifications import (
    CryptVolume,
    Directory,
    File,
    Filesystem,
    Partition,
    PartitionTable,
    LoopDevice,
    LvmLogicalVolume,
    LvmPhysicalVolume,
    LvmVolumeGroup,
    PhysicalDevice,
    RaidVolume,
    Root,
    SwapVolume,
)

__all__ = [
    "FoundIllegalKeysError",
    "FoundIncompatibleKeysError",
    "MissingRequiredKeysError",
    "MissingVariantKeysError",
    "ParseError",
    "parse",
]

# Public interface


class ParseError(Exception):
    """
    Base class for all parse errors.
    """
    pass


class MissingRequiredKeysError(ParseError):
    """
    Error thrown when required keys are missing from a spec.
    """
    def __init__(self, name: str, spec: Dict[str, Any], keys: Set[str]):
        super().__init__(
            f"{name}: Missing required keys {str(keys)} in spec: {str(spec)}"
        )
        self.name = name
        self.spec = spec
        self.keys = keys


class MissingVariantKeysError(ParseError):
    """
    Error thrown when variant keys are missing from a spec.
    """
    def __init__(self, name: str, spec: Dict[str, Any], keys: Set[str]):
        super().__init__(
            f"{name}: Missing one of variant keys {str(keys)} in spec: {str(spec)}"
        )
        self.name = name
        self.spec = spec
        self.keys = keys


class FoundIllegalKeysError(ParseError):
    """
    Error thrown when illegal keys are found in a spec.
    """
    def __init__(self, name: str, spec: Dict[str, Any], keys: Set[str]):
        super().__init__(
            f"{name}: Found illegal keys {str(keys)} in spec: {str(spec)}"
        )
        self.name = name
        self.spec = spec
        self.keys = keys


class FoundIncompatibleKeysError(ParseError):
    """
    Error thrown when incompatible keys are found in a spec.
    """
    def __init__(self, name: str, spec: Dict[str, Any], keys: Set[str]):
        super().__init__(
            f"{name}: Found incompatible keys {str(keys)} in spec: {str(spec)}"
        )
        self.name = name
        self.spec = spec
        self.keys = keys


def parse(spec: Mapping[str, Any]) -> Iterator[Specification]:
    """
    Parse a spec and yield the specifications described within.
    """
    validate_spec(
        "Root",
        spec,
        required={"physical_devices"},
        allowed={"raid_volumes", "lvm_volume_groups"},
    )

    yield Root()

    for physical_device_spec in spec["physical_devices"]:
        yield from parse_physical_device(physical_device_spec)

    for raid_volume_spec in spec.get("raid_volumes", []):
        yield from parse_raid_volume(raid_volume_spec)

    for lvm_volume_group_spec in spec.get("lvm_volume_groups", []):
        yield from parse_lvm_volume_group(lvm_volume_group_spec)


# Private interface


def validate_spec(
    name: str,
    spec: Mapping[str, Any],
    required: Set[str] = set(),
    allowed: Set[str] = set(),
    illegal: Set[str] = set(),
    variant: Set[str] = set(),
    exclusive: Set[str] = set(),
    inclusive: Set[str] = set(),
    ignore: bool = False,
) -> Set[str]:
    missing = required - spec.keys()
    if missing:
        raise MissingRequiredKeysError(name, dict(spec), missing)

    valid = required | allowed
    if not ignore:
        disallowed = spec.keys() - valid
        if disallowed:
            raise FoundIllegalKeysError(name, dict(spec), disallowed)

    disallowed = spec.keys() & illegal
    if illegal and disallowed:
        raise FoundIllegalKeysError(name, dict(spec), disallowed)

    missing = spec.keys() & variant
    if variant and len(missing) < 1:
        raise MissingVariantKeysError(name, dict(spec), variant)

    mutually_exclusive = exclusive | variant
    incompatible = spec.keys() & mutually_exclusive
    if len(incompatible) > 1:
        raise FoundIncompatibleKeysError(name, dict(spec), incompatible)

    specified = spec.keys() & inclusive
    missing = inclusive - spec.keys()
    if inclusive and specified and specified != inclusive:
        raise MissingRequiredKeysError(name, dict(spec), missing)

    return valid


def split_spec(name: str, spec: Mapping[str, Any],
                   **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    valid_keys = validate_spec(name, spec, **kwargs)

    lhs = dict()
    rhs = dict()
    for key in spec:
        if key in valid_keys:
            lhs[key] = spec[key]
        else:
            rhs[key] = spec[key]
    return lhs, rhs


def parse_block_device(
    name: str,
    spec: Mapping[str, Any],
    device: str,
) -> Iterator[Specification]:
    keys = {
        "partition_table",
        "filesystem",
        "crypt_volume",
        "swap_volume",
        "lvm_physical_volume",
    }
    validate_spec(name, spec, allowed=keys, variant=keys, exclusive=keys)

    if "partition_table" in spec:
        partition_table_spec = spec["partition_table"]
        validate_spec(
            "PartitionTable",
            partition_table_spec,
            illegal={"name", "device"},
            ignore=True,
        )
        yield from parse_partition_table({
            "name": f"{device}:pt",
            "device": device,
            **partition_table_spec
        })

    if "filesystem" in spec:
        filesystem_spec = spec["filesystem"]
        validate_spec(
            "Filesystem",
            filesystem_spec,
            illegal={"device"},
            ignore=True,
        )
        yield from parse_filesystem({"device": device, **filesystem_spec})

    if "crypt_volume" in spec:
        crypt_volume_spec = spec["crypt_volume"]
        validate_spec(
            "CryptVolume",
            crypt_volume_spec,
            illegal={"device"},
            ignore=True,
        )
        yield from parse_crypt_volume({"device": device, **crypt_volume_spec})

    if "swap_volume" in spec:
        swap_volume_spec = spec["swap_volume"]
        validate_spec(
            "SwapVolume",
            swap_volume_spec,
            illegal={"device"},
            ignore=True,
        )
        yield from parse_swap_volume({"device": device, **swap_volume_spec})

    if "lvm_physical_volume" in spec:
        lvm_physical_volume_spec = spec["lvm_physical_volume"]
        validate_spec(
            "LvmPhysicalVolume",
            lvm_physical_volume_spec,
            illegal={"device"},
            ignore=True,
        )
        yield from parse_lvm_physical_volume({
            "device": device,
            **lvm_physical_volume_spec
        })


def parse_physical_device(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_physical_device")

    name = "PhysicalDevice"
    physical_device_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name"},
        ignore=True,
    )

    physical_device_name = physical_device_spec["name"]
    yield PhysicalDevice(name=physical_device_name)

    if block_device_spec:
        yield from parse_block_device(
            name, block_device_spec, physical_device_name
        )


def parse_partition_table(
    spec: Mapping[str, Any],
) -> Iterator[Specification]:
    logging.debug("parse_partition_table")

    validate_spec(
        "PartitionTable",
        spec,
        required={"name", "device", "type", "partitions"},
        allowed={"glue"},
    )

    partition_table_name = spec["name"]
    yield PartitionTable(
        name=partition_table_name,
        device=spec["device"],
        type=spec["type"],
        glue=spec.get("glue"),
    )

    for index, partition_spec in enumerate(spec["partitions"]):
        validate_spec(
            "Partition",
            partition_spec,
            illegal={"name", "partition_table", "number"},
            ignore=True,
        )

        number = index + 1
        yield from parse_partition({
            "name": f"{partition_table_name}:{number}",
            "partition_table": partition_table_name,
            "number": number,
            **partition_spec
        })


def parse_partition(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_partition")

    name = "Partition"
    partition_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name", "partition_table", "number", "type", "start", "end"},
        allowed={"align", "label", "unit", "flags"},
        ignore=True,
    )

    partition_name = partition_spec["name"]
    yield Partition(
        name=partition_name,
        partition_table=partition_spec["partition_table"],
        align=partition_spec.get("align"),
        number=partition_spec["number"],
        type=partition_spec["type"],
        start=partition_spec["start"],
        end=partition_spec["end"],
        label=partition_spec.get("label"),
        unit=partition_spec.get("unit"),
        flags=partition_spec.get("flags", []),
    )

    if block_device_spec:
        yield from parse_block_device(name, block_device_spec, partition_name)


def parse_raid_volume(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_raid_volume")

    name = "RaidVolume"
    raid_volume_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name", "devices", "level", "metadata"},
        ignore=True,
    )

    raid_volume_name = raid_volume_spec["name"]
    yield RaidVolume(
        name=raid_volume_name,
        devices=raid_volume_spec["devices"],
        level=raid_volume_spec["level"],
        metadata=raid_volume_spec["metadata"],
    )

    if block_device_spec:
        yield from parse_block_device(name, block_device_spec, raid_volume_name)


def parse_crypt_volume(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_crypt_volume")

    name = "CryptVolume"
    crypt_volume_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name", "device", "type", "keyfile", "keysize"},
        allowed={"password"},
        ignore=True,
    )

    crypt_volume_name = crypt_volume_spec["name"]
    yield CryptVolume(
        name=crypt_volume_name,
        device=crypt_volume_spec["device"],
        type=crypt_volume_spec["type"],
        keyfile=crypt_volume_spec["keyfile"],
        keysize=crypt_volume_spec["keysize"],
        password=crypt_volume_spec.get("password"),
    )

    if block_device_spec:
        yield from parse_block_device(
            name, block_device_spec, crypt_volume_name
        )


def parse_lvm_physical_volume(
    spec: Mapping[str, Any],
) -> Iterator[Specification]:
    logging.debug("parse_lvm_physical_volume")

    validate_spec("LvmPhysicalVolume", spec, required={"name", "device"})

    yield LvmPhysicalVolume(
        name=spec["name"],
        device=spec["device"],
    )


def parse_lvm_volume_group(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_lvm_volume_group")

    validate_spec(
        "LvmVolumeGroup",
        spec,
        required={"name", "lvm_physical_volumes", "lvm_logical_volumes"},
    )

    lvm_volume_group_name = spec["name"]
    yield LvmVolumeGroup(
        name=lvm_volume_group_name,
        lvm_physical_volumes=spec["lvm_physical_volumes"],
    )

    for lvm_logical_volume_spec in spec["lvm_logical_volumes"]:
        validate_spec(
            "LvmLogicalVolume",
            lvm_logical_volume_spec,
            illegal={"lvm_volume_group"},
            ignore=True,
        )
        yield from parse_lvm_logical_volume({
            "lvm_volume_group": lvm_volume_group_name,
            **lvm_logical_volume_spec
        })


def parse_lvm_logical_volume(
    spec: Mapping[str, Any],
) -> Iterator[Specification]:
    logging.debug("parse_lvm_logical_volume")

    name = "LvmLogicalVolume"
    lvm_logical_volume_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name", "lvm_volume_group"},
        allowed={
            "size",
            "extents",
            "type",
            "args",
            "lvm_physical_volumes",
            "lvm_poolmetadata_volume",
            "lvm_cachepool_volume",
            "lvm_thinpool_volume",
        },
        ignore=True,
    )
    split_spec(
        name,
        spec,
        exclusive={"size", "extents"},
        ignore=True,
    )
    split_spec(
        name,
        spec,
        exclusive={
            "lvm_poolmetadata_volume",
            "lvm_cachepool_volume",
            "lvm_thinpool_volume",
        },
        ignore=True,
    )

    lvm_logical_volume_name = lvm_logical_volume_spec["name"]
    lvm_physical_volumes = lvm_logical_volume_spec.get(
        "lvm_physical_volumes",
        [],
    )
    lvm_poolmetadata_volume = lvm_logical_volume_spec.get(
        "lvm_poolmetadata_volume",
    )
    lvm_cachepool_volume = lvm_logical_volume_spec.get("lvm_cachepool_volume")
    lvm_thinpool_volume = lvm_logical_volume_spec.get("lvm_thinpool_volume")
    yield LvmLogicalVolume(
        name=lvm_logical_volume_name,
        size=lvm_logical_volume_spec.get("size"),
        extents=lvm_logical_volume_spec.get("extents"),
        type=lvm_logical_volume_spec.get("type"),
        args=lvm_logical_volume_spec.get("args", []),
        lvm_volume_group=lvm_logical_volume_spec["lvm_volume_group"],
        lvm_physical_volumes=lvm_physical_volumes,
        lvm_poolmetadata_volume=lvm_poolmetadata_volume,
        lvm_cachepool_volume=lvm_cachepool_volume,
        lvm_thinpool_volume=lvm_thinpool_volume,
    )

    if block_device_spec:
        yield from parse_block_device(
            name, block_device_spec, lvm_logical_volume_name
        )


def parse_filesystem(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_filesystem")

    validate_spec(
        "Filesystem",
        spec,
        required={"name", "device", "mountpoint", "type"},
        allowed={"options", "directories", "files"},
    )

    filesystem_name = spec["name"]
    yield Filesystem(
        name=filesystem_name,
        device=spec["device"],
        mountpoint=spec["mountpoint"],
        type=spec["type"],
        options=spec.get("options", []),
    )

    for directory_spec in spec.get("directories", []):
        validate_spec(
            "Directory",
            directory_spec,
            required={"relative_path"},
            illegal={"name", "filesystem"},
            ignore=True,
        )
        yield from parse_directory({
            "name": f"{filesystem_name}:{directory_spec['relative_path']}",
            "filesystem": filesystem_name,
            **directory_spec
        })

    for file_spec in spec.get("files", []):
        validate_spec(
            "File",
            file_spec,
            required={"relative_path"},
            illegal={"name", "filesystem"},
            ignore=True,
        )
        yield from parse_file({
            "name": f"{filesystem_name}:{file_spec['relative_path']}",
            "filesystem": filesystem_name,
            **file_spec
        })


def parse_directory(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_directory")

    validate_spec(
        "Directory",
        spec,
        required={"name", "filesystem", "relative_path"},
        allowed={"owner", "group", "mode"},
    )

    yield Directory(
        name=spec["name"],
        filesystem=spec["filesystem"],
        relative_path=spec["relative_path"],
        owner=spec.get("owner"),
        group=spec.get("group"),
        mode=spec.get("mode"),
    )


def parse_file(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_file")

    validate_spec(
        "File",
        spec,
        required={"name", "filesystem", "relative_path"},
        allowed={
            "owner", "group", "mode", "size", "loop_device", "swap_volume"
        },
        exclusive={"loop_device", "swap_volume"},
    )

    file_name = spec["name"]
    yield File(
        name=file_name,
        filesystem=spec["filesystem"],
        relative_path=spec["relative_path"],
        owner=spec.get("owner"),
        group=spec.get("group"),
        mode=spec.get("mode"),
        size=spec.get("size"),
    )

    if "loop_device" in spec:
        validate_spec("File", spec, required={"size"}, ignore=True)
        loop_device_spec = spec["loop_device"]
        validate_spec(
            "LoopDevice",
            loop_device_spec,
            illegal={"file"},
            ignore=True,
        )
        yield from parse_loop_device({"file": file_name, **loop_device_spec})

    if "swap_volume" in spec:
        validate_spec("File", spec, required={"size"}, ignore=True)
        swap_volume_spec = spec["swap_volume"]
        validate_spec(
            "SwapVolume",
            swap_volume_spec,
            illegal={"device"},
            ignore=True,
        )
        yield from parse_swap_volume({"device": file_name, **swap_volume_spec})


def parse_loop_device(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_loop_device")

    name = "LoopDevice"
    loop_device_spec, block_device_spec = split_spec(
        name,
        spec,
        required={"name", "file"},
        allowed={"args"},
        ignore=True,
    )

    loop_device_name = loop_device_spec["name"]
    yield LoopDevice(
        name=loop_device_name,
        file=loop_device_spec["file"],
        args=loop_device_spec.get("args", []),
    )

    if block_device_spec:
        yield from parse_block_device(name, block_device_spec, loop_device_name)


def parse_swap_volume(spec: Mapping[str, Any]) -> Iterator[Specification]:
    logging.debug("parse_swap_volume")

    validate_spec(
        "SwapVolume",
        spec,
        required={"name", "device"},
        allowed={"label", "pagesize", "uuid"},
    )

    yield SwapVolume(
        name=spec["name"],
        device=spec["device"],
        label=spec.get("label"),
        pagesize=spec.get("pagesize"),
        uuid=spec.get("uuid"),
    )
