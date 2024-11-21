import importlib
import os
import shutil
from pathlib import Path
import sys

from pywxdump import decrypt as pywxdump_decrypt
from pywxdump import get_wx_info as pywxdump_get_wx_info
import requests


def get_root_path(import_name: str) -> str:
    # 模块已经导入
    mod = sys.modules.get(import_name)

    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    # 检查加载器
    try:
        spec = importlib.util.find_spec(import_name)

        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        loader = None
    else:
        loader = spec.loader

    # Loader does not exist or we're referring to an unloaded main
    # module or a main module without path (interactive sessions), go
    # with the current working directory.
    if loader is None:
        return os.getcwd()

    if hasattr(loader, "get_filename"):
        filepath = loader.get_filename(import_name)
    else:
        # Fall back to imports.
        __import__(import_name)
        mod = sys.modules[import_name]
        filepath = getattr(mod, "__file__", None)

        # If we don't have a file path it might be because it is a
        # namespace package. In this case pick the root path from the
        # first module that is contained in the package.
        if filepath is None:
            raise RuntimeError(
                "No root path can be found for the provided module"
                f" {import_name!r}. This can happen because the module"
                " came from an import hook that does not provide file"
                " name information or because it's a namespace package."
                " In this case the root path needs to be explicitly"
                " provided."
            )

    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))  # type: ignore[no-any-return]


def get_wx_info(info: dict = None):
    if info is not None:
        return info
    infos = pywxdump_get_wx_info()
    res = infos[0]
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
