import shutil
import os

from config.user_init import USER_WXDB_DIR
from decrypter import db_decrypt
from config import USER_CACHE_DIR, USER_DB_DIR, LOG

from .micro_msg import MICRO_MSG, MicroMsg
from .misc import MISC, Misc
from .sns import SNS, Sns


class DataBaseSet:
    def __init__(self):
        self.decrypter = db_decrypt.DatabaseDecrypter()

    def init_db_set(self):
        # 1. 初始化用户数据库
        if not USER_DB_DIR.exists():
            os.mkdir(USER_DB_DIR)
        # 2. 清除缓存数据库
        self.init_cache()
        # 3. 将解密后的数据放入缓存数据库
        self.decrypter.decrypt_and_move()

    def update_user_db_by_cache(self, db: str):
        user_db = USER_DB_DIR.joinpath(db + ".db")
        cache_db = USER_CACHE_DIR.joinpath(db + ".db")
        # 情况一：缓存数据库不存在
        if not cache_db.exists():
            LOG.warning(f"[{db}] 缓存数据库不存在")
            return
        # 情况二：用户数据库不存在
        if not user_db.exists():
            shutil.copy(cache_db, user_db)
            LOG.info(f"[{db}]缓存数据库 -> 用户数据库 ")
            return
        # 情况三：用户数据库存在
        LOG.info(f"[{db}] 用户数据库存在，使用缓存更新 ")
        if db == MISC:
            misc = Misc()
            misc.update_db_from_cache_by_all()
        elif db == MICRO_MSG:
            micro_msg = MicroMsg()
            micro_msg.update_db_from_cache_by_all()
        elif db == SNS:
            sns = Sns()
            sns.update_db_from_cache_by_all()
        else:
            raise NotImplementedError()

    def init_cache(self):
        # 说明不存在 wx_db_dir ，不对 cache 进行清理
        if not USER_CACHE_DIR.exists():
            os.mkdir(USER_CACHE_DIR)
        if USER_WXDB_DIR is None:
            return
        if USER_WXDB_DIR.exists() and USER_CACHE_DIR.exists():
            # todo: 如果有数据 warning
            shutil.rmtree(USER_CACHE_DIR)
            os.mkdir(USER_CACHE_DIR)
