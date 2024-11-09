from wemo.config import Config, ConfigAttribute
from wemo.helper import get_debug_flag
from wemo.logging import create_logger
from .scaffold import Scaffold
import typing as t
from logging import Logger


class App(Scaffold):
    config_class = Config
    testing = ConfigAttribute[bool]("TESTING")
    secret_key = ConfigAttribute[t.Union[str, bytes, None]]("SECRET_KEY")
    default_config: dict[str, t.Any]

    def __init__(self, import_name, root_path=None):
        super().__init__(import_name, root_path)
        self.config = self.make_config()
    @property
    def name(self) -> str:  # type: ignore
        # :todo:
        return

    @property
    def logger(self) -> Logger:
        return create_logger(self)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"

    def make_config(self) -> Config:
        root_path = self.root_path
        defaults = dict(self.default_config)
        defaults["DEBUG"] = get_debug_flag()
        return self.config_class(root_path, defaults)

    @property
    def debug(self) -> bool:
        return self.config["DEBUG"]  # type: ignore[no-any-return]

    @debug.setter
    def debug(self, value: bool) -> None:
        self.config["DEBUG"] = value
