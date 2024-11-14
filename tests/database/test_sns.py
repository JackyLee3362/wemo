from wemo.database.db import DbCacheTuple, UserTable
from wemo.base.logger import default_console_logger
from wemo.database.sns import (
    Sns as DB,
    SnsCache as DBCache,
    FeedsV20,
    CommentV20,
    SnsConfigV20,
)
from wemo.base import constant
import time
import datetime

from wemo.utils.utils import to_timestamp

DB_N = 200
CACHE_N = 300
name = "test_database"
db_name = "MicroMsg.db"
user_db_dir = constant.DATA_DIR.joinpath(name, "data")
user_cache_db_dir = constant.DATA_DIR.joinpath(name, "cache")
LOG = default_console_logger(name)
db = DB(user_db_dir.joinpath(db_name), LOG)
cache = DBCache(user_cache_db_dir.joinpath(db_name), LOG)


class TestMock:

    def test_feed_v20(self):
        s0 = FeedsV20.mock(1)
        s1 = FeedsV20.mock(1)
        s2 = FeedsV20.mock(2)

        assert s0.FeedId == s1.FeedId
        assert s0.FeedId != s2.FeedId

    def test_comment_v20(self):
        s0 = CommentV20.mock(1)
        s1 = CommentV20.mock(1)
        s2 = CommentV20.mock(2)

        assert s0.FeedId == s1.FeedId
        assert s0.FeedId != s2.FeedId

    def test_sns_config_v20(self):
        s0 = SnsConfigV20.mock(1)
        s1 = SnsConfigV20.mock(1)
        s2 = SnsConfigV20.mock(2)

        assert s0.Key == s1.Key
        assert s0.Key != s2.Key


class TestDB:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = db
        self.db.init_db()

    def test_singleton(self):
        db2 = DB(self.db_dir, LOG)
        assert self.db == db2

    def test_count_all(self):
        for table in self.db.table_cls_list:
            self.db.count_all(table)

    def test_query_all(self):
        for table in self.db.table_cls_list:
            self.db.query_all(table)

    def test_merge_all(self):
        self.merge_by_table(FeedsV20)
        self.merge_by_table(CommentV20)
        self.merge_by_table(SnsConfigV20, 5)

    def merge_by_table(self, cls: UserTable = None, n=DB_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()

    def test_get_message_in_time(self):
        begin_timestamp = int(time.time() - 100)
        end_timestamp = int(time.time() + 100)
        assert isinstance(begin_timestamp, int)
        assert isinstance(end_timestamp, int)
        res = self.db.get_feeds_by_duration_and_wxid(begin_timestamp, end_timestamp)
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
        res = self.db.get_feeds_by_duration_and_wxid(b, e)

    def teardown_class(self):
        self.db.close_session()


class TestCache:
    def setup_class(self):
        # 指定目录
        self.cache_dir = user_cache_db_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = cache
        self.db.init_db()

    def test_count_all(self):
        for table in self.db.table_cls_list:
            self.db.count_all(table)

    def test_merge_all(self):
        self.merge_by_table(FeedsV20)
        self.merge_by_table(CommentV20)
        self.merge_by_table(SnsConfigV20, 5)

    def merge_by_table(self, cls: UserTable = None, n=CACHE_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()


class TestDBCache:

    def test_update_db_by_cache(self):
        dcs = DbCacheTuple(db, cache)
        dcs.init_db_cache()
        dcs.update_db_by_cache()
        for table in dcs.db.table_cls_list:
            c1 = dcs.db.count_all(table)
            c2 = dcs.cache.count_all(table)
            print(table, "c1 is ", c1, "c2 is ", c2)
            # assert c1 == c2
