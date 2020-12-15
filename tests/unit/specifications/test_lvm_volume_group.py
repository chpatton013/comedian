import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import LvmVolumeGroup


class LvmVolumeGroupTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            LvmVolumeGroup(
                name="name",
                lvm_physical_volumes=["lvm_physical_volume"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["lvm_physical_volume"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual(
            ["lvm_physical_volume"], self.specification.lvm_physical_volumes
        )

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_post_apply_commands(self):
        self.assertIsNone(self.specification.post_apply)

    def test_apply_commands(self):
        expected = [
            Command(["vgcreate", "name", "lvm_physical_volume"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_up_commands(self):
        expected = [
            Command(["vgchange", "--activate", "y", "name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.up(self.context)),
        )

    def test_pre_down_commands(self):
        self.assertIsNone(self.specification.pre_down)

    def test_down_commands(self):
        expected = [
            Command(["vgchange", "--activate", "n", "name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )
