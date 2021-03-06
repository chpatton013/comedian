import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import Directory


class DirectoryTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            Directory(
                name="name",
                mount="mount",
                relative_path="relative_path",
                owner="owner",
                group="group",
                mode="mode",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["mount"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("mount", self.specification.mount)
        self.assertEqual("relative_path", self.specification.relative_path)
        self.assertEqual("owner", self.specification.owner)
        self.assertEqual("group", self.specification.group)
        self.assertEqual("mode", self.specification.mode)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink("mount", "relative_path"),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["mkdir", "--parents", "media_dir/name"]),
            Command(["chown", "owner:group", "media_dir/name"]),
            Command(["chmod", "mode", "media_dir/name"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_post_apply_commands(self):
        self.assertIsNone(self.specification.post_apply)

    def test_up_commands(self):
        self.assertIsNone(self.specification.up)

    def test_pre_down_commands(self):
        self.assertIsNone(self.specification.pre_down)

    def test_down_commands(self):
        self.assertIsNone(self.specification.down)
