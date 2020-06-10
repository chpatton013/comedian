import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import GptPartitionTable


class GptPartitionTableTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            GptPartitionTable(
                name="name",
                device="device",
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("device", self.specification.device)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink("device", None),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        expected = [
            Command(["parted", "--script", "device", "mklabel", "gpt"]),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )
