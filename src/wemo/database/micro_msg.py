from __future__ import annotations

import random
from typing import List, Tuple

from wemo.base.db import AbsUserDB
from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_, case

from wemo.utils import mock_url, mock_user, singleton
from wemo.base.db import UserTable

# 联系人信息


class Contact(UserTable):
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

    def __repr__(self):
        return f"{self.UserName}-NickName:{self.NickName}-Remark:{self.Remark}"

    @staticmethod
    def mock(seed):
        random.seed(seed)
        user = mock_user(seed)
        alias = None
        if seed % 2 == 0:
            alias = "alias:" + user

        return Contact(
            UserName=user,
            Alias=alias,
            DelFlag=0,
            Type=3,
            VerifyFlag=0,  # 0 表示是好友
        )


class ContactHeadImgUrl(UserTable):
    __tablename__ = "ContactHeadImgUrl"

    usrName = Column("usrName", String, primary_key=True)
    smallHeadImgUrl = Column("smallHeadImgUrl", String)
    bigHeadImgUrl = Column("bigHeadImgUrl", String)
    headImgMd5 = Column("headImgMd5", String)
    reverse0 = Column("reverse0", Integer)
    reverse1 = Column("reverse1", String)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        username = mock_user(seed)
        url = mock_url(seed)
        return ContactHeadImgUrl(
            usrName=username,
            smallHeadImgUrl=url,
            bigHeadImgUrl=url + "bigHead",
            reverse0=0,
        )


class ContactLabel(UserTable):
    __tablename__ = "ContactLabel"

    LabelID = Column("LabelID", Integer, primary_key=True)
    LabelName = Column("LabelName", String)
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", Integer)
    Reserved3 = Column("Reserved3", String)
    Reserved4 = Column("Reserved4", String)
    RespData = Column("RespData", LargeBinary)
    Reserved5 = Column("Reserved5", LargeBinary)

    @staticmethod
    def mock(seed):
        names = {0: "默认", 1: "家人", 2: "朋友", 3: "同事", 4: "同学", 5: "其他"}
        if seed not in names.keys():
            raise ValueError("seed too large")
        return ContactLabel(LabelID=seed, LabelName=names[seed])


@singleton
class MicroMsgCache(AbsUserDB):
    def __init__(self, user_cache_db_dir, logger=None):
        super().__init__(user_cache_db_dir, db_name=MicroMsg.__name__, logger=logger)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])


@singleton
class MicroMsg(AbsUserDB):
    def __init__(self, user_db_dir, logger=None):
        super().__init__(user_db_dir, logger=logger)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])

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
