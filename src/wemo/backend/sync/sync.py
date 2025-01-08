import logging
import re
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Syncer:
    def __init__(
        self,
        src_dir: Optional[Path] = None,
        dst_dir: Optional[Path] = None,
    ):
        self.src_dir = src_dir
        self.dst_dir = dst_dir

    def sync(self, *args, **kwargs):
        raise NotImplementedError("Not Implemented")

    def get_months_by_existing_dir(self):
        res = []
        if self.src_dir is None:
            return res
        pattern = re.compile(r"^20\d{2}-[01][0-9]$")
        for file in self.src_dir.iterdir():
            if file.is_dir() and pattern.match(file.name) is not None:
                res.append(file.name)
        return res
