import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import File


class FileTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            File(
                name="name",
                filesystem="filesystem",
                relative_path="relative_path",
                owner="owner",
                group="group",
                mode="mode",
                size="size",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["filesystem"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("filesystem", self.specification.filesystem)
        self.assertEqual("relative_path", self.specification.relative_path)
        self.assertEqual("owner", self.specification.owner)
        self.assertEqual("group", self.specification.group)
        self.assertEqual("mode", self.specification.mode)
        self.assertEqual("size", self.specification.size)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink("filesystem", "relative_path"),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["mkdir", "--parents", "media_dir"]),
            Command(["fallocate", "--length", "size", "media_dir/name"]),
            Command(["chown", "owner:group", "media_dir/name"]),
            Command(["chmod", "mode", "media_dir/name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )
