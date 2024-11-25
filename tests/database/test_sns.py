from wemo.backend.base.logger import create_app_logger
from wemo.backend.database.db import UserTable
from wemo.backend.database.sns import (
    Sns as DB,
    SnsCache as DBCache,
    Feed,
    Comment,
    SnsConfig,
)
from wemo.backend.base import constant
import time
import datetime

from wemo.backend.utils.utils import to_timestamp

DB_N = 200
CACHE_N = 300
name = "test_database"
db_name = "MicroMsg.db"
user_db_dir = constant.DATA_DIR.joinpath(name, "data")
user_cache_db_dir = constant.DATA_DIR.joinpath(name, "cache")
logger = create_app_logger(name)
db = DB(user_db_dir.joinpath(db_name), logger)
cache = DBCache(user_cache_db_dir.joinpath(db_name), logger)


class TestMock:

    def test_feed_v20(self):
        s0 = Feed.mock(1)
        s1 = Feed.mock(1)
        s2 = Feed.mock(2)

        assert s0.feed_id == s1.feed_id
        assert s0.feed_id != s2.feed_id

    def test_comment_v20(self):
        s0 = Comment.mock(1)
        s1 = Comment.mock(1)
        s2 = Comment.mock(2)

        assert s0.feed_id == s1.feed_id
        assert s0.feed_id != s2.feed_id

    def test_sns_config_v20(self):
        s0 = SnsConfig.mock(1)
        s1 = SnsConfig.mock(1)
        s2 = SnsConfig.mock(2)

        assert s0.key == s1.key
        assert s0.key != s2.key


class TestDB:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = db
        self.db.init()

    def test_singleton(self):
        db2 = DB(self.db_dir, logger)
        assert self.db == db2

    def test_count_all(self):
        for table in self.db.table_cls_list:
            self.db.count_all(table)

    def test_query_all(self):
        for table in self.db.table_cls_list:
            self.db.query_all(table)

    def test_merge_all(self):
        self.merge_by_table(Feed)
        self.merge_by_table(Comment)
        self.merge_by_table(SnsConfig, 5)

    def merge_by_table(self, cls: type[UserTable] = None, n=DB_N):
        res = [cls.mock(i) for i in range(n)]
        db_data = self.db.query_all(cls)
        self.test_count_all()
        self.db.merge_all(cls, db_data, res)
        self.test_count_all()

    def test_get_message_in_time(self):
        begin_timestamp = int(time.time() - 100)
        end_timestamp = int(time.time() + 100)
        assert isinstance(begin_timestamp, int)
        assert isinstance(end_timestamp, int)
        res = self.db.get_feeds_by_dur_and_wxids(begin_timestamp, end_timestamp)
        print("Feed 数量是", len(res))

        if len(res) <= 0:
            return
        for latest in res:
            feed_id = latest.FeedId
            res2 = self.db.get_comment_by_feed_id(feed_id=feed_id)
            if len(res2) > 0:
                print("Comment 数量是", len(res2))
                break

    def test_get_cover_url(self):
        res = self.db.get_cover_url()
        print(res)

    def test_get_feed_by_id(self):
        res = self.db.get_feed_by_feed_id(-3926330463233363453)
        print(res)
        assert res is not None

    def test_recent_feed(self):
        begin_date = datetime.datetime.now() + datetime.timedelta(days=-1)
        end_date = datetime.datetime.now() + datetime.timedelta(days=1)
        b = to_timestamp(begin_date)
        e = to_timestamp(end_date)
        print(b, "->", e)
        res = self.db.get_feeds_by_dur_and_wxids(b, e)

    def teardown_class(self):
        self.db.close_session()


class TestCache:
    def setup_class(self):
        # 指定目录
        self.cache_dir = user_cache_db_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = cache
        self.db.init()

    def test_count_all(self):
        for table in self.db.table_cls_list:
            self.db.count_all(table)

    def test_merge_all(self):
        self.merge_by_table(Feed)
        self.merge_by_table(Comment)
        self.merge_by_table(SnsConfig, 5)

    def merge_by_table(self, cls: UserTable = None, n=CACHE_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()
