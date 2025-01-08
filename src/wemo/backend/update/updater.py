import logging
from logging import Logger
from pathlib import Path
from wemo.backend.model.moment import MomentMsg


logger = logging.getLogger(__name__)


class Updater:
    def __init__(self, src_dir: Path, dst_dir: Path):
        self.src_dir = src_dir
        self.dst_dir = dst_dir

    def update_by_username(self, username: str): ...

    def update_by_moment(self, moment: MomentMsg): ...
