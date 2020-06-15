import unittest

from context import comedian, SpecificationTestBase

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import PhysicalDevice


class PhysicalDeviceTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            PhysicalDevice(name="name"),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertEqual("name", self.specification.name)
        self.assertListEqual([], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )
