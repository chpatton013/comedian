import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import LoopDevice


class LoopDeviceTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            LoopDevice(
                name="name",
                file="file",
                args=["args"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["file"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("file", self.specification.file)
        self.assertEqual(["args"], self.specification.args)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["losetup", "args", "/dev/name", "file"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_up_commands(self):
        expected = [
            Command(["losetup", "args", "/dev/name", "file"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.up(self.context)),
        )

    def test_down_commands(self):
        expected = [
            Command(["losetup", "--detach", "/dev/name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )