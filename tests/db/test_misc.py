from db.misc import BizContactHeadImg, ContactHeadImg1, Misc
import uuid
import pytest
from sqlalchemy import null
import time


@pytest.fixture
def misc() -> Misc:
    misc = Misc()
    return misc


def test_temp(misc: Misc):
    res = misc.session.get(BizContactHeadImg, "2")
    print(res)


def test_singleton(misc: Misc):
    """测试单例"""
    misc2 = Misc()
    assert misc == misc2


def test_query_all(misc: Misc):
    """测试查询全部"""
    res = misc.query_all(BizContactHeadImg)
    assert res is not None

    res = misc.query_all(ContactHeadImg1)
    assert res is not None


def test_count_all(misc: Misc):
    res = misc.count_all(BizContactHeadImg)
    print(f"待查表中的数据量是 {res}")
    assert res >= 0


def test_insert(misc: Misc):
    """测试插入"""
    misc.insert_all(
        [
            BizContactHeadImg(
                usrName=str(uuid.uuid4()), createTime=time.time(), smallHeadBuf=null()
            ),
            BizContactHeadImg(
                usrName=str(uuid.uuid4()), createTime=time.time(), smallHeadBuf=null()
            ),
        ],
        BizContactHeadImg,
    )


def test_update(misc: Misc):
    """测试更新"""
    biz = (
        misc.session.query(BizContactHeadImg)
        .filter(BizContactHeadImg.usrName == "2")
        .one_or_none()
    )
    if biz is None:
        return 
    biz.createTime = time.time()
    misc.session.commit()

    misc.session.query(BizContactHeadImg).filter(
        BizContactHeadImg.usrName == "3"
    ).update({BizContactHeadImg.createTime: 1000})
    misc.session.commit()


def test_update_db_by_table(misc: Misc):
    misc.update_db_from_cache_by_table(BizContactHeadImg)


def test_update_db(misc: Misc):
    misc.update_db_from_cache_by_all()


def test_query_avatar(misc: Misc):
    avatar = misc.get_avatar_buffer("2")
    print(avatar)
