from sqlite3 import connect
from db.misc import BizContactHeadImg, Misc
import pytest

wxid = "wxid_h8cex1v6segm21"


@pytest.fixture
def misc() -> Misc:
    misc = Misc("test")
    misc.connect()
    misc.init_session()
    return misc


def test_singleton(misc: Misc):
    misc2 = Misc(wxid)
    assert misc == misc2


def test_query(misc: Misc):
    res = misc.query_all(BizContactHeadImg)
    print(res)
    assert res is not None


def test_insert(misc: Misc):
    misc.insert_all([BizContactHeadImg(usrName="xxx", createTime=1)])


def test_update(misc: Misc):
    biz = (
        misc.session.query(BizContactHeadImg)
        .filter(BizContactHeadImg.usrName == "2")
        .one()
    )
    biz.createTime = 10
    misc.session.commit()


def test_update_db_by_table(misc: Misc):
    misc.update_db_from_cache_by_table(BizContactHeadImg)


def test_update_db(misc: Misc):
    misc.update_db_from_cache()
