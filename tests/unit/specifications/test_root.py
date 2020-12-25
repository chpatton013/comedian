import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import Root


class RootTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            Root(),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("/", self.specification.name)
        self.assertListEqual([], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, "/"),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["mkdir", "--parents", "tmp_dir/etc"]),
            Command(["truncate", "--size=0", "tmp_dir/etc/fstab"]),
            Command(["chmod", "0644", "tmp_dir/etc/fstab"]),
            Command(["chown", "root:root", "tmp_dir/etc/fstab"]),
            Command(["truncate", "--size=0", "tmp_dir/etc/crypttab"]),
            Command(["chmod", "0644", "tmp_dir/etc/crypttab"]),
            Command(["chown", "root:root", "tmp_dir/etc/crypttab"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_post_apply_commands(self):
        expected = [
            Command(["mkdir", "--parents", "media_dir/etc"]),
            Command(
                [
                    "cp",
                    "tmp_dir/etc/fstab",
                    "media_dir/etc/fstab",
                    "--preserve=mode,ownership",
                ]
            ),
            Command(
                [
                    "cp",
                    "tmp_dir/etc/crypttab",
                    "media_dir/etc/crypttab",
                    "--preserve=mode,ownership",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.post_apply(self.context)),
        )

    def test_up_commands(self):
        self.assertIsNone(self.specification.up)

    def test_pre_down_commands(self):
        self.assertIsNone(self.specification.pre_down)

    def test_down_commands(self):
        self.assertIsNone(self.specification.down)
