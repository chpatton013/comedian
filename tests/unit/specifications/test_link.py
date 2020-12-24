import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import Link


class LinkTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            Link(
                name="name",
                filesystem="filesystem",
                relative_path="relative_path",
                source="source",
                owner="owner",
                group="group",
                mode="mode",
                symbolic=False,
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["filesystem"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("filesystem", self.specification.filesystem)
        self.assertEqual("relative_path", self.specification.relative_path)
        self.assertEqual("source", self.specification.source)
        self.assertEqual("owner", self.specification.owner)
        self.assertEqual("group", self.specification.group)
        self.assertEqual("mode", self.specification.mode)
        self.assertFalse(self.specification.symbolic)

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
            Command(["ln", "--force", "source", "media_dir/name"]),
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


class SymbolicLinkTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            Link(
                name="name",
                filesystem="filesystem",
                relative_path="relative_path",
                source="source",
                owner="owner",
                group="group",
                mode="mode",
                symbolic=True,
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["filesystem"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("filesystem", self.specification.filesystem)
        self.assertEqual("relative_path", self.specification.relative_path)
        self.assertEqual("source", self.specification.source)
        self.assertEqual("owner", self.specification.owner)
        self.assertEqual("group", self.specification.group)
        self.assertEqual("mode", self.specification.mode)
        self.assertTrue(self.specification.symbolic)

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
            Command(["ln", "--force", "--symbolic", "source", "media_dir/name"]),
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
