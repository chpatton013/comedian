import json
import os
import stat
import subprocess
import tempfile
import unittest
from typing import Dict, Iterable

COMEDIAN_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
RUNTIME_DATA_DIR = os.path.join(COMEDIAN_ROOT, "data")
SRC_DIR = os.path.join(COMEDIAN_ROOT, "src")
TEST_CASES_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "cases")
)


def size_to_bytes(size: str) -> int:
    magnitude = {
        "TB": 2**40,
        "GB": 2**30,
        "MB": 2**20,
        "KB": 2**10,
        "B": 1,
    }
    for suffix, multiplier in magnitude.items():
        if size.endswith(suffix):
            return int(size[:-len(suffix)]) * multiplier
    return int(size)


def render_template(template: str, replacements: Dict[str, str]) -> str:
    content = template
    for key, value in replacements.items():
        content = content.replace("{{" + key + "}}", value)
    return content


def comedian_command(
    comedian: str, config: str, mode: str, action: str, spec: str
):
    return f"python {comedian} --config={config} --mode={mode} {action} {spec}"


def pipeline(*commands: Iterable[str]) -> str:
    return " | ".join(commands)


class TestCase:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        with open(self.devices_path(), "r") as f:
            self.devices = json.load(f)

    def config_path(self) -> str:
        return os.path.join(self.path, "config.json")

    def devices_path(self) -> str:
        return os.path.join(self.path, "devices.json")

    def spec_path(self) -> str:
        return os.path.join(self.path, "spec.json")

    def after_apply_path(self) -> str:
        return os.path.join(self.path, "after_apply")

    def after_down_path(self) -> str:
        return os.path.join(self.path, "after_down")

    def after_up_path(self) -> str:
        return os.path.join(self.path, "after_up")


class TempFile:
    def __init__(self, content: str, **kwargs):
        fd, self.path = tempfile.mkstemp(text=True, **kwargs)
        os.write(fd, content.encode("utf-8"))
        os.chmod(fd, stat.S_IREAD | stat.S_IWRITE | stat.S_IXUSR)
        os.close(fd)

    def __del__(self):
        os.unlink(self.path)


class TempLoopDevice:
    def __init__(self, size: str):
        self.size = size
        self.path = None
        self.loop = None
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        if not self.path:
            _, self.path = tempfile.mkstemp()
            subprocess.check_call([
                "fallocate", "--offset", "0", "--length", self.size, self.path
            ])
        if not self.loop:
            self.loop = subprocess.check_output([
                "losetup", "--find", "--show", self.path
            ]).decode("utf-8").strip()

    def close(self):
        if self.loop:
            subprocess.check_call(["losetup", "--detach", self.loop])
            self.loop = None
        if self.path:
            subprocess.check_call(["rm", "--force", self.path])
            self.path = None


class TestRunner(unittest.TestCase, TestCase):
    def setUp(self):
        self.devices = {}
        self.resources = []
        for device in self._test_case.devices:
            loop = TempLoopDevice(str(size_to_bytes(device["size"])))
            name = os.path.relpath(loop.loop, start="/dev")
            self.devices[device["name"]] = name
            self.resources.append(loop)
        self.media_dir = tempfile.TemporaryDirectory()
        self.resources.append(self.media_dir)

    def find_config_file(self) -> str:
        if os.path.isfile(self._test_case.config_path()):
            return self._test_case.config_path()
        else:
            return os.path.join(RUNTIME_DATA_DIR, "default.config.json")

    def find_assertion_file(self, path) -> str:
        assertion_file = os.path.join(COMEDIAN_ROOT, path)
        return assertion_file if os.path.isfile(assertion_file) else ""

    def render_config_file(self) -> TempFile:
        config_file = self.find_config_file()
        with open(config_file, "r") as f:
            config_content = json.load(f)
        config_content["media_dir"] = self.media_dir.name
        return TempFile(json.dumps(config_content), suffix=".json")

    def render_spec_file(self) -> TempFile:
        spec_template_file = os.path.join(
            COMEDIAN_ROOT, self._test_case.spec_path()
        )
        with open(spec_template_file, "r") as f:
            spec_content = render_template(f.read(), self.devices)
        return TempFile(spec_content, suffix=".json")

    def render_integration_test_file(
        self, config_file: str, spec_file: str
    ) -> TempFile:
        after_apply_file = self.find_assertion_file(
            self._test_case.after_apply_path()
        )
        after_down_file = self.find_assertion_file(
            self._test_case.after_down_path()
        )
        after_up_file = self.find_assertion_file(
            self._test_case.after_up_path()
        )

        def _comedian_command(mode: str, action: str):
            return comedian_command(
                SRC_DIR,
                config_file,
                mode,
                action,
                spec_file,
            )

        content = [
            "#!/usr/bin/env bash",
            "set -xeuo pipefail",
        ]

        content.append(pipeline(_comedian_command("shell", "apply"), "bash"))
        if after_apply_file:
            content.append(after_apply_file)

        content.append(pipeline(_comedian_command("shell", "down"), "bash"))
        if after_down_file:
            content.append(after_down_file)

        content.append(pipeline(_comedian_command("shell", "up"), "bash"))
        if after_up_file:
            content.append(after_up_file)

        content.append(pipeline(_comedian_command("shell", "down"), "bash"))

        return TempFile("\n".join(content), suffix=".sh")


def make_test_fn():
    def test_fn(self):
        config_file = self.render_config_file()
        spec_file = self.render_spec_file()
        integration_test_file = self.render_integration_test_file(
            config_file.path, spec_file.path
        )

        subprocess.check_call([integration_test_file.path])

    return test_fn


def generate_test_cases(root):
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            yield TestCase(name, path)


for case in generate_test_cases(TEST_CASES_ROOT):
    classname = f"Test_{case.name}"
    globals()[classname] = type(
        classname,
        (TestRunner, ),
        {
            f"test_{case.name}": make_test_fn(),
            "_test_case": case,
        },
    )
