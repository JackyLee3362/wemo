from functools import cached_property
import typing as t

from wemo.backend.base.config import TomlConfig
from wemo.backend.utils.helper import get_root_path


class Scaffold:
    name: str
    config: TomlConfig

    default_config: dict[str, t.Any] = {}

    def __init__(self, import_name, root_path=None):
        self.import_name = import_name
        if root_path is None:
            root_path = get_root_path(self.import_name)
        self.root_path = root_path

        self.config = TomlConfig()

    @cached_property
    def name(self) -> str:
        return self.import_name

    @cached_property
    def testing(self) -> bool:
        return self.config.testing

    @cached_property
    def secret_key(self) -> t.Union[str, bytes, None]:
        return self.config.secret_key

    @cached_property
    def debug(self) -> bool:
        return self.config.debug

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.name!r}>"
