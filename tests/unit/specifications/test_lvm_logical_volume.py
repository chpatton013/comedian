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
                size="size",
                extents="extents",
                type="type",
                args=["args"],
                lvm_volume_group="lvm_volume_group",
                lvm_physical_volumes=["lvm_physical_volume"],
                lvm_poolmetadata_volume="lvm_poolmetadata_volume",
                lvm_cachepool_volume="lvm_cachepool_volume",
                lvm_thinpool_volume="lvm_thinpool_volume",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(
            [
                "lvm_volume_group",
                "lvm_physical_volume",
                "lvm_poolmetadata_volume",
                "lvm_cachepool_volume",
                "lvm_thinpool_volume",
            ],
            self.specification.dependencies,
        )
        self.assertListEqual([], self.specification.references)
        self.assertEqual("size", self.specification.size)
        self.assertEqual("extents", self.specification.extents)
        self.assertEqual("type", self.specification.type)
        self.assertListEqual(["args"], self.specification.args)
        self.assertEqual("lvm_volume_group", self.specification.lvm_volume_group)
        self.assertEqual(
            ["lvm_physical_volume"],
            self.specification.lvm_physical_volumes,
        )
        self.assertEqual(
            "lvm_poolmetadata_volume",
            self.specification.lvm_poolmetadata_volume,
        )
        self.assertEqual(
            "lvm_cachepool_volume",
            self.specification.lvm_cachepool_volume,
        )
        self.assertEqual(
            "lvm_thinpool_volume",
            self.specification.lvm_thinpool_volume,
        )

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
            Command(
                [
                    "lvcreate",
                    "--name=name",
                    "--size=size",
                    "--extents=extents",
                    "--type=type",
                    "--poolmetadata=lvm_poolmetadata_volume",
                    "--cachepool=lvm_cachepool_volume",
                    "--thinpool=lvm_thinpool_volume",
                    "args",
                    "lvm_volume_group",
                    "lvm_physical_volume",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )
