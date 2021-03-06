import unittest

from context import comedian, SpecificationTestBase  # pylint: disable=W0611

from comedian.command import Command
from comedian.graph import ResolveLink
from comedian.specifications import CryptVolume


class CryptVolumeTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            CryptVolume(
                name="name",
                device="device",
                identify="device",
                type="type",
                keyfile="keyfile",
                keysize="keysize",
                password="password",
                options=["opt", "ions"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertFalse(self.specification.ephemeral_keyfile())
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual(["keyfile"], self.specification.references)
        self.assertEqual("device", self.specification.device)
        self.assertEqual("device", self.specification.identify)
        self.assertEqual("type", self.specification.type)
        self.assertEqual("keyfile", self.specification.keyfile)
        self.assertEqual("keysize", self.specification.keysize)
        self.assertEqual("password", self.specification.password)
        self.assertListEqual(["opt", "ions"], self.specification.options)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/mapper/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        crypttab_lines = "\\n".join(
            [
                "",
                "# name (originally device)",
                "name\\tdevice\\tkeyfile\\topt,ions",
            ]
        )

        expected = [
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=random_device",
                    "open",
                    "device",
                    "randomize_name",
                    "--type=plain",
                ]
            ),
            Command(
                [
                    "shell",
                    "-c",
                    "'dd status=progress conv=sync,noerror if=/dev/zero of=/dev/mapper/randomize_name bs=dd_bs || true'",
                ]
            ),
            Command(["sync"]),
            Command(["cryptsetup", "--batch-mode", "close", "randomize_name"]),
            Command(["mkdir", "--parents", "tmp_dir"]),
            Command(
                [
                    "dd",
                    "status=progress",
                    "conv=sync,noerror",
                    "if=random_device",
                    "of=tmp_dir/keyfile",
                    "bs=keysize",
                    "count=1",
                ]
            ),
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=tmp_dir/keyfile",
                    "luksFormat",
                    "--type=type",
                    "device",
                ]
            ),
            Command(
                [
                    "shell",
                    "-c",
                    "'echo password | cryptsetup --batch-mode --key-file=tmp_dir/keyfile luksAddKey device'",
                ]
            ),
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=tmp_dir/keyfile",
                    "open",
                    "device",
                    "name",
                ]
            ),
            Command(
                [
                    "shell",
                    "-c",
                    "'echo -e \"{}\" >> tmp_dir/etc/crypttab'".format(crypttab_lines),
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_post_apply_commands(self):
        expected = [
            Command(
                [
                    "cp",
                    "tmp_dir/keyfile",
                    "media_dir/keyfile",
                    "--preserve=mode,ownership",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.post_apply(self.context)),
        )

    def test_up_commands(self):
        expected = [
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=tmp_dir/keyfile",
                    "open",
                    "device",
                    "name",
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
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "close",
                    "name",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )


class EphemeralCryptVolumeTest(SpecificationTestBase, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        SpecificationTestBase.__init__(
            self,
            CryptVolume(
                name="name",
                device="device",
                identify="device",
                type="type",
                keyfile="/keyfile",
                keysize=None,
                password=None,
                options=["opt", "ions"],
            ),
        )
        unittest.TestCase.__init__(self, *args, **kwargs)

    def test_properties(self):
        self.assertTrue(self.specification.ephemeral_keyfile())
        self.assertEqual("name", self.specification.name)
        self.assertListEqual(["device"], self.specification.dependencies)
        self.assertListEqual([], self.specification.references)
        self.assertEqual("device", self.specification.device)
        self.assertEqual("device", self.specification.identify)
        self.assertEqual("type", self.specification.type)
        self.assertEqual("/keyfile", self.specification.keyfile)
        self.assertIsNone(self.specification.keysize)
        self.assertIsNone(self.specification.password)
        self.assertListEqual(["opt", "ions"], self.specification.options)

    def test_resolve(self):
        self.assertEqual(
            ResolveLink(None, "/dev/mapper/name"),
            self.specification.resolve_device(),
        )
        self.assertEqual(
            ResolveLink(None, None),
            self.specification.resolve_path(),
        )

    def test_apply_commands(self):
        crypttab_lines = "\\n".join(
            [
                "",
                "# name (originally device)",
                "name\\tdevice\\t/keyfile\\topt,ions",
            ]
        )

        expected = [
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=/keyfile",
                    "open",
                    "device",
                    "name",
                    "--type=type",
                ]
            ),
            Command(
                [
                    "shell",
                    "-c",
                    "'echo -e \"{}\" >> tmp_dir/etc/crypttab'".format(crypttab_lines),
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.apply(self.context)),
        )

    def test_post_apply_commands(self):
        expected = []
        self.assertListEqual(
            expected,
            list(self.specification.post_apply(self.context)),
        )

    def test_up_commands(self):
        expected = [
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "--key-file=/keyfile",
                    "open",
                    "device",
                    "name",
                    "--type=type",
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
            Command(
                [
                    "cryptsetup",
                    "--batch-mode",
                    "close",
                    "name",
                ]
            ),
        ]
        self.assertListEqual(
            expected,
            list(self.specification.down(self.context)),
        )
