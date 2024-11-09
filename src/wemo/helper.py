import os
from flask.helpers import get_root_path as flask_get_root_path


def get_debug_flag() -> bool:
    val = os.environ.get("WEMO_DEBUG")
    return bool(val and val.lower() not in {"0", "false", "no"})


#: copy from flask.helpers import get_root_path
def get_root_path(import_name: str) -> str:
    return flask_get_root_path(import_name)
