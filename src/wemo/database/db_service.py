from datetime import datetime
import logging
from wemo.database.db import AbsUserDB
from wemo.database.micro_msg import Contact, MicroMsg, MicroMsgCache
from wemo.database.misc import Misc, MiscCache
from wemo.database.sns import Feed, Sns, SnsCache
from wemo.model.user import User


class DBService:

    def __init__(self, user: User, logger: logging.Logger = None):
        self.user = user
        self.logger = logger or user.logger

    def init(self):
        self.logger.info("[ DB SERVICE ] init db...")
        self._init_db()
        self._init_cache()

    def update_db(self):
        self.logger.info("[ DB SERVICE ] updating...")
        self._update_db_by_cache(self.sns, self.sns_cache)
        self._update_db_by_cache(self.misc, self.misc_cache)
        self._update_db_by_cache(self.micro_msg, self.micro_msg_cache)

    def get_feeds_by_dur_ids(
        self, begin: datetime, end: datetime, wx_ids: list[str] = None
    ):
        b_int = int(begin.timestamp())
        e_int = int(end.timestamp())
        feeds = self.sns.get_feeds_by_dur_and_wxids(b_int, e_int, wx_ids)
        return feeds

    def get_contact_by_username(self, username: str) -> Contact:
        return self.micro_msg.get_contact_by_username(username)

    def get_feeds_and_by_duration_and_wxids(
        self, begin, end, wx_ids=None
    ) -> list[Feed]:
        return self.sns.get_feeds_by_dur_and_wxids(begin, end, wx_ids)

    def get_contact_list(self) -> list[Contact]:
        return self.micro_msg.get_contact_list()

    def get_avatar_buf_by_username(self, username: str):
        return self.misc.get_avatar_buffer(username)

    def _init_db(self):
        user = self.user
        db_dir = user.data_dir.db_dir  # 用户数据库数据
        self.sns = Sns(db_dir.joinpath("Sns.db"), self.logger)
        self.sns.init()
        self.micro_msg = MicroMsg(db_dir.joinpath("MicroMsg.db"), self.logger)
        self.micro_msg.init()
        self.misc = Misc(db_dir.joinpath("Misc.db"), self.logger)
        self.misc.init()

    def _init_cache(self):
        db_dir = self.user.cache_dir.db_dir
        self.sns_cache = SnsCache(db_dir.joinpath("Sns.db"), self.logger)
        self.sns_cache.init()
        self.misc_cache = MiscCache(db_dir.joinpath("Misc.db"), self.logger)
        self.misc_cache.init()
        self.micro_msg_cache = MicroMsgCache(
            db_dir.joinpath("MicroMsg.db"), self.logger
        )
        self.micro_msg_cache.init()

    def _update_db_by_cache(self, db: AbsUserDB, cache: AbsUserDB):
        self.logger.debug(f"[ DB SERVICE ] db({db.__class__.__name__}) update db by cache")
        for t_cls in db.table_cls_list:
            self.logger.debug(f"[ DB SERVICE ] table({t_cls.__name__}) update")
            data_list = cache.query_all(t_cls)
            db.merge_all(data_list)
