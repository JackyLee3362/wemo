from pathlib import Path

import requests
from pywxdump import decrypt as pywxdump_decrypt
from pywxdump import get_wx_info as pywxdump_get_wx_info


def get_wx_info():
    res = None
    infos = pywxdump_get_wx_info()
    # 说明没有登录
    if len(infos) < 1:
        return None
    res: dict = infos[0]
    wx_dir = res.get("wx_dir")
    res["wx_dir"] = Path(wx_dir)
    # 说明检测错误
    if res["wxid"] is None:
        return None
    return res


def decrypt(key: str, db_path: Path | str, out_path: Path | str) -> bool:
    return pywxdump_decrypt(key, db_path, out_path)


def get_img_from_server(url, params: dict) -> bytes:
    if params:
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        url = f"{url}?{query_string}"
    response = requests.get(url)
    if response.ok:
        return response.content
