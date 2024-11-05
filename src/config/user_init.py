from pathlib import Path
from .constant import DATA_DIR
from .config import config


def init_constant():
    from pywxdump import get_wx_info

    global USER_WXID
    global USER_WXDB_DIR
    global USER_DB_DIR
    global USER_CACHE_DIR
    global USER_BACK_DIR
    global USER_KEY

    if config.get("app.env") in ["dev", "test"]:
        USER_WXID = "test"
        USER_WXDB_DIR = None
        USER_DB_DIR = DATA_DIR.joinpath(USER_WXID, "db")
        USER_CACHE_DIR = DATA_DIR.joinpath(USER_WXID, "cache")
        USER_BACK_DIR = DATA_DIR.joinpath(USER_WXID, "backup")
        USER_KEY = "test"
        return

    wx_info = get_wx_info()
    info = wx_info[0]
    if info is not None:

        USER_WXID = info["wxid"]
        USER_WXDB_DIR = Path(info["wx_dir"])
        USER_DB_DIR = DATA_DIR.joinpath(USER_WXID, "db")
        USER_CACHE_DIR = DATA_DIR.joinpath(USER_WXID, "cache")
        USER_BACK_DIR = DATA_DIR.joinpath(USER_WXID, "backup")
        USER_KEY = info["key"]


init_constant()
