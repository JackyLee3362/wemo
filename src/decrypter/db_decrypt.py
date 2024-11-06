from pywxdump import decrypt

from config import WX_KEY, WX_DIR, LOG, APP_USER_CACHE_DIR
from db import MICRO_MSG, MISC, SNS


class DatabaseDecrypter:
    """数据库解密"""

    def __init__(self):
        self.db_name_list = [MICRO_MSG, MISC, SNS]

    def decrypt_and_move(self):
        if WX_DIR is None:
            LOG.error("未找到微信数据库，请检查是否已登录微信")
            return
        tasks = {}
        # 遍历 wx 数据库中的 db 数据库，并存入 cache 中
        for wx_db_path in WX_DIR.rglob("*.db"):
            if wx_db_path.stem in self.db_name_list:
                app_db_path = APP_USER_CACHE_DIR.joinpath(wx_db_path.name)
                tasks[wx_db_path.stem] = [wx_db_path, app_db_path]
        # 调用 pywxdump 解密
        for k, task in tasks.items():
            flag, result = decrypt(WX_KEY, *task)
            if not flag:
                LOG.error(result)
