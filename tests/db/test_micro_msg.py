from db.micro_msg import MicroMsg, Contact, ContactHeadImgUrl, ContactLabel
import pytest

wxid = "wxid_h8cex1v6segm21"


@pytest.fixture
def microMsg() -> MicroMsg:
    microMsg = MicroMsg()
    return microMsg


def test_singleton(microMsg: MicroMsg):
    """测试单例"""
    microMsg2 = MicroMsg()
    assert microMsg == microMsg2


def test_query_all(microMsg: MicroMsg):
    """测试查询全部"""
    res = microMsg.query_all(Contact)
    assert len(res) > 0

    res = microMsg.query_all(ContactHeadImgUrl)
    assert len(res) > 0

    res = microMsg.query_all(ContactLabel)
    assert len(res) > 0


def test_insert(microMsg: MicroMsg):
    """测试插入"""
    pass


def test_update_db_by_table(microMsg: MicroMsg):
    microMsg.update_db_from_cache_by_table(Contact)


def test_update_db(microMsg: MicroMsg):
    microMsg.update_db_from_cache_by_all()


def test_get_contact(microMsg: MicroMsg):
    res = microMsg.get_contact()
    assert len(res) > 0
