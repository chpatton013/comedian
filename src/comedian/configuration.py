import os

from comedian.traits import DebugMixin, EqMixin


class Configuration(DebugMixin, EqMixin):
    def __init__(
        self,
        shell: str,
        dd_bs: str,
        random_device: str,
        media_dir: str,
        tmp_dir: str,
    ):
        self.shell = shell
        self.dd_bs = dd_bs
        self.random_device = random_device
        self.media_dir = media_dir
        self.tmp_dir = tmp_dir

    def media_path(self, path: str) -> str:
        return _join(self.media_dir, path)

    def tmp_path(self, path: str) -> str:
        return _join(self.tmp_dir, path)


def _join(root: str, path: str) -> str:
    if os.path.isabs(path):
        path = path[1:]
    return os.path.join(root, path)
