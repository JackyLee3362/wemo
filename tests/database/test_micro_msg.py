from pathlib import Path
from wemo.base.db import UserTable
from wemo.base.logging import default_console_logger
from wemo.database.micro_msg import MicroMsg, Contact, ContactHeadImgUrl, ContactLabel
from wemo import constant

N = 200
name = "test_database"
user_dir = constant.DATA_DIR.joinpath(name)
LOG = default_console_logger(name)


class TestMock:

    def test_contact_head_img_url(self):
        c1 = ContactHeadImgUrl.mock(1)
        c1_other = ContactHeadImgUrl.mock(1)
        c2 = ContactHeadImgUrl.mock(2)

        assert c1.usrName == c1_other.usrName
        assert c1.usrName != c2.usrName

    def test_contact(self):
        c1 = Contact.mock(1)
        c1_other = Contact.mock(1)
        c2 = Contact.mock(2)

        assert c1.UserName == c1_other.UserName
        assert c1.UserName != c2.UserName

    def test_contact_label(self):
        c1 = ContactLabel.mock(1)
        c1_other = ContactLabel.mock(1)
        c2 = ContactLabel.mock(2)

        assert c1.LabelID == c1_other.LabelID
        assert c1.LabelID != c2.LabelID


class TestMicroMsg:

    def setup_class(self):
        # 指定目录
        self.db_dir = user_dir
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # 准备数据库
        self.db = MicroMsg(self.db_dir, LOG)
        self.db.init_db()

    def test_singleton(self):
        db2 = MicroMsg(self.db_dir, LOG)
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

    def merge_by_table(self, cls: UserTable = None, n=N):
        res = [cls.mock(i) for i in range(n)]
        self.test_count_all()
        self.db.merge_all(res)
        self.test_count_all()

    def test_get_all_contact(self):
        res = self.db.list_contact()
        cnt = self.db.count_all(Contact)
        assert len(res) == cnt

    def test_get_one_contact(self):
        res = Contact.mock(1)
        user = self.db.get_contact_by_username(res.UserName)
        assert user is not None

    def teardown_class(self):
        self.db.close_session()
