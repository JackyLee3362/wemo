import datetime
import time
from pathlib import Path
from wemo.base.db import UserTable
from wemo.base.logging import default_console_logger
from wemo.database.sns import Sns, FeedsV20, CommentV20, SnsConfigV20
from wemo import constant
from wemo.utils import to_timestamp

N = 200
name = "test_database"
user_dir = constant.DATA_DIR.joinpath(name)
LOG = default_console_logger(name)


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


class TestSns:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = Sns(self.db_dir, LOG)
        self.db.init_db()

    def test_singleton(self):
        db2 = Sns(self.db_dir, LOG)
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
        self.merge_by_table(SnsConfigV20, 10)

    def merge_by_table(self, cls: UserTable = None, n=N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()

    def test_get_message_in_time(self):
        begin_timestamp = int(time.time() - 100)
        end_timestamp = int(time.time() + 100)
        assert isinstance(begin_timestamp, int)
        assert isinstance(end_timestamp, int)
        res = self.db.get_feeds_by_duration(begin_timestamp, end_timestamp)
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
        res = self.db.get_feeds_by_duration(b, e)

    def teardown_class(self):
        self.db.close_session()
