from wemo.database.db import DbCacheTuple, UserTable
from wemo.base.logger import default_console_logger
from wemo.database.misc import (
    Misc as DB,
    MiscCache as DBCache,
    BizContactHeadImg,
    ContactHeadImg1,
)
from wemo.base import constant

DB_N = 200
CACHE_N = 300
name = "test_database"
db_name = "Misc.db"
user_db_dir = constant.DATA_DIR.joinpath(name, "data")
user_cache_db_dir = constant.DATA_DIR.joinpath(name, "cache")
LOG = default_console_logger(name)
db = DB(user_db_dir.joinpath(db_name), LOG)
cache = DBCache(user_cache_db_dir.joinpath(db_name), LOG)


class TestMock:

    def test_biz_contact_head_img(self):
        b1 = BizContactHeadImg.mock(1)
        b1_other = BizContactHeadImg.mock(1)
        b2 = BizContactHeadImg.mock(2)

        assert b1.usrName == b1_other.usrName
        assert b1.usrName != b2.usrName

    def test_contact_head_img_1(self):
        c1 = ContactHeadImg1.mock(1)
        c1_other = ContactHeadImg1.mock(1)
        c2 = ContactHeadImg1.mock(2)

        assert c1.usrName == c1_other.usrName
        assert c1.usrName != c2.usrName


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
        self.merge_by_table(BizContactHeadImg)
        self.merge_by_table(ContactHeadImg1)

    def merge_by_table(self, cls: UserTable = None, n=DB_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()

    def test_get_avatar(self):
        user = ContactHeadImg1.mock(1)
        buf = b"00112233"
        user.smallHeadBuf = buf
        self.db.merge_all([user])
        res = self.db.get_avatar_buffer(user.usrName)
        assert res.smallHeadBuf == buf

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
        self.merge_by_table(BizContactHeadImg)
        self.merge_by_table(ContactHeadImg1)

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
            print("c1 is ", c1, "c2 is ", c2)
            assert c1 == c2
