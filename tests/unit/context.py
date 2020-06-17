import os
import sys
from abc import ABC, abstractmethod

# Add the parent directory to the path so we can import the comedian module
# directly instead of relying on it to be installed in site-packages.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")),
)

# Import and expose the comedian module for each test file.
import comedian

from comedian.command import CommandContext
from comedian.configuration import Configuration
from comedian.graph import Graph, ResolveLink
from comedian.specification import Specification

__all__ = ("SpecificationTestBase", "comedian")


class TestSpecification(Specification):
    def __init__(self, name: str):
        super().__init__(name, [])

    def resolve_device(self) -> ResolveLink:
        return ResolveLink(None, self.name)

    def resolve_path(self) -> ResolveLink:
        return ResolveLink(None, self.name)


class SpecificationTestBase(ABC):
    def __init__(self, specification: Specification):
        super().__init__()

        configuration = Configuration(
            shell="shell",
            dd_bs="dd_bs",
            random_device="random_device",
            media_dir="media_dir",
            tmp_dir="tmp_dir",
        )
        graph = Graph([
            TestSpecification("device"),
            TestSpecification("file"),
            TestSpecification("filesystem"),
            TestSpecification("keyfile"),
            TestSpecification("lvm_logical_volume"),
            TestSpecification("lvm_physical_volume"),
            TestSpecification("mountpoint"),
            TestSpecification("name"),
            TestSpecification("partition_table"),
        ])
        self.context = CommandContext(configuration, graph)
        self.specification = specification

    @abstractmethod
    def test_properties(self):
        pass

    @abstractmethod
    def test_resolve(self):
        pass

    def test_apply_commands(self):
        self.assertIsNone(self.specification.apply)

    def test_post_apply_commands(self):
        self.assertIsNone(self.specification.post_apply)

    def test_up_commands(self):
        self.assertIsNone(self.specification.up)

    def test_down_commands(self):
        self.assertIsNone(self.specification.down)
