from decrypter import db_decrypter
from utils import singleton
from pathlib import Path

from .micro_msg import MICRO_MSG, MicroMsg, MicroMsgCache
from .misc import MISC, Misc, MiscCache
from .sns import SNS, Sns, SnsCache


@singleton
class DBCluster:
    def __init__(self, src_dir: Path, dst_dir: Path, db_dir: Path):
        self.wx_dir = src_dir
        self.user_cache_db = dst_dir
        self.user_db = db_dir
        self.decrypter = db_decrypter.DatabaseDecrypter()
        # 数据库
        self.dbs = None
        # 缓存数据
        self.caches = None

    def init_dbs(self):
        self.dbs = {MICRO_MSG: MicroMsg(), MISC: Misc(), SNS: Sns()}

    def init_caches(self):
        self.decrypter.decrypt_and_copy()
        self.caches = {MICRO_MSG: MicroMsgCache(), MISC: MiscCache(), SNS: SnsCache()}

    def update_user_db_by_cache(self, db_name: str):
        pass
