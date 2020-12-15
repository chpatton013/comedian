import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import PartitionTable


class PartitionTableTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            PartitionTable(
                name="name",
                device="device",
                type="type",
                glue="glue",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("device", self.specification.device)
        self.assertEqual("glue", self.specification.glue)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink("device", None, "glue"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["parted", "--script", "--", "device", "mklabel", "type"]),
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
