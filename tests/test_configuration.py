import unittest

from context import comedian

from comedian.configuration import Configuration


class ConfigurationTest(unittest.TestCase):
    def setUp(self):
        self.configuration = Configuration(
            dd_bs="dd_bs",
            random_device="random_device",
            media_dir="media_dir",
            tmp_dir="tmp_dir",
        )

    def test_values(self):
        self.assertEqual("dd_bs", self.configuration.dd_bs)
        self.assertEqual("random_device", self.configuration.random_device)
        self.assertEqual("media_dir", self.configuration.media_dir)
        self.assertEqual("tmp_dir", self.configuration.tmp_dir)

    def test_paths(self):
        self.assertEqual(
            "media_dir/path",
            self.configuration.media_path("path"),
        )
        self.assertEqual("tmp_dir/path", self.configuration.tmp_path("path"))
