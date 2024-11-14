from functools import cached_property
from pathlib import Path
import typing as t
from logging import Logger

from wemo.base.logger import create_app_logger
from wemo.base.config import Config, ConfigAttribute
from wemo.utils.utils import get_debug_flag
from wemo.utils.helper import get_root_path


class AbsApp:
    name: str
    config: Config

    config_class = Config
    testing = ConfigAttribute[bool]("TESTING")
    secret_key = ConfigAttribute[t.Union[str, bytes, None]]("SECRET_KEY")
    proj_dir = ConfigAttribute[Path]("PROJECT_DIR")

    default_config: dict[str, t.Any] = {}

    def __init__(self, import_name, root_path=None):
        self.import_name = import_name
        if root_path is None:
            root_path = get_root_path(self.import_name)
        self.root_path = root_path

        self.config = self.make_config()

    @cached_property
    def name(self) -> str:
        return self.import_name

    @cached_property
    def logger(self) -> Logger:
        return create_app_logger(self, self.config.get("LOGS_DIR"))

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"

    def make_config(self) -> Config:
        root_path = self.root_path
        defaults = dict(self.default_config)
        defaults["DEBUG"] = get_debug_flag()
        return self.config_class(root_path, defaults)

    @property
    def debug(self) -> bool:
        return self.config["DEBUG"]

    @debug.setter
    def debug(self, value: bool) -> None:
        self.config["DEBUG"] = value
