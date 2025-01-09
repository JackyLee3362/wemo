import logging

from wemo.backend.common import constant
from wemo.backend.database.misc import Misc as DB
from wemo.backend.database.misc import MiscCache as DBCache
from wemo.backend.utils.mock import mock_biz_contact_head_img, mock_contact_head_img_1

DB_N = 200
CACHE_N = 300

name = "test_database"
db_name = "Misc.db"

user_db_dir = constant.DATA_DIR.joinpath(name, "data")
user_cache_db_dir = constant.DATA_DIR.joinpath(name, "cache")

logger = logging.getLogger(__name__)

db = DB(user_db_dir.joinpath(db_name))

cache = DBCache(user_cache_db_dir.joinpath(db_name))


class TestMock:

    def test_biz_contact_head_img(self):
        b1 = mock_biz_contact_head_img(1)
        b1_other = mock_biz_contact_head_img(1)
        b2 = mock_biz_contact_head_img(2)

        assert b1.username == b1_other.username
        assert b1.username != b2.username

    def test_contact_head_img_1(self):
        c1 = mock_contact_head_img_1(1)
        c1_other = mock_contact_head_img_1(1)
        c2 = mock_contact_head_img_1(2)

        assert c1.username == c1_other.username
        assert c1.username != c2.username


class TestDB:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_db_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = db
        self.db.init()

    def test_singleton(self):
        db2 = DB(self.db_dir)
        assert self.db == db2

    def test_count_all(self):
        for table in self.db.table_cls_list:
            self.db.count_all(table)

    def test_query_all(self):
        for table in self.db.table_cls_list:
            self.db.query_all(table)

    def test_merge_all(self):
        self.merge_by_table(mock_biz_contact_head_img)
        self.merge_by_table(mock_contact_head_img_1)

    def merge_by_table(self, mock_func, n=DB_N):
        res = [mock_func(i) for i in range(n)]
        db_data = self.db.query_all(mock_func)
        self.test_count_all()
        self.db.merge_all(mock_func, db_data, res)
        self.test_count_all()

    def test_get_avatar(self):
        user = mock_contact_head_img_1(1)
        buf = b"00112233"
        user.buf = buf
        self.db.merge_all([user])
        res = self.db.get_avatar_buffer(user.username)
        assert res.buf == buf

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
        self.merge_by_table(mock_biz_contact_head_img)
        self.merge_by_table(mock_contact_head_img_1)

    def merge_by_table(self, mock_func, n=CACHE_N):
        res = [mock_func(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()
