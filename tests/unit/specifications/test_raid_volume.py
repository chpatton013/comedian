import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import RaidVolume


class RaidVolumeTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            RaidVolume(
                name="name",
                devices=["device"],
                level="level",
                metadata="metadata",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual(["device"], self.specification.devices)
        self.assertEqual("level", self.specification.level)
        self.assertEqual("metadata", self.specification.metadata)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/md/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(
                [
                    "mdadm",
                    "--create",
                    "--name=name",
                    "--level=level",
                    "--metadata=metadata",
                    "--raid-devices=1",
                    "/dev/md/name",
                    "device",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_up_commands(self):
        expected = [
            Command(["mdadm", "--assemble", "/dev/md/name", "device"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.up(self.context)),
        )

    def test_down_commands(self):
        expected = [
            Command(["mdadm", "--stop", "/dev/md/name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )
