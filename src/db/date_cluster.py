import os
import shutil

from common import RC, LOG
from decrypter import db_decrypt
from .micro_msg import MICRO_MSG, MicroMsg
from .misc import MISC, Misc
from .sns import SNS, Sns


class DataBaseSet:
    def __init__(self):
        self.wx_dir = RC.WX_DIR
        self.user_cache_db = RC.USER_CACHE_DB
        self.user_db = RC.USER_DB
        self.decrypter = db_decrypt.DatabaseDecrypter()

    def run(self):
        self.init_db_set()
        self.update_user_db_by_cache(MISC)
        self.update_user_db_by_cache(SNS)
        self.update_user_db_by_cache(MICRO_MSG)

    def init_db_set(self):
        # 1. 初始化用户数据库
        if not self.user_cache_db.exists():
            os.mkdir(self.user_cache_db)
        # 2. 清除缓存数据库
        self.init_cache()
        # 3. 将解密后的数据放入缓存数据库
        self.decrypter.decrypt_and_move()

    def update_user_db_by_cache(self, db: str):
        user_db_path = self.user_db.joinpath(db + ".db")
        cache_db_path = self.user_cache_db.joinpath(db + ".db")
        # 情况一：缓存数据库不存在
        if not cache_db_path.exists():
            LOG.warning(f"[{db}] 缓存数据库不存在")
            return
        # 情况二：用户数据库不存在
        if not user_db_path.exists():
            shutil.copy(cache_db_path, user_db_path)
            LOG.debug(f"[{db}]缓存数据库 -> 用户数据库")
            return
        # 情况三：用户数据库存在
        LOG.debug(f"[{db}] 用户数据库存在，使用缓存更新")
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
        if not self.wx_dir.exists():
            return
        if self.wx_dir.exists() and self.user_cache_db.exists():
            # todo: 如果有数据 warning
            shutil.rmtree(self.user_cache_db)
            os.mkdir(self.user_cache_db)
