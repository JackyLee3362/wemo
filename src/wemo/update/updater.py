import logging
from logging import Logger
from pathlib import Path
from wemo.model.moment import MomentMsg


class Updater:
    def __init__(self, src_dir: Path, dst_dir: Path, logger: Logger):
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.logger = logger or logging.getLogger(__name__)

    def update_by_username(self, username: str): ...

    def update_by_moment(self, moment: MomentMsg): ...
