import os
import shutil

from common import RC, LOG
from decrypter import db_decrypt
from db.impl.micro_msg import MicroMsg, MICRO_MSG, MicroMsgCache
from db.impl.misc import MISC, Misc, MiscCache
from db.impl.sns import Sns, SNS, SnsCache
from utils import singleton


@singleton
class DBCluster:
    def __init__(self):
        self.wx_dir = RC.WX_DIR
        self.user_cache_db = RC.USER_CACHE_DB
        self.user_db = RC.USER_DB
        self.decrypter = db_decrypt.DatabaseDecrypter()
        # 数据库
        self.dbs = None
        # 缓存数据
        self.caches = None

    def init_dbs(self):
        self.dbs = {MICRO_MSG: MicroMsg(), MISC: Misc(), SNS: Sns()}

    def init_caches(self):
        self.decrypter.decrypt_and_move()
        self.caches = {MICRO_MSG: MicroMsgCache(), MISC: MiscCache(), SNS: SnsCache()}

    def update_user_db_by_cache(self, db_name: str):
        pass
