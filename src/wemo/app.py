from pathlib import Path

from wemo.base.app import App


class Wemo(App):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
