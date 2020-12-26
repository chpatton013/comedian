import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import SwapVolume


class SwapVolumeTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            SwapVolume(
                name="name",
                device="device",
                identify="device",
                label="label",
                pagesize="pagesize",
                uuid="uuid",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("device", self.specification.device)
        self.assertEqual("device", self.specification.identify)
        self.assertEqual("label", self.specification.label)
        self.assertEqual("pagesize", self.specification.pagesize)
        self.assertEqual("uuid", self.specification.uuid)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        fstab_lines = "\\n".join(
            [
                "",
                "# name (originally device)",
                "device\\tnone\\tswap\\tdefaults\\t0\\t0",
            ]
        )

        expected = [
            Command(
                [
                    "mkswap",
                    "device",
                    "--label=label",
                    "--pagesize=pagesize",
                    "--uuid=uuid",
                ]
            ),
            Command(["swapon", "device"]),
            Command(
                [
                    "shell",
                    "-c",
                    f'echo -e "{fstab_lines}" >> tmp_dir/etc/fstab',
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_post_apply_commands(self):
        self.assertIsNone(self.specification.post_apply)

    def test_up_commands(self):
        expected = [
            Command(["swapon", "device"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.up(self.context)),
        )

    def test_pre_down_commands(self):
        self.assertIsNone(self.specification.pre_down)

    def test_down_commands(self):
        expected = [
            Command(["swapoff", "device"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )
