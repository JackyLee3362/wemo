from __future__ import annotations
from utils.singleton import singleton


from .userdb import Base, UserDB
from sqlalchemy import LargeBinary, Column, String, Integer


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
class Misc(UserDB):
    def __init__(self, wxid):
        super().__init__(wxid, MISC)
        self.register_table(BizContactHeadImg)
        self.register_table(ContactHeadImg1)
        self.connect()
        self.init_session()

    def get_avatar_buffer(self, userName):
        cls = BizContactHeadImg
        self.session.query(cls).filter(cls.usrName == userName).one_or_none()
