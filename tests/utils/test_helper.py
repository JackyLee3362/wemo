from pathlib import Path
from wemo.backend.utils import helper


def test_find_root_path():
    import_name = "wemo"
    root_path = helper.get_root_path(import_name)
    print(root_path)
