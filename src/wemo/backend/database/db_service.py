import logging
from datetime import datetime, timedelta

from wemo.backend.ctx import AppContext
from wemo.backend.database.db import AbsUserDB
from wemo.backend.database.micro_msg import Contact, MicroMsg, MicroMsgCache
from wemo.backend.database.misc import Misc, MiscCache
from wemo.backend.database.sns import Feed, Sns, SnsCache

logger = logging.getLogger(__name__)


class DBService:

    def __str__(self):
        return "[ DB SERVICE ]"

    def __init__(self, ctx: AppContext):
        self.ctx = ctx
        self.init()

    def init(self):
        logger.info(f"{self} init db...")
        self._create_db_cache()
        self._init_db()

    def update_db(self):
        logger.info(f"{self} updating...")
        self._update_db_by_cache(self.sns, self.sns_cache)
        self._update_db_by_cache(self.misc, self.misc_cache)
        self._update_db_by_cache(self.micro_msg, self.micro_msg_cache)

    def _close_db(self):
        self.sns.close_session()
        self.sns.close_connection()
        self.micro_msg.close_session()
        self.micro_msg.close_connection()
        self.misc.close_session()
        self.misc.close_connection()

    def flush_db(self):
        self._close_db()
        self._init_db()

    def get_feeds_by_dur_wxids(self, begin: int, end: int, wx_ids: list[str] = None):
        try:
            feeds = self.sns.get_feeds_by_dur_and_wxids(begin, end, wx_ids)
        except Exception as e:
            logger.exception(e)
            return []
        return feeds

    def get_contact_by_username(self, username: str) -> Contact:
        return self.micro_msg.get_contact_by_username(username)

    def get_latest_feed(self) -> Feed:
        begin = (datetime.now() - timedelta(days=365)).timestamp()
        end = datetime.now().timestamp()
        feeds = self.sns.get_feeds_by_dur_and_wxids(begin, end, None)
        if len(feeds) > 0:
            return feeds[0]
        return None

    def get_feeds_and_by_duration_and_wxids(
        self, begin, end, wx_ids=None
    ) -> list[Feed]:
        return self.sns.get_feeds_by_dur_and_wxids(begin, end, wx_ids)

    def get_contact_list(self) -> list[Contact]:
        return self.micro_msg.get_contact_list()

    def get_avatar_buf_by_username(self, username: str):
        return self.misc.get_avatar_buffer(username)

    def get_feed_by_feed_id(self, feed_id):
        return self.sns.get_feed_by_feed_id(feed_id)

    def get_fuzzy_name(self, fuzzy_name):
        return self.micro_msg.get_contact_by_fuzzy_name(fuzzy_name)

    def get_cover_url(self):
        return self.sns.get_cover_url()

    def get_comment_by_feed_id(self, feed_id: int):
        return self.sns.get_comment_by_feed_id(feed_id)

    def _init_db(self):
        self.sns.init()
        self.micro_msg.init()
        self.misc.init()

    def _create_db_cache(self):
        db_dir = self.ctx.user_data_dir.db_dir
        self.sns = Sns(db_dir.joinpath("Sns.db"))
        self.micro_msg = MicroMsg(db_dir.joinpath("MicroMsg.db"))
        self.misc = Misc(db_dir.joinpath("Misc.db"))
        cache_dir = self.ctx.user_cache_dir.db_dir
        self.sns_cache = SnsCache(cache_dir.joinpath("Sns.db"))
        self.misc_cache = MiscCache(cache_dir.joinpath("Misc.db"))
        self.micro_msg_cache = MicroMsgCache(cache_dir.joinpath("MicroMsg.db"))

    def _update_db_by_cache(self, db: AbsUserDB, cache: AbsUserDB):
        logger.debug(f"{self} db({db.__class__.__name__}) update db by cache")
        for t_cls in db.table_cls_list:
            if not self.ctx.running:
                logger.debug(f"{self} stop updating")
                break
            logger.debug(f"{self} table({t_cls.__name__}) update")
            db_data = db.query_all(t_cls)
            cache_data = cache.query_all(t_cls)
            db.merge_all(t_cls, db_data, cache_data)
