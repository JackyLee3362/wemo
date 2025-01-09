from functools import cached_property

from wemo.backend.base.config import TomlConfig
from wemo.backend.base.logger import config_app_logger
from wemo.backend.common import constant


class Scaffold:
    name: str
    config: TomlConfig

    def __init__(self, import_name, root_path=None):
        self.name = import_name
        self.root_path = root_path

        self.config = TomlConfig()
        self.setup_logger()

    @cached_property
    def debug(self) -> bool:
        return self.config.app.debug

    def setup_logger(self) -> None:
        config_app_logger(self.name, log_dir=constant.LOGS_DIR)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"
