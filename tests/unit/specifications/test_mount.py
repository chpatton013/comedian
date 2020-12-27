import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import Mount


class MountTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            Mount(
                name="name",
                device="device",
                identify="device",
                mountpoint="mountpoint",
                type="type",
                options=["opt", "ions"],
                dump_frequency=1,
                fsck_order=2,
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["mountpoint", "device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("device", self.specification.device)
        self.assertEqual("device", self.specification.identify)
        self.assertEqual("mountpoint", self.specification.mountpoint)
        self.assertEqual("type", self.specification.type)
        self.assertEqual(["opt", "ions"], self.specification.options)
        self.assertEqual(1, self.specification.dump_frequency)
        self.assertEqual(2, self.specification.fsck_order)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink("device", None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink("mountpoint", None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        fstab_lines = "\\n".join(
            [
                "",
                "# name (originally device)",
                "device\\tmountpoint\\ttype\\topt,ions\\t1\\t2",
            ]
        )

        expected = [
            Command(
                [
                    "mount",
                    "--types",
                    "type",
                    "-o",
                    "opt,ions",
                    "device",
                    "media_dir/mountpoint",
                ]
            ),
            Command(
                [
                    "shell",
                    "-c",
                    "'echo -e \"{}\" >> tmp_dir/etc/fstab'".format(fstab_lines),
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
            Command(
                [
                    "mount",
                    "--types",
                    "type",
                    "-o",
                    "opt,ions",
                    "device",
                    "media_dir/mountpoint",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.up(self.context)),
        )

    def test_pre_down_commands(self):
        self.assertIsNone(self.specification.pre_down)

    def test_down_commands(self):
        expected = [
            Command(["umount", "media_dir/mountpoint"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )
