import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import LvmLogicalVolume


class LvmLogicalVolumeTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            LvmLogicalVolume(
                name="name",
                lvm_volume_group="lvm_volume_group",
                size="size",
                lvm_physical_volumes=["lvm_physical_volume"],
                args=["args"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["lvm_volume_group", "lvm_physical_volume"],
                             self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual(
            "lvm_volume_group", self.specification.lvm_volume_group
        )
        self.assertEqual("size", self.specification.size)
        self.assertEqual(["lvm_physical_volume"],
                         self.specification.lvm_physical_volumes)
        self.assertEqual(["args"], self.specification.args)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink("lvm_volume_group", "name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command([
                "lvcreate",
                "--name",
                "name",
                "--size",
                "size",
                "args",
                "lvm_volume_group",
                "lvm_physical_volume",
            ]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )
