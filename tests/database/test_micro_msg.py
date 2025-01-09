import logging
import shutil

from wemo.backend.ctx import Context
from wemo.backend.database.db import UserTable
from wemo.backend.database.micro_msg import (
    MicroMsg as DB,
    MicroMsgCache as DBCache,
    Contact,
    ContactHeadImgUrl,
    ContactLabel,
)

DB_N = 2
CACHE_N = 3
wxid = "test_database"
db_name = "MicroMsg.db"
ctx = Context.mock_ctx(wxid)
user_data_db_dir = ctx.user_data_dir
user_cache_db_dir = ctx.user_cache_dir
logger = logging.getLogger(__name__)
db = DB(user_data_db_dir.user_root_dir.joinpath(db_name))
cache = DBCache(user_cache_db_dir.user_root_dir.joinpath(db_name))


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
        self.db_dir = user_data_db_dir
        shutil.rmtree(self.db_dir)
        self.db_dir.mkdir()

        # 准备数据库
        self.db = db
        self.db.init()

        def insert_all(cls: type[UserTable], n=DB_N):
            self.db.insert_all([cls.mock(i) for i in range(n)])

        insert_all(Contact)
        insert_all(ContactHeadImgUrl)
        insert_all(ContactLabel, 5)

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
        self.merge_by_table(Contact)
        self.merge_by_table(ContactHeadImgUrl)
        self.merge_by_table(ContactLabel, 5)

    def merge_by_table(self, cls: type[UserTable] = None, n=CACHE_N):
        cache_data = [cls.mock(i) for i in range(n)]
        db_data = self.db.query_all(cls)
        self.test_count_all()
        self.db.merge_all(cls, db_data, cache_data)
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
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir()

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
