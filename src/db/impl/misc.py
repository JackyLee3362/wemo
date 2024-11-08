from __future__ import annotations

from sqlalchemy import LargeBinary, Column, String, Integer

from common import RC
from db.abstract_user_db import Base, UserDB
from utils import singleton

# 二进制头像
MISC = "Misc"


class BizContactHeadImg(Base):
    __tablename__ = "BizContactHeadImg"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadBuf = Column("smallHeadBuf", LargeBinary)
    m_headImgMD5 = Column("m_headImgMD5", String)

    def __hash__(self):
        return self.usrName

    def __eq__(self, other: BizContactHeadImg):
        return (
            self.usrName == other.usrName
            and self.createTime == other.createTime
            and self.smallHeadBuf == other.smallHeadBuf
            and self.m_headImgMD5 == other.m_headImgMD5
        )

    def __repr__(self):
        return f"<联系人头像[test]: {self.usrName}>"


class ContactHeadImg1(Base):
    __tablename__ = "ContactHeadImg1"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadBuf = Column("smallHeadBuf", LargeBinary)
    m_headImgMD5 = Column("m_headImgMD5", String)

    def __hash__(self):
        return self.usrName

    def __eq__(self, other: BizContactHeadImg):
        return (
            self.usrName == other.usrName
            and self.createTime == other.createTime
            and self.smallHeadBuf == other.smallHeadBuf
            and self.m_headImgMD5 == other.m_headImgMD5
        )

    def __repr__(self):
        return f"<联系人头像: {self.usrName}>"


@singleton
class MiscCache(UserDB):
    def __init__(self):
        super().__init__(RC.USER_CACHE_DB, MISC)
        self.register_tables([
            BizContactHeadImg,
            ContactHeadImg1
        ])
        self.connect_db()


@singleton
class Misc(UserDB):
    def __init__(self):
        super().__init__(RC.USER_DB, MISC)
        self.register_tables([
            BizContactHeadImg,
            ContactHeadImg1
        ])
        self.connect_db()

    def get_avatar_buffer(self, usr_name: str) -> ContactHeadImg1:
        cls = ContactHeadImg1
        return self.session.query(cls).filter(
            cls.usrName == usr_name).one_or_none()
