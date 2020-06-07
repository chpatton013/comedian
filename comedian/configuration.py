import os

from .traits import __Debug__, __Eq__


class Configuration(__Debug__, __Eq__):
    def __init__(
        self,
        dd_bs: str = "16M",
        random_device: str = "/dev/random",
        media_dir: str = "/mnt/comedian",
        tmp_dir: str = "/tmp/comedian",
    ):
        self.dd_bs = dd_bs
        self.random_device = random_device
        self.media_dir = media_dir
        self.tmp_dir = tmp_dir

    def media_path(self, path: str) -> str:
        return _join(self.media_dir, path)

    def tmp_path(self, path: str) -> str:
        return _join(self.tmp_dir, path)


def _join(head, *tail):
    joined = _join(*tail) if tail else ""
    if joined.startswith(os.path.sep):
        joined = joined[len(os.path.sep):]
    return head + os.path.sep + joined if joined else head
