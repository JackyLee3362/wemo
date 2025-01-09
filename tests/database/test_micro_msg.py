import logging
import shutil

from wemo.backend.database.micro_msg import Contact
from wemo.backend.database.micro_msg import MicroMsg as DB
from wemo.backend.database.micro_msg import MicroMsgCache as DBCache
from wemo.backend.utils.mock import (
    mock_contact,
    mock_contact_label,
    mock_contant_head_img_url,
    mock_ctx,
)

DB_N = 2
CACHE_N = 3
wxid = "test_database"
db_name = "MicroMsg.db"

ctx = mock_ctx(wxid)

user_data_db_dir = ctx.user_data_dir.user_root_dir
user_cache_db_dir = ctx.user_cache_dir.user_root_dir

logger = logging.getLogger(__name__)

db = DB(user_data_db_dir.joinpath(db_name))
cache = DBCache(user_cache_db_dir.joinpath(db_name))


class TestMock:

    def test_contact_head_img_url(self):
        c1 = mock_contant_head_img_url(1)
        c1_other = mock_contant_head_img_url(1)
        c2 = mock_contant_head_img_url(2)

        assert c1.username == c1_other.username
        assert c1.username != c2.username

    def test_contact(self):
        c1 = mock_contact(1)
        c1_other = mock_contact(1)
        c2 = mock_contact(2)

        assert c1.username == c1_other.username
        assert c1.username != c2.username

    def test_contact_label(self):
        c1 = mock_contact_label(1)
        c1_other = mock_contact_label(1)
        c2 = mock_contact_label(2)

        assert c1.label_id == c1_other.label_id
        assert c1.label_id != c2.label_id


class TestDB:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_data_db_dir
        shutil.rmtree(self.db_dir)

        # 准备数据库
        self.db = db
        self.db.init()

        def insert_all(mock_func=None, n=DB_N):
            self.db.insert_all([mock_func(i) for i in range(n)])

        insert_all(mock_func=mock_contact)
        insert_all(mock_func=mock_contant_head_img_url)
        insert_all(mock_func=mock_contact_label, n=5)

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
        self.merge_by_table(mock_contact)
        self.merge_by_table(mock_contant_head_img_url)
        self.merge_by_table(mock_contact_label, 5)

    def merge_by_table(self, mock_func, n=CACHE_N):
        cache_data = [mock_func(i) for i in range(n)]
        db_data = self.db.query_all(mock_func)
        self.test_count_all()
        self.db.merge_all(mock_func, db_data, cache_data)
        self.test_count_all()

    def test_get_all_contact(self):
        res = self.db.get_contact_list()
        cnt = self.db.count_all(Contact)
        assert len(res) == cnt

    def test_get_one_contact(self):
        res = mock_contact(1)
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
        self.merge_by_table(mock_contact)
        self.merge_by_table(mock_contant_head_img_url)
        self.merge_by_table(mock_contact_label, 5)

    def merge_by_table(self, mock_func, n=CACHE_N):
        res = [mock_func(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()
