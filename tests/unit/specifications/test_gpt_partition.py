import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import GptPartition


class GptPartitionTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            GptPartition(
                name="name",
                partition_table="partition_table",
                align=None,
                number=1,
                type="type",
                start="start",
                end="end",
                label="label",
                unit="unit",
                flags=["flags"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["partition_table"],
                             self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual(1, self.specification.number)
        self.assertEqual("type", self.specification.type)
        self.assertEqual("start", self.specification.start)
        self.assertEqual("end", self.specification.end)
        self.assertEqual("label", self.specification.label)
        self.assertEqual("unit", self.specification.unit)
        self.assertEqual(["flags"], self.specification.flags)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink("partition_table", "1"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command([
                "parted",
                "--script",
                "--",
                "partition_table",
                "mkpart",
                "type",
                "start",
                "end",
                "name",
                "1",
                "label",
                "unit",
                "unit",
                "set",
                "1",
                "flags",
                "on",
            ]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )
