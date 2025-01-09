from __future__ import annotations

from datetime import datetime
from functools import cached_property
import logging
from pathlib import Path
import shutil

from wemo.backend.base import constant
from wemo.backend.base.config import TomlConfig
from wemo.backend.base.constant import MOCK_DIR
from wemo.backend.utils.helper import get_wx_info
from wemo.gui_signal import GuiSignal

logger = logging.getLogger(__name__)


class Context:
    """应用上下文对象，主要是目录信息和用户信息"""

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

    db_name_list = ["Sns", "MicroMsg", "Misc"]

    def __init__(self, root: Path, config: TomlConfig, extra: dict = {}):
        super().__init__()
        self.root_dir = root
        self.config = config
        self.signal: GuiSignal = None
        self.running = True
        self.extra_info = extra
        # 项目目录初始化
        self.init_app_info()
        self.init_user_info()

    def inject(self, signal: GuiSignal):
        self.signal = signal

    def init_app_info(self):
        self.config.load_file(constant.CONFIG_DIR.joinpath("app.toml"))
        logger.info(f"[ CTX ] init ctx, project dir is {self.proj_dir}")
        self.template_dir = self.proj_dir.joinpath("template")
        self.data_dir = self.proj_dir.joinpath("data")
        self.output_dir = self.proj_dir.joinpath("output")
        self.static_dir = self.proj_dir.joinpath("static")
        self.bin_dir = self.proj_dir.joinpath("bin")
        self.output_date_dir = None
        # self.generate_output_date_dir()

    def init_user_info(self):
        # 用户目录
        # 1. 首先获取用户信息
        info = get_wx_info(self.extra_info)
        self.config.update(info)
        logger.info(f"[ CTX ] init user({self.wx_id})...")
        # 2. 初始化用户目录
        self.wx_sns_cache_dir = self.wx_dir.joinpath("FileStorage", "Sns", "Cache")
        self.user_dir = self.data_dir.joinpath(self.wx_id)
        self.user_data_dir = UserDir(self.user_dir.joinpath("data"))
        self.user_data_dir.init_mkdir()
        self.user_cache_dir = UserDir(self.user_dir.joinpath("cache"))
        self.user_cache_dir.init_mkdir()

    def generate_output_date_dir(self) -> UserDir:
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        p = self.output_dir.joinpath(date)
        shutil.copytree(self.static_dir, p)
        res = UserDir(p)
        res.init_mkdir()
        self.output_date_dir = res
        return res

    @staticmethod
    def mock_ctx(wxid: str) -> Context:
        proj_path = constant.PROJECT_DIR
        config = TomlConfig()
        config.load_file(constant.CONFIG_DIR.joinpath("app.toml"))
        wx_user_dir = MOCK_DIR.joinpath(wxid)
        info = {"wxid": wxid, "key": None, "wx_dir": wx_user_dir}

        return Context(
            root=proj_path,
            config=config,
            extra=info,
        )


class UserDir:

    def __init__(self, user_root_dir: Path):
        self.user_root_dir = user_root_dir

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

    def init_mkdir(self):
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.img_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.avatar_dir.mkdir(parents=True, exist_ok=True)
