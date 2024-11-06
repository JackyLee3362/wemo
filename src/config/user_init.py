from pathlib import Path
from pywxdump import get_wx_info

from .constant import DATA_DIR
from .config import config


def init_constant():

    global WX_ID
    global WX_DIR
    global WX_KEY
    global WX_SNS_CACHE_DIR
    global APP_USER_DB_DIR
    global APP_USER_CACHE_DIR
    global APP_USER_BACKUP_DIR
    global APP_USER_SNS_DIR

    if config.get("app.env") in ["dev", "test"]:
        WX_ID = "test"
        WX_KEY = "test"
        WX_DIR = None
        WX_SNS_CACHE_DIR = None
    else:
        wx_info = get_wx_info()
        info = wx_info[0]
        if info is not None:
            WX_ID = info["wxid"]
            WX_KEY = info["key"]
            WX_DIR = Path(info["wx_dir"])
            WX_SNS_CACHE_DIR = WX_DIR.joinpath("FileStorage", "Sns", "Cache")

    APP_USER_DB_DIR = DATA_DIR.joinpath(WX_ID, "db")
    APP_USER_CACHE_DIR = DATA_DIR.joinpath(WX_ID, "cache")
    APP_USER_BACKUP_DIR = DATA_DIR.joinpath(WX_ID, "backup")
    APP_USER_SNS_DIR = DATA_DIR.joinpath(WX_ID, "sns")


init_constant()
