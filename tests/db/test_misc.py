from db.misc import BizContactHeadImg, Misc
import uuid
import pytest
from sqlalchemy import null

wxid = "wxid_h8cex1v6segm21"


@pytest.fixture
def misc() -> Misc:
    misc = Misc("test")
    misc.connect()
    misc.init_session()
    return misc


def test_singleton(misc: Misc):
    """测试单例"""
    misc2 = Misc(wxid)
    assert misc == misc2


def test_query_all(misc: Misc):
    """测试查询全部"""
    res = misc.query_all(BizContactHeadImg)
    print(res)
    assert res is not None


def test_insert(misc: Misc):
    """测试插入"""
    usrName = str(uuid.uuid4())
    misc.insert_all(
        [BizContactHeadImg(usrName=usrName, createTime=1, smallHeadImgBuf=null())]
    )


def test_update(misc: Misc):
    """测试更新"""
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


def test_query_avatar(misc: Misc):
    avatar = misc.get_avatar_buffer("2")
    print(avatar)