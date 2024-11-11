from __future__ import annotations
import random
from venv import create

from sqlalchemy import LargeBinary, Column, String, Integer

from wemo.base.db import AbsUserDB
from wemo.base.db import UserTable
from wemo.utils import mock_bytes, mock_timestamp, mock_user, singleton

# 二进制头像


class BizContactHeadImg(UserTable):
    __tablename__ = "BizContactHeadImg"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadBuf = Column("smallHeadBuf", LargeBinary)
    m_headImgMD5 = Column("m_headImgMD5", String)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return BizContactHeadImg(
            usrName=mock_user(seed),
            createTime=mock_timestamp(),
            smallHeadBuf=mock_bytes(),
        )


class ContactHeadImg1(UserTable):
    __tablename__ = "ContactHeadImg1"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadBuf = Column("smallHeadBuf", LargeBinary)
    m_headImgMD5 = Column("m_headImgMD5", String)

    def __repr__(self):
        return f"<联系人头像: {self.usrName}>"

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return ContactHeadImg1(
            usrName=mock_user(seed),
            createTime=mock_timestamp(),
            smallHeadBuf=mock_bytes(),
        )


@singleton
class MiscCache(AbsUserDB):
    def __init__(self, user_cache_db_dir, logger=None):
        super().__init__(user_cache_db_dir, db_name=Misc.__name__, logger=logger)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])


@singleton
class Misc(AbsUserDB):
    def __init__(self, user_db_dir, logger=None):
        super().__init__(user_db_dir, logger=logger)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])

    def get_avatar_buffer(self, usr_name: str) -> ContactHeadImg1:
        cls = ContactHeadImg1
        return self.session.query(cls).filter(cls.usrName == usr_name).one_or_none()
