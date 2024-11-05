import shutil
from pathlib import Path
import os

from decrypter import db_decrypt
from config import DB_DIR, LOG

from .micro_msg import MICRO_MSG, MicroMsg
from .misc import MISC, Misc
from .sns import SNS, Sns


class DataBaseSet:
    def __init__(self, info: dict):
        # 1. 存储基本信息
        self.wxid = info.get("wxid")
        self.wx_dir = Path(info.get("wx_dir"))
        self.key = info.get("key")
        # 2. 用来存储正式的数据库
        self.user_db_dir: Path = DB_DIR / self.wxid
        # 3. 用户缓存数据库
        self.user_cache_db_dir: Path = DB_DIR / self.wxid / "cache"
        self.decrypter = db_decrypt.DatabaseDecrypter(self.wx_dir, self.key)

    def init_db_set(self):
        # 1. 初始化用户数据库
        if not self.user_db_dir.exists():
            os.mkdir(self.user_db_dir)
        # 2. 清除缓存数据库
        self.clear_cache()
        os.mkdir(self.user_cache_db_dir)
        # 3. 将解密后的数据放入缓存数据库
        self.decrypter.decrypt_and_move(self.user_cache_db_dir)

    def update_user_db_by_cache(self, db: str):
        user_db = self.user_db_dir.joinpath(db + ".db")
        cache_db = self.user_cache_db_dir.joinpath(db + ".db")
        # 情况一：缓存数据库不存在
        if not cache_db.exists():
            LOG.warning(f"缓存数据库 {db} 不存在")
            return
        # 情况二：用户数据库不存在
        if not user_db.exists():
            shutil.copy(cache_db, user_db)
            LOG.info(f"缓存数据库 {db} -> 主数据库 {db}")
            return
        # 情况三：用户数据库存在
        LOG.info(f"用户数据库存在，使用缓存更新 {db}")
        if db == MISC:
            misc = Misc(self.wxid)
            misc.update_db_from_cache_by_all()
        elif db == MICRO_MSG:
            micro_msg = MicroMsg(self.wxid)
            micro_msg.update_db_from_cache_by_all()
        elif db == SNS:
            sns = Sns(self.wxid)
            sns.update_db_from_cache_by_all()
        else:
            raise NotImplementedError()

    def clear_cache(self):
        if self.user_cache_db_dir.exists():
            # todo: 如果有数据 warning
            shutil.rmtree(self.user_cache_db_dir)
