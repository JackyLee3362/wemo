from __future__ import annotations

import logging
from functools import cached_property
from pathlib import Path

from wemo.base.constant import MOCK_DIR
from wemo.base.logger import default_console_logger

from wemo.base.config import Config, ConfigAttribute


class UserDirStructure(Path):

    def __init__(self, user_root_dir: Path, *args):
        super().__init__(user_root_dir, *args)

    @property
    def db_dir(self):
        return self.joinpath("db")

    @property
    def img_dir(self):
        return self.joinpath("image")

    @property
    def video_dir(self):
        return self.joinpath("video")

    @property
    def avatar_dir(self):
        return self.joinpath("avatar")

    def init_dir(self):
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.avatar_dir.mkdir(parents=True, exist_ok=True)


class User:
    # runtime constant 运行时常量
    wx_id = ConfigAttribute[str]("wxid")
    wx_dir: Path = ConfigAttribute[Path]("wx_dir")
    wx_key = ConfigAttribute[str]("key")
    db_name_list = ["Sns", "MicroMsg", "Misc"]

    def __init__(
        self,
        proj_dir: Path,
        info: dict,
        config: Config,
        logger: logging.Logger = None,
    ):
        self.proj_dir = proj_dir
        self.info = info
        config.update(info)
        self.config = config

        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug(f"[ USER ] user({self.wx_id}) init.")

    def init_user_dir(self):
        if self.data_dir is None:
            raise ValueError("data dir is None!")
        self.data_dir.init_dir()

        if self.cache_dir is None:
            raise ValueError("cache dir is None!")
        self.cache_dir.init_dir()

    @cached_property
    def wx_sns_cache_dir(self) -> Path:
        return self.wx_dir.joinpath("FileStorage", "Sns", "Cache")

    @cached_property
    def user_dir(self) -> Path:
        proj_data_dir: Path = self.config.get("DATA_DIR")
        return proj_data_dir.joinpath(self.wx_id)

    @cached_property
    def data_dir(self) -> UserDirStructure:
        return UserDirStructure(self.user_dir.joinpath("data"))

    @cached_property
    def cache_dir(self) -> UserDirStructure:
        return UserDirStructure(self.user_dir.joinpath("cache"))

    @staticmethod
    def mock_user(wxid: str) -> User:
        from wemo.base import constant

        proj_path = constant.PROJECT_DIR

        config = Config(proj_path)
        config.from_object(constant)

        wx_user_dir = MOCK_DIR.joinpath(wxid)

        info = {"wxid": wxid, "key": None, "wx_dir": wx_user_dir}
        logger = default_console_logger(__name__)

        return User(proj_dir=proj_path, info=info, config=config, logger=logger)
