from __future__ import annotations

import logging
import shutil
from datetime import datetime
from functools import cached_property
from pathlib import Path

from wemo.backend.base.scaffold import Scaffold
from wemo.backend.common import constant
from wemo.backend.utils.helper import get_wx_info
from wemo.gui_signal import GuiSignal

logger = logging.getLogger(__name__)


class AppContext(Scaffold):
    """应用上下文对象，主要是目录信息和用户信息"""

    db_name_list = ["Sns", "MicroMsg", "Misc"]

    def __init__(self, name: str, root: Path = None):
        if root is None:
            root = constant.PROJECT_DIR
        super().__init__(name, root)
        self.config.load_file(constant.CONFIG_DEFAULT_FILE)
        self.signal: GuiSignal = None
        self.running = True
        self.has_init_user = False
        # 项目目录初始化
        self.init_app_info()

    def inject(self, signal: GuiSignal):
        self.signal = signal

    def init_app_info(self):
        logger.info(f"{self} init ctx, project dir is {self.proj_dir}")
        self.output_date_dir: UserDir = None
        self.generate_output_date_dir()

    def init_user_wx_info(self):
        # 如果已经初始化过，则直接返回
        if self.has_init_user:
            return True
        # 用户目录
        # 首先获取用户信息
        info = get_wx_info()
        # 说明没有登录
        if info is None:
            logger.warning(f"{self} 未登录微信，请先登录微信，如果已登录，请稍等 10 秒")
            return False
        self.config.update(info)
        logger.info(f"{self} init user({self.wx_id})...")
        self.has_init_user = True
        return self.has_init_user

    def init_user_dir(self):
        # 初始化用户目录
        self.wx_sns_cache_dir = self.wx_dir.joinpath("FileStorage", "Sns", "Cache")
        self.user_dir = constant.DATA_DIR.joinpath(self.wx_id)
        self.user_data_dir = UserDir(self.user_dir.joinpath("data"))
        self.user_cache_dir = UserDir(self.user_dir.joinpath("cache"))

    def generate_output_date_dir(self) -> UserDir:
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        p = constant.OUTPUT_DIR.joinpath(date)
        if not p.exists():
            shutil.copytree(constant.STATIC_DIR, p)
        res = UserDir(p)
        self.output_date_dir = res
        return res

    def __str__(self):
        return "[ CTX ]"

    @cached_property
    def wx_id(self) -> str:
        return self.config.wxid

    @cached_property
    def wx_key(self) -> str:
        return self.config.key

    @cached_property
    def wx_dir(self) -> Path:
        return self.config.wx_dir

    @cached_property
    def proj_dir(self) -> Path:
        return constant.PROJECT_DIR


class UserDir:

    def __init__(self, user_root_dir: Path):
        self.user_root_dir: Path = user_root_dir
        self._init_dir()

    @property
    def db_dir(self) -> Path:
        return self.user_root_dir.joinpath("db")

    @property
    def img_dir(self) -> Path:
        return self.user_root_dir.joinpath("image")

    @property
    def video_dir(self) -> Path:
        return self.user_root_dir.joinpath("video")

    @property
    def avatar_dir(self) -> Path:
        return self.user_root_dir.joinpath("avatar")

    def _init_dir(self):
        self.user_root_dir.mkdir(parents=True, exist_ok=True)
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
