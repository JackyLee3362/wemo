from __future__ import annotations
from utils.singleton import singleton


from .userdb import Base, UserDB, UserTable
from sqlalchemy import LargeBinary, Column, String, Integer

# 二进制头像
MISC = "Misc"


class BizContactHeadImg(Base, UserTable):
    __tablename__ = "BizContactHeadImg"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadImgBuf = Column("smallHeadBuf", LargeBinary)
    mHeadImgMD5 = Column("m_headImgMD5", String)

    def __hash__(self):
        return self.usrName

    def __eq__(self, other: BizContactHeadImg):
        return (
            self.usrName == other.usrName
            and self.createTime == other.createTime
            and self.smallHeadImgBuf == other.smallHeadImgBuf
            and self.mHeadImgMD5 == other.mHeadImgMD5
        )

    def __repr__(self):
        return f"<联系人头像: {self.usrName}>"

    def update(self, obj: BizContactHeadImg):
        self.createTime = obj.createTime
        self.smallHeadImgBuf = obj.smallHeadImgBuf
        self.mHeadImgMD5 = obj.mHeadImgMD5


class ContactHeadingImg1(Base, UserTable):
    __tablename__ = "ContactHeadingImg1"

    usrName = Column("usrName", String, primary_key=True)
    createTime = Column("createTime", Integer)
    smallHeadImgBuf = Column("smallHeadBuf", LargeBinary)
    mHeadImgMD5 = Column("m_headImgMD5", String)

    def __repr__(self):
        return f"<联系人头像: {self.usrName}>"

    def update(self, obj: ContactHeadingImg1):
        self.usrName = obj.usrName
        self.createTime = obj.createTime
        self.smallHeadImgBuf = obj.smallHeadImgBuf
        self.mHeadImgMD5 = obj.mHeadImgMD5


@singleton
class Misc(UserDB):
    def __init__(self, wxid):
        super().__init__(wxid, MISC)

    def get_avatar_buffer(self, userName):
        cls = BizContactHeadImg
        self.session.query(cls).filter(cls.usrName == userName).one_or_none()
