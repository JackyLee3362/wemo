from __future__ import annotations
from functools import cached_property
import logging
from pathlib import Path

from wemo.base.config import Config, ConfigAttribute


class UserDirStructure(Path):

    def __init__(self, user_root_dir: Path, *args, **kwargs):
        super().__init__(user_root_dir, *args, **kwargs)

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
    wx_id = ConfigAttribute[str]("wx_id")
    wx_dir: Path = ConfigAttribute[Path]("wx_dir")
    wx_key = ConfigAttribute[str]("wx_key")

    def __init__(
        self,
        proj_data_dir: Path,
        info: dict,
        config: Config,
        logger: logging.Logger = None,
    ):
        self.proj_data_dir = proj_data_dir
        self.info = info
        config.update(info)
        self.config = config

        if logger is None:
            logger = logging.getLogger(__name__)
        self.logger = logger

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
        return self.proj_data_dir.joinpath(self.wx_id)

    @cached_property
    def data_dir(self) -> UserDirStructure:
        return UserDirStructure(self.user_dir.joinpath("data"))

    @cached_property
    def cache_dir(self) -> UserDirStructure:
        return UserDirStructure(self.user_dir.joinpath("cache"))

    @staticmethod
    def mock_user(mock_wx_id: str) -> User:
        from wemo import constant

        project_path = constant.PROJECT_DIR

        config = Config(project_path)
        config.from_object(constant)

        data_dir: Path = config.get("DATA_DIR")
        mock_dir: Path = config.get("MOCK_DIR")
        mock_wx_dir = mock_dir.joinpath(mock_wx_id)

        info = {"wx_id": mock_wx_id, "wx_key": None, "wx_dir": mock_wx_dir}

        return User(proj_data_dir=data_dir, info=info, config=config)
