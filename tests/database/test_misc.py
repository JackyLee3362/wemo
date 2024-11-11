from pathlib import Path
from wemo.base.db import UserTable
from wemo.base.logging import default_console_logger
from wemo.database.misc import BizContactHeadImg, ContactHeadImg1, Misc
from wemo import constant

N = 200
name = "test_database"
user_dir = constant.DATA_DIR.joinpath(name)
LOG = default_console_logger(name)


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


class TestMisc:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = Misc(self.db_dir, LOG)
        self.db.init_db()

    def test_singleton(self):
        db2 = Misc(self.db_dir, LOG)
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

    def merge_by_table(self, cls: UserTable = None, n=N):
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