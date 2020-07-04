import copy
import unittest
from unittest.mock import patch

from context import comedian

from comedian.specifications import (
    CryptVolume,
    Directory,
    File,
    Filesystem,
    GptPartition,
    GptPartitionTable,
    LoopDevice,
    LvmLogicalVolume,
    LvmPhysicalVolume,
    LvmVolumeGroup,
    PhysicalDevice,
    RaidVolume,
    Root,
    SwapVolume,
)

from comedian.parse import (
    FoundIllegalKeysError,
    FoundIncompatibleKeysError,
    MissingRequiredKeysError,
    MissingVariantKeysError,
    parse,
)

_FSROOT_SPEC = {
    "name":
        "fsroot",
    "mountpoint":
        "/",
    "type":
        "ext4",
    "directories": [
        {
            "relative_path": "raid",
            "owner": "root",
            "group": "root",
            "mode": "0755",
        },
        {
            "relative_path": "loop",
        },
    ],
    "files": [
        {
            "relative_path": "swapfile",
            "owner": "root",
            "group": "root",
            "mode": "0755",
            "size": "10",
            "swap_volume": {
                "name": "swap1",
            },
        },
        {
            "relative_path": "loopfile",
            "size": "10",
            "loop_device": {
                "name": "loop",
                "args": ["-e", "18"],
                "filesystem": {
                    "name": "fsloop",
                    "mountpoint": "/loop",
                    "type": "ext4",
                    "options": ["noatime"],
                },
            },
        },
        {
            "relative_path": "randomfile",
        },
        {
            "relative_path": "keyfile",
        },
    ],
}

SPEC = {
    "physical_devices": [
        {
            "name": "sda",
            "gpt_partition_table": {
                "glue":
                    "p",
                "gpt_partitions": [
                    {
                        "type": "primary",
                        "start": "1",
                        "end": "3",
                        "flags": ["bios_grub"],
                    },
                    {
                        "type": "primary",
                        "start": "3",
                        "end": "-1",
                        "crypt_volume": {
                            "name": "cryptroot",
                            "type": "luks2",
                            "keyfile": "fsroot:keyfile",
                            "keysize": "2048",
                            "password": "hunter2",
                            "filesystem": _FSROOT_SPEC,
                        },
                    },
                ],
            },
        },
        {
            "name": "sdb",
            "swap_volume": {
                "name": "swap2",
            },
        },
        {
            "name": "sdc",
            "lvm_physical_volume": {
                "name": "lvmpv",
            },
        },
        {
            "name": "sdd",
        },
    ],
    "raid_volumes": [{
        "name": "raidarray",
        "devices": ["sdc"],
        "level": "1",
        "metadata": "1.2",
        "filesystem": {
            "name": "fsraid",
            "mountpoint": "/raid",
            "type": "ext4",
        },
    }],
    "lvm_volume_groups": [{
        "name":
            "lvmvg",
        "lvm_physical_volumes": ["lvmpv"],
        "lvm_logical_volumes": [{
            "name": "lvmlv",
            "size": "10",
            "crypt_volume": {
                "name": "crypt_lvm",
                "type": "luks2",
                "keyfile": "fsroot:randomfile",
                "keysize": "2048",
            },
        }],
    }],
}


class ParseTestBase(unittest.TestCase):
    def setUp(self):
        self.spec = copy.deepcopy(SPEC)


class ParseRootTest(ParseTestBase):
    def test_illegal_key(self):
        spec = self.spec
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Root")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec
        del spec["physical_devices"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Root")
        self.assertSetEqual(context.exception.keys, {"physical_devices"})

    def test_complete(self):
        expected = [
            Root(),
            PhysicalDevice("sda"),
            GptPartitionTable(name="sda:gpt", device="sda", glue="p"),
            GptPartition(
                name="sda:gpt:1",
                partition_table="sda:gpt",
                align=None,
                number=1,
                type="primary",
                start="1",
                end="3",
                label=None,
                unit=None,
                flags=["bios_grub"]
            ),
            GptPartition(
                name="sda:gpt:2",
                partition_table="sda:gpt",
                align=None,
                number=2,
                type="primary",
                start="3",
                end="-1",
                label=None,
                unit=None,
                flags=[],
            ),
            CryptVolume(
                name="cryptroot",
                device="sda:gpt:2",
                type="luks2",
                keyfile="fsroot:keyfile",
                keysize="2048",
                password="hunter2"
            ),
            Filesystem(
                name="fsroot",
                device="cryptroot",
                mountpoint="/",
                type="ext4",
                options=[],
            ),
            Directory(
                name="fsroot:raid",
                filesystem="fsroot",
                relative_path="raid",
                owner="root",
                group="root",
                mode="0755",
            ),
            Directory(
                name="fsroot:loop",
                filesystem="fsroot",
                relative_path="loop",
                owner=None,
                group=None,
                mode=None,
            ),
            File(
                name="fsroot:swapfile",
                filesystem="fsroot",
                relative_path="swapfile",
                owner="root",
                group="root",
                mode="0755",
                size="10",
            ),
            SwapVolume(name="swap1", device="fsroot:swapfile"),
            File(
                name="fsroot:loopfile",
                filesystem="fsroot",
                relative_path="loopfile",
                owner=None,
                group=None,
                mode=None,
                size="10",
            ),
            LoopDevice(
                name="loop",
                file="fsroot:loopfile",
                args=["-e", "18"],
            ),
            Filesystem(
                name="fsloop",
                device="loop",
                mountpoint="/loop",
                type="ext4",
                options=["noatime"],
            ),
            File(
                name="fsroot:randomfile",
                filesystem="fsroot",
                relative_path="randomfile",
                owner=None,
                group=None,
                mode=None,
                size=None,
            ),
            File(
                name="fsroot:keyfile",
                filesystem="fsroot",
                relative_path="keyfile",
                owner=None,
                group=None,
                mode=None,
                size=None,
            ),
            PhysicalDevice("sdb"),
            SwapVolume(name="swap2", device="sdb"),
            PhysicalDevice("sdc"),
            LvmPhysicalVolume(name="lvmpv", device="sdc"),
            PhysicalDevice("sdd"),
            RaidVolume(
                name="raidarray",
                devices=["sdc"],
                level="1",
                metadata="1.2",
            ),
            Filesystem(
                name="fsraid",
                device="raidarray",
                mountpoint="/raid",
                type="ext4",
                options=[],
            ),
            LvmVolumeGroup(name="lvmvg", lvm_physical_volumes=["lvmpv"]),
            LvmLogicalVolume(
                name="lvmlv",
                size="10",
                type=None,
                args=[],
                lvm_volume_group="lvmvg",
                lvm_physical_volumes=[],
                lvm_poolmetadata_volume=None,
                lvm_cachepool_volume=None,
                lvm_thinpool_volume=None,
            ),
            CryptVolume(
                name="crypt_lvm",
                device="lvmlv",
                type="luks2",
                keyfile="fsroot:randomfile",
                keysize="2048",
                password=None,
            ),
        ]

        self.assertListEqual(list(parse(self.spec)), expected)


class ParsePhysicalDeviceTest(ParseTestBase):
    def test_illegal_key(self):
        self.spec["physical_devices"][0]["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PhysicalDevice")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        del self.spec["physical_devices"][0]["name"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PhysicalDevice")
        self.assertSetEqual(context.exception.keys, {"name"})


class ParseRaidVolumeTest(ParseTestBase):
    def test_illegal_key(self):
        spec = self.spec["raid_volumes"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "RaidVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["raid_volumes"][0]
        del spec["name"]
        del spec["devices"]
        del spec["level"]
        del spec["metadata"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "RaidVolume")
        self.assertSetEqual(
            context.exception.keys, {"name", "devices", "level", "metadata"}
        )


class ParseLvmVolumeGroupTest(ParseTestBase):
    def test_illegal_key(self):
        spec = self.spec["lvm_volume_groups"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmVolumeGroup")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["lvm_volume_groups"][0]
        del spec["name"]
        del spec["lvm_physical_volumes"]
        del spec["lvm_logical_volumes"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmVolumeGroup")
        self.assertSetEqual(
            context.exception.keys,
            {"name", "lvm_physical_volumes", "lvm_logical_volumes"},
        )


class ParseGptPartitionTableTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # gpt_partition_table spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec["name"] = "name"
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartitionTable")
        self.assertSetEqual(context.exception.keys, {"name", "device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartitionTable")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        del spec["gpt_partitions"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartitionTable")
        self.assertSetEqual(context.exception.keys, {"gpt_partitions"})


class ParseGptPartitionTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # gpt_partition spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][0]
        spec["name"] = "name"
        spec["partition_table"] = "partition_table"
        spec["number"] = 1

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartition")
        self.assertSetEqual(
            context.exception.keys, {"name", "partition_table", "number"}
        )

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartition")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][0]
        del spec["type"]
        del spec["start"]
        del spec["end"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "GptPartition")
        self.assertSetEqual(context.exception.keys, {"type", "start", "end"})


class ParseCryptVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the crypt_volume
        # spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]
        del spec["name"]
        del spec["type"]
        del spec["keyfile"]
        del spec["keysize"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(
            context.exception.keys, {"name", "type", "keyfile", "keysize"}
        )


class ParseFilesystemTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the filesystem
        # spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        del spec["name"]
        del spec["mountpoint"]
        del spec["type"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(
            context.exception.keys, {"name", "mountpoint", "type"}
        )


class ParseDirectoryTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the directory
        # spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["directories"][0]
        spec["name"] = "name"
        spec["filesystem"] = "filesystem"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"name", "filesystem"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["directories"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["directories"][0]
        del spec["relative_path"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"relative_path"})


class ParseFileTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the file spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]
        spec["name"] = "name"
        spec["filesystem"] = "filesystem"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"name", "filesystem"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]
        del spec["relative_path"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"relative_path"})


class ParseSwapVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the swap_volume
        # spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]["swap_volume"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]["swap_volume"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][0]["swap_volume"]
        del spec["name"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"name"})


class ParseLoopDeviceTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the loop_device
        # spec.
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][1]["loop_device"]
        spec["file"] = "file"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LoopDevice")
        self.assertSetEqual(context.exception.keys, {"file"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][1]["loop_device"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LoopDevice")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["gpt_partition_table"]
        spec = spec["gpt_partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["files"][1]["loop_device"]
        del spec["name"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LoopDevice")
        self.assertSetEqual(context.exception.keys, {"name"})


class ParseLvmPhysicalVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # lvm_physical_volume spec.
        spec = self.spec["physical_devices"][2]["lvm_physical_volume"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmPhysicalVolume")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][2]["lvm_physical_volume"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmPhysicalVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][2]["lvm_physical_volume"]
        del spec["name"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmPhysicalVolume")
        self.assertSetEqual(context.exception.keys, {"name"})


class ParseLvmLogicalVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # lvm_logical_volume spec.
        spec = self.spec["lvm_volume_groups"][0]["lvm_logical_volumes"][0]
        spec["lvm_volume_group"] = "lvm_volume_group"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(context.exception.keys, {"lvm_volume_group"})

    def test_illegal_key_2(self):
        spec = self.spec["lvm_volume_groups"][0]["lvm_logical_volumes"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["lvm_volume_groups"][0]["lvm_logical_volumes"][0]
        del spec["name"]
        del spec["size"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(context.exception.keys, {"name", "size"})

    def test_exclusive_keys(self):
        spec = self.spec["lvm_volume_groups"][0]["lvm_logical_volumes"][0]
        spec["lvm_poolmetadata_volume"] = "lvm_poolmetadata_volume"
        spec["lvm_cachepool_volume"] = "lvm_cachepool_volume"
        spec["lvm_thinpool_volume"] = "lvm_thinpool_volume"

        with self.assertRaises(FoundIncompatibleKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(
            context.exception.keys,
            {
                "lvm_poolmetadata_volume",
                "lvm_cachepool_volume",
                "lvm_thinpool_volume",
            },
        )
