from pathlib import Path
from pywxdump import get_wx_info

from .constant import SC
from .config import config


class RC:
    # runtime constant 运行时常量

    WX_ID: str
    WX_DIR: Path
    WX_KEY: str
    WX_SNS_CACHE_DIR: Path

    ENV = config.get("app.env")
    if ENV in ["dev", "test"]:
        WX_ID = ENV
        WX_KEY = ENV
        WX_DIR = SC.MOCK_DIR(ENV)
    else:
        wx_info = get_wx_info()
        info = wx_info[0]
        if info is not None:
            WX_ID = info["wxid"]
            WX_KEY = info["key"]
            WX_DIR = Path(info["wx_dir"])
    WX_SNS_CACHE_DIR = WX_DIR.joinpath("FileStorage", "Sns", "Cache")

    # 用户目录
    USER_DIR = SC.DATA_DIR.joinpath(WX_ID)
    USER_DB = USER_DIR.joinpath("db")
    USER_SNS_DIR = USER_DIR.joinpath("sns")
    USER_BACKUP_DIR = USER_DIR.joinpath("backup")
    USER_OUTPUT_DIR = USER_DIR.joinpath("output")
    USER_CACHE_DIR = USER_DIR.joinpath("cache")
    # 缓存目录
    USER_CACHE_DB = USER_CACHE_DIR.joinpath("db")
    USER_CACHE_SNS = USER_CACHE_DIR.joinpath("sns")
    USER_CACHE_SNS_IMAGE = USER_CACHE_SNS.joinpath("images")
    USER_CACHE_SNS_THUMB = USER_CACHE_SNS.joinpath("thumbs")
    USER_CACHE_SNS_VIDEO = USER_CACHE_SNS.joinpath("videos")
    # 朋友圈资源目录
    USER_SNS_THUMB = USER_SNS_DIR.joinpath("thumbs")
    USER_SNS_IMAGE = USER_SNS_DIR.joinpath("images")
    USER_SNS_VIDEO = USER_SNS_DIR.joinpath("videos")


# 初始化创建用户文件夹
for item in dir(RC):
    var = getattr(RC, item)
    if isinstance(var, Path) and item.startswith("USER"):
        if not var.exists():
            var.mkdir(parents=True, exist_ok=True)
