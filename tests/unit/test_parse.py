import copy
import unittest

from context import comedian  # pylint: disable=W0611

from comedian.specifications import (
    CryptVolume,
    Directory,
    File,
    Filesystem,
    Link,
    LoopDevice,
    LvmLogicalVolume,
    LvmPhysicalVolume,
    LvmVolumeGroup,
    Mount,
    Partition,
    PartitionTable,
    PhysicalDevice,
    RaidVolume,
    Root,
    SwapVolume,
)

from comedian.parse import (
    FoundIllegalKeysError,
    FoundIncompatibleKeysError,
    MissingRequiredKeysError,
    parse,
)

_FSROOT_SPEC = {
    "name": "fsroot",
    "type": "ext4",
    "mount": {
        "mountpoint": "/",
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
                "crypt_volume": {
                    "name": "cryptswap1",
                    "type": "luks2",
                    "keyfile": "/dev/urandom",
                    "options": ["swap", "cipher=aes-cbc-essiv:sha256", "size=256"],
                    "swap_volume": {"name": "swap1"},
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
                        "type": "ext4",
                        "mount": {
                            "mountpoint": "/loop",
                            "options": ["noatime"],
                        },
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
        "links": [
            {
                "relative_path": "hardlink",
                "source": "/keyfile",
            },
            {
                "relative_path": "symlink",
                "source": "/randomfile",
                "symbolic": True,
            },
        ],
    },
}

SPEC = {
    "physical_devices": [
        {
            "name": "sda",
            "partition_table": {
                "type": "gpt",
                "glue": "p",
                "partitions": [
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
                            "keyfile": "fsroot:mount:keyfile",
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
    "raid_volumes": [
        {
            "name": "raidarray",
            "devices": ["sdc"],
            "level": "1",
            "metadata": "1.2",
            "filesystem": {
                "name": "fsraid",
                "type": "ext4",
                "mount": {
                    "mountpoint": "/raid",
                },
            },
        }
    ],
    "lvm_volume_groups": [
        {
            "name": "lvmvg",
            "lvm_physical_volumes": ["lvmpv"],
            "lvm_logical_volumes": [
                {
                    "name": "lvmlv",
                    "crypt_volume": {
                        "name": "crypt_lvm",
                        "type": "luks2",
                        "keyfile": "fsroot:mount:randomfile",
                        "keysize": "2048",
                    },
                }
            ],
        }
    ],
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
            PartitionTable(name="sda:pt", device="sda", type="gpt", glue="p"),
            Partition(
                name="sda:pt:1",
                partition_table="sda:pt",
                align=None,
                number=1,
                type="primary",
                start="1",
                end="3",
                label=None,
                unit=None,
                flags=["bios_grub"],
            ),
            Partition(
                name="sda:pt:2",
                partition_table="sda:pt",
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
                device="sda:pt:2",
                identify="partuuid",
                type="luks2",
                keyfile="fsroot:mount:keyfile",
                keysize="2048",
                password="hunter2",
                options=[],
            ),
            Filesystem(
                name="fsroot",
                device="cryptroot",
                type="ext4",
                options=[],
            ),
            Mount(
                name="fsroot:mount",
                device="fsroot",
                identify="device",
                mountpoint="/",
                type="ext4",
                options=[],
                dump_frequency=None,
                fsck_order=None,
            ),
            Directory(
                name="fsroot:mount:raid",
                mount="fsroot:mount",
                relative_path="raid",
                owner="root",
                group="root",
                mode="0755",
            ),
            Directory(
                name="fsroot:mount:loop",
                mount="fsroot:mount",
                relative_path="loop",
                owner=None,
                group=None,
                mode=None,
            ),
            File(
                name="fsroot:mount:swapfile",
                mount="fsroot:mount",
                relative_path="swapfile",
                owner="root",
                group="root",
                mode="0755",
                size="10",
            ),
            CryptVolume(
                name="cryptswap1",
                device="fsroot:mount:swapfile",
                identify="device",
                type="luks2",
                keyfile="/dev/urandom",
                keysize=None,
                password=None,
                options=["swap", "cipher=aes-cbc-essiv:sha256", "size=256"],
            ),
            SwapVolume(
                name="swap1",
                device="cryptswap1",
                identify="device",
                label=None,
                pagesize=None,
                uuid=None,
            ),
            File(
                name="fsroot:mount:loopfile",
                mount="fsroot:mount",
                relative_path="loopfile",
                owner=None,
                group=None,
                mode=None,
                size="10",
            ),
            LoopDevice(
                name="loop",
                file="fsroot:mount:loopfile",
                args=["-e", "18"],
            ),
            Filesystem(
                name="fsloop",
                device="loop",
                type="ext4",
                options=[],
            ),
            Mount(
                name="fsloop:mount",
                device="fsloop",
                identify="device",
                mountpoint="/loop",
                type="ext4",
                options=["noatime"],
                dump_frequency=None,
                fsck_order=None,
            ),
            File(
                name="fsroot:mount:randomfile",
                mount="fsroot:mount",
                relative_path="randomfile",
                owner=None,
                group=None,
                mode=None,
                size=None,
            ),
            File(
                name="fsroot:mount:keyfile",
                mount="fsroot:mount",
                relative_path="keyfile",
                owner=None,
                group=None,
                mode=None,
                size=None,
            ),
            Link(
                name="fsroot:mount:hardlink",
                mount="fsroot:mount",
                relative_path="hardlink",
                source="/keyfile",
                owner=None,
                group=None,
                mode=None,
                symbolic=False,
            ),
            Link(
                name="fsroot:mount:symlink",
                mount="fsroot:mount",
                relative_path="symlink",
                source="/randomfile",
                owner=None,
                group=None,
                mode=None,
                symbolic=True,
            ),
            PhysicalDevice("sdb"),
            SwapVolume(
                name="swap2",
                device="sdb",
                identify="uuid",
                label=None,
                pagesize=None,
                uuid=None,
            ),
            PhysicalDevice("sdc"),
            LvmPhysicalVolume(name="lvmpv", device="sdc"),
            PhysicalDevice("sdd"),
            LvmVolumeGroup(name="lvmvg", lvm_physical_volumes=["lvmpv"]),
            LvmLogicalVolume(
                name="lvmlv",
                size=None,
                extents=None,
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
                identify="device",
                type="luks2",
                keyfile="fsroot:mount:randomfile",
                keysize="2048",
                password=None,
                options=[],
            ),
            RaidVolume(
                name="raidarray",
                devices=["sdc"],
                level="1",
                metadata="1.2",
            ),
            Filesystem(
                name="fsraid",
                device="raidarray",
                type="ext4",
                options=[],
            ),
            Mount(
                name="fsraid:mount",
                device="fsraid",
                identify="device",
                mountpoint="/raid",
                type="ext4",
                options=[],
                dump_frequency=None,
                fsck_order=None,
            ),
        ]

        self.assertListEqual(list(parse(self.spec)), expected)


class ParseCryptVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the crypt_volume
        # spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]
        del spec["name"]
        del spec["type"]
        del spec["keyfile"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(context.exception.keys, {"name", "type", "keyfile"})

    def test_exclusive_keys_1(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]
        spec["keyfile"] = "keyfile"
        del spec["keysize"]

        with self.assertRaises(FoundIncompatibleKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(
            context.exception.keys,
            {"keyfile", "keysize"},
        )

    def test_exclusive_keys_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]
        spec["keyfile"] = "/keyfile"
        spec["keysize"] = "swap_volume"

        with self.assertRaises(FoundIncompatibleKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "CryptVolume")
        self.assertSetEqual(
            context.exception.keys,
            {"keyfile", "keysize"},
        )


class ParseFilesystemTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the filesystem
        # spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        del spec["name"]
        del spec["type"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Filesystem")
        self.assertSetEqual(context.exception.keys, {"name", "type"})


class ParseDirectoryTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the directory
        # spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["directories"][0]
        spec["name"] = "name"
        spec["mount"] = "mount"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"name", "mount"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["directories"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["directories"][0]
        del spec["relative_path"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Directory")
        self.assertSetEqual(context.exception.keys, {"relative_path"})


class ParseFileTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the file spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]
        spec["name"] = "name"
        spec["mount"] = "mount"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"name", "mount"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]
        del spec["relative_path"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(context.exception.keys, {"relative_path"})

    def test_exclusive_keys(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]
        spec["loop_device"] = "loop_device"
        spec["crypt_volume"] = "crypt_volume"
        spec["swap_volume"] = "swap_volume"

        with self.assertRaises(FoundIncompatibleKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "File")
        self.assertSetEqual(
            context.exception.keys,
            {"loop_device", "crypt_volume", "swap_volume"},
        )


class ParseLinkTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the link spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["links"][0]
        spec["name"] = "name"
        spec["mount"] = "mount"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Link")
        self.assertSetEqual(context.exception.keys, {"name", "mount"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["links"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Link")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["links"][0]
        del spec["relative_path"]
        del spec["source"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Link")
        self.assertSetEqual(context.exception.keys, {"relative_path", "source"})


class ParseLoopDeviceTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the loop_device
        # spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][1]["loop_device"]
        spec["file"] = "file"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LoopDevice")
        self.assertSetEqual(context.exception.keys, {"file"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][1]["loop_device"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LoopDevice")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][1]["loop_device"]
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

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(context.exception.keys, {"name"})

    def test_exclusive_keys_1(self):
        spec = self.spec["lvm_volume_groups"][0]["lvm_logical_volumes"][0]
        spec["size"] = "size"
        spec["extents"] = "extents"

        with self.assertRaises(FoundIncompatibleKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "LvmLogicalVolume")
        self.assertSetEqual(
            context.exception.keys,
            {"size", "extents"},
        )

    def test_exclusive_keys_2(self):
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


class ParsePartitionTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # partition spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][0]
        spec["name"] = "name"
        spec["partition_table"] = "partition_table"
        spec["number"] = 1

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Partition")
        self.assertSetEqual(
            context.exception.keys, {"name", "partition_table", "number"}
        )

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][0]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Partition")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][0]
        del spec["type"]
        del spec["start"]
        del spec["end"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "Partition")
        self.assertSetEqual(context.exception.keys, {"type", "start", "end"})


class ParsePartitionTableTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the
        # partition_table spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec["name"] = "name"
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PartitionTable")
        self.assertSetEqual(context.exception.keys, {"name", "device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PartitionTable")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key_1(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        del spec["type"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PartitionTable")
        self.assertSetEqual(context.exception.keys, {"type"})

    def test_missing_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        del spec["partitions"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "PartitionTable")
        self.assertSetEqual(context.exception.keys, {"partitions"})


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


class ParseSwapVolumeTest(ParseTestBase):
    def test_illegal_key_1(self):
        # These keys are restricted before parsing the rest of the swap_volume
        # spec.
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]["crypt_volume"]["swap_volume"]
        spec["device"] = "device"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"device"})

    def test_illegal_key_2(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]["crypt_volume"]["swap_volume"]
        spec["foo"] = "bar"

        with self.assertRaises(FoundIllegalKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"foo"})

    def test_missing_key(self):
        spec = self.spec["physical_devices"][0]["partition_table"]
        spec = spec["partitions"][1]["crypt_volume"]["filesystem"]
        spec = spec["mount"]["files"][0]["crypt_volume"]["swap_volume"]
        del spec["name"]

        with self.assertRaises(MissingRequiredKeysError) as context:
            list(parse(self.spec))
        self.assertEqual(context.exception.name, "SwapVolume")
        self.assertSetEqual(context.exception.keys, {"name"})
