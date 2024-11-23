from wemo.backend.base.logger import default_console_logger

from wemo.backend.base import constant
from wemo.backend.database.db import UserTable
from wemo.backend.database.micro_msg import (
    MicroMsg as DB,
    MicroMsgCache as DBCache,
    Contact,
    ContactHeadImgUrl,
    ContactLabel,
)

DB_N = 200
CACHE_N = 300
wxid = "test_database"
db_name = "MicroMsg.db"
user_db_dir = constant.DATA_DIR.joinpath(wxid, "data")
user_cache_db_dir = constant.DATA_DIR.joinpath(wxid, "cache")
logger = default_console_logger(wxid)
db = DB(user_db_dir.joinpath(db_name), logger)
cache = DBCache(user_cache_db_dir.joinpath(db_name), logger)


class TestMock:

    def test_contact_head_img_url(self):
        c1 = ContactHeadImgUrl.mock(1)
        c1_other = ContactHeadImgUrl.mock(1)
        c2 = ContactHeadImgUrl.mock(2)

        assert c1.username == c1_other.username
        assert c1.username != c2.username

    def test_contact(self):
        c1 = Contact.mock(1)
        c1_other = Contact.mock(1)
        c2 = Contact.mock(2)

        assert c1.username == c1_other.username
        assert c1.username != c2.username

    def test_contact_label(self):
        c1 = ContactLabel.mock(1)
        c1_other = ContactLabel.mock(1)
        c2 = ContactLabel.mock(2)

        assert c1.label_id == c1_other.label_id
        assert c1.label_id != c2.label_id


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
        self.merge_by_table(Contact)
        self.merge_by_table(ContactHeadImgUrl)
        self.merge_by_table(ContactLabel, 5)

    def merge_by_table(self, cls: UserTable = None, n=DB_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()

    def test_get_all_contact(self):
        res = self.db.get_contact_list()
        cnt = self.db.count_all(Contact)
        assert len(res) == cnt

    def test_get_one_contact(self):
        res = Contact.mock(1)
        user = self.db.get_contact_by_username(res.username)
        assert user is not None

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
        self.merge_by_table(Contact)
        self.merge_by_table(ContactHeadImgUrl)
        self.merge_by_table(ContactLabel, 5)

    def merge_by_table(self, cls: UserTable = None, n=CACHE_N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()
