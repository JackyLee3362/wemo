import re
from logging import Logger, getLogger
from pathlib import Path


class Decrypter:
    def __init__(
        self, src_dir: Path = None, dst_dir: Path = None, logger: Logger = None
    ):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.logger = logger or getLogger(__name__)

    def decrypt(self, *args, **kwargs):
        raise NotImplementedError("Not Implemented")

    def get_months_by_existing_dir(self):
        res = []
        pattern = re.compile(r"^20\d{2}-[01][0-9]$")
        for file in self.src_dir.iterdir():
            if file.is_dir() and pattern.match(file.name) is not None:
                res.append(file.name)
        return res
