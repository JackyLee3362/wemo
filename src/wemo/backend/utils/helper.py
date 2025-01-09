from pathlib import Path

import requests
from pywxdump import decrypt as pywxdump_decrypt
from pywxdump import get_wx_info as pywxdump_get_wx_info


def get_wx_info(info: dict = None):
    if info.get("wxid", False):
        return info
    infos = pywxdump_get_wx_info()
    res: dict = infos[0]
    wx_dir = res.get("wx_dir")
    res["wx_dir"] = Path(wx_dir)
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
