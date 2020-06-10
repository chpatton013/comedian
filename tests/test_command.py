import unittest

from context import comedian

from comedian.command import Command, CommandContext
from comedian.configuration import Configuration
from comedian.graph import Graph


class CommandTest(unittest.TestCase):
    def test_command(self):
        self.assertListEqual(["a"], Command(["a"]).cmd)

    def test_command_context(self):
        configuration = Configuration(
            shell="shell",
            dd_bs="dd_bs",
            random_device="random_device",
            media_dir="media_dir",
            tmp_dir="tmp_dir",
        )
        graph = Graph([])
        context = CommandContext(configuration, graph)

        self.assertEqual(configuration, context.config)
        self.assertEqual(graph, context.graph)
