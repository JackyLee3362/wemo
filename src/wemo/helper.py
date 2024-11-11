import os
from pathlib import Path
import shutil
from flask.helpers import get_root_path as flask_get_root_path
from pywxdump import get_wx_info as pywxdump_get_wx_info
from pywxdump import decrypt as pywxdump_decrypt


def get_debug_flag() -> bool:
    val = os.environ.get("WEMO_DEBUG")
    return bool(val and val.lower() not in {"0", "false", "no"})


def get_root_path(import_name: str) -> str:
    return flask_get_root_path(import_name)


def get_wx_info(info: dict = None):
    return info or pywxdump_get_wx_info()


def decrypt(key: str, db_path: Path | str, out_path: Path | str) -> bool:
    if key is None:
        shutil.copy(db_path, out_path)
        return
    pywxdump_decrypt(key, db_path, out_path)
