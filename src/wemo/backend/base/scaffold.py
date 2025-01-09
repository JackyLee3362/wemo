from functools import cached_property

from wemo.backend.common import constant
from wemo.backend.base.config import TomlConfig
from wemo.backend.base.logger import config_app_logger


class Scaffold:
    name: str
    config: TomlConfig

    def __init__(self, import_name, root_path=None):
        self.import_name = import_name
        self.root_path = root_path

        self.config = TomlConfig()
        self.setup_logger()

    @cached_property
    def name(self) -> str:
        return self.import_name

    @cached_property
    def debug(self) -> bool:
        return self.config.debug

    def setup_logger(self) -> None:
        config_app_logger("wemo", log_dir=constant.LOGS_DIR)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"
