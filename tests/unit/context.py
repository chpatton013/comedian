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
import comedian  # pylint: disable=C0413

from comedian.command import CommandContext  # pylint: disable=C0413
from comedian.configuration import Configuration  # pylint: disable=C0413
from comedian.graph import Graph, ResolveLink  # pylint: disable=C0413
from comedian.specification import Specification  # pylint: disable=C0413

__all__ = ["SpecificationTestBase", "comedian"]


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
        graph = Graph(
            [
                TestSpecification("device"),
                TestSpecification("file"),
                TestSpecification("filesystem"),
                TestSpecification("keyfile"),
                TestSpecification("lvm_logical_volume"),
                TestSpecification("lvm_physical_volume"),
                TestSpecification("lvm_cachedata_volume"),
                TestSpecification("lvm_cachemeta_volume"),
                TestSpecification("mountpoint"),
                TestSpecification("name"),
                TestSpecification("partition_table"),
            ]
        )
        self.context = CommandContext(configuration, graph)
        self.specification = specification

    @abstractmethod
    def test_properties(self):
        pass

    @abstractmethod
    def test_resolve(self):
        pass

    @abstractmethod
    def test_apply_commands(self):
        pass

    @abstractmethod
    def test_post_apply_commands(self):
        pass

    @abstractmethod
    def test_up_commands(self):
        pass

    @abstractmethod
    def test_pre_down_commands(self):
        pass

    @abstractmethod
    def test_down_commands(self):
        pass
