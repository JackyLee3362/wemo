from .config import Config
from ..utils.helper import get_root_path


class Scaffold:
    name: str
    config: Config

    def __init__(self, import_name: str, root_path: str | None = None):
        self.import_name = import_name

        if root_path is None:
            root_path = get_root_path(self.import_name)
        self.root_path = root_path

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r}>"
