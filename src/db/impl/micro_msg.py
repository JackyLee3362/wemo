from __future__ import annotations

from typing import List, Tuple

from db.abstract_db import AbstractUserDB
from db.abstract_user_db import Base, UserDB
from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_, case

from common import RC
from utils import singleton

# 联系人信息
MICRO_MSG = "MicroMsg"


class Contact(Base):
    __tablename__ = "Contact"

    UserName = Column("UserName", String, primary_key=True)  # 原始微信号
    Alias = Column("Alias", String)  # 更改后的微信号
    EncryptUserName = Column("EncryptUserName", String)
    DelFlag = Column("DelFlag", Integer)
    Type = Column("Type", Integer)  # type 4: 表示是群友
    VerifyFlag = Column("VerifyFlag", Integer)  # 0 表示是好友
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", Integer)
    Reserved3 = Column("Reserved3", String)
    Reserved4 = Column("Reserved4", String)
    Remark = Column("Remark", String)  # 我给的备注
    NickName = Column("NickName", String)  # 自己取的昵称
    LabelIdList = Column("LabelIdList", String)
    DomainList = Column("DomainList", String)
    ChatRoomType = Column("ChatRoomType", Integer)
    PYInitial = Column("PYInitial", String)
    QuanPin = Column("QuanPin", String)
    RemarkPYInitial = Column("RemarkPYInitial", String)
    RemarkQuanPin = Column("RemarkQuanPin", String)
    BigHeadImgUrl = Column("BigHeadImgUrl", String)
    SmallHeadImgUrl = Column("SmallHeadImgUrl", String)
    HeadImgMd5 = Column("HeadImgMd5", String)
    ChatRoomNotify = Column("ChatRoomNotify", Integer)
    Reserved5 = Column("Reserved5", Integer)
    Reserved6 = Column("Reserved6", String)
    Reserved7 = Column("Reserved7", String)
    ExtraBuf = Column("ExtraBuf", LargeBinary)
    Reserved8 = Column("Reserved8", Integer)
    Reserved9 = Column("Reserved9", Integer)
    Reserved10 = Column("Reserved10", String)
    Reserved11 = Column("Reserved11", String)

    def __hash__(self):
        return self.UserName

    def __eq__(self, o: Contact):
        return (
            self.UserName == o.UserName
            and self.Alias == o.Alias
            and self.Remark == self.Remark
            and self.NickName == o.NickName
            and self.LabelIdList == o.LabelIdList
        )

    def __repr__(self):
        return f"{self.UserName}-NickName:{self.NickName}-Remark:{self.Remark}"


class ContactHeadImgUrl(Base):
    __tablename__ = "ContactHeadImgUrl"

    usrName = Column("usrName", String, primary_key=True)
    smallHeadImgUrl = Column("smallHeadImgUrl", String)
    bigHeadImgUrl = Column("bigHeadImgUrl", String)
    headImgMd5 = Column("headImgMd5", String)
    reverse0 = Column("reverse0", Integer)
    reverse1 = Column("reverse1", String)

    def __hash__(self):
        return self.usrName

    def __eq__(self, o: ContactHeadImgUrl):
        return (
            self.usrName == o.usrName
            and self.smallHeadImgUrl == o.smallHeadImgUrl
            and self.bigHeadImgUrl == o.bigHeadImgUrl
            and self.reverse0 == o.reverse0
            and self.reverse1 == o.reverse1
        )


class ContactLabel(Base):
    __tablename__ = "ContactLabel"

    LabelID = Column("LabelID", Integer, primary_key=True)
    LabelName = Column("LabelName", String)
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", Integer)
    Reserved3 = Column("Reserved3", String)
    Reserved4 = Column("Reserved4", String)
    RespData = Column("RespData", LargeBinary)
    Reserved5 = Column("Reserved5", LargeBinary)

    def __hash__(self):
        return self.LabelID

    def __eq__(self, o: ContactLabel):
        return (
            self.LabelName == o.LabelName
            and self.Reserved1 == o.Reserved1
            and self.Reserved2 == o.Reserved2
            and self.Reserved3 == o.Reserved3
            and self.Reserved4 == o.Reserved4
        )


@singleton
class MicroMsgCache(AbstractUserDB):
    def __init__(self):
        super().__init__(RC.USER_CACHE_DB, MICRO_MSG)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])


@singleton
class MicroMsg(AbstractUserDB):
    def __init__(self):
        super().__init__(RC.USER_DB, MICRO_MSG)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])
        self.connect_db()

    def list_contact(self):
        """获取所有联系人信息"""
        res = (
            self.session.query(Contact)
            .filter(and_(Contact.Type != 4, Contact.VerifyFlag == 0))
            .order_by(
                case(
                    (Contact.RemarkPYInitial == "", Contact.PYInitial),
                    else_=Contact.RemarkPYInitial,
                )
            )
            .all()
        )
        return res

    def get_contact_by_username(
        self, username: str
    ) -> Tuple[Contact, List[ContactLabel]]:
        """根据用户名获取用户信息"""
        contact = (
            self.session.query(Contact)
            .filter(Contact.UserName == username)
            .one_or_none()
        )
        if contact is None:
            return Contact(), []
        contactImg = (
            self.session.query(ContactHeadImgUrl)
            .filter(ContactHeadImgUrl.usrName == username)
            .one_or_none()
        )
        contact.BigHeadImgUrl = contactImg.bigHeadImgUrl
        contact.SmallHeadImgUrl = contactImg.smallHeadImgUrl
        contactLabel = (
            self.session.query(ContactLabel)
            .filter(ContactLabel.LabelID == contact.LabelIdList)
            .all()
        )
        return (contact, contactLabel)
