from __future__ import annotations

from dataclasses import dataclass
import random

from sqlalchemy import Column, String, Integer, LargeBinary, or_
from sqlalchemy import and_, case

from wemo.database.db import AbsUserDB
from wemo.database.db import UserTable
from wemo.utils.utils import mock_url, mock_user, singleton


# 联系人信息


class Contact(UserTable):
    __tablename__ = "Contact"

    username = Column("UserName", String, primary_key=True)  # 原始微信号
    alias = Column("Alias", String)  # 更改后的微信号
    encrypt_username = Column("EncryptUserName", String)
    del_flag = Column("DelFlag", Integer)
    type = Column("Type", Integer)  # type 4: 表示是群友
    verify_flag = Column("VerifyFlag", Integer)  # 0 表示是好友
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", Integer)
    r3 = Column("Reserved3", String)
    r4 = Column("Reserved4", String)
    remark = Column("Remark", String)  # 我给的备注
    nick_name = Column("NickName", String)  # 自己取的昵称
    label_id_list = Column("LabelIdList", String)
    domain_list = Column("DomainList", String)
    chat_room_type = Column("ChatRoomType", Integer)
    py_initial = Column("PYInitial", String)
    quan_pin = Column("QuanPin", String)
    remark_py_initial = Column("RemarkPYInitial", String)
    remark_quan_pin = Column("RemarkQuanPin", String)
    big_head_img_url = Column("BigHeadImgUrl", String)
    small_head_img_url = Column("SmallHeadImgUrl", String)
    head_img_md5 = Column("HeadImgMd5", String)
    chat_room_notify = Column("ChatRoomNotify", Integer)
    r5 = Column("Reserved5", Integer)
    r6 = Column("Reserved6", String)
    r7 = Column("Reserved7", String)
    extra_buf = Column("ExtraBuf", LargeBinary)
    r8 = Column("Reserved8", Integer)
    r9 = Column("Reserved9", Integer)
    r10 = Column("Reserved10", String)
    r11 = Column("Reserved11", String)

    def __repr__(self):
        return f"{self.username}-NickName:{self.nick_name}-Remark:{self.remark}"

    @staticmethod
    def mock(seed):
        random.seed(seed)
        user = mock_user(seed)
        alias = None
        if seed % 2 == 0:
            alias = "alias:" + user

        return Contact(
            username=user,
            alias=alias,
            del_flag=0,
            type=3,
            verify_flag=0,  # 0 表示是好友
        )


@dataclass
class ContactHeadImgUrl(UserTable):
    __tablename__ = "ContactHeadImgUrl"

    username = Column("usrName", String, primary_key=True)
    small_url = Column("smallHeadImgUrl", String)
    big_url = Column("bigHeadImgUrl", String)
    md5 = Column("headImgMd5", String)
    r0 = Column("reverse0", Integer)
    r1 = Column("reverse1", String)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        username = mock_user(seed)
        url = mock_url(seed)
        return ContactHeadImgUrl(
            username=username,
            small_url=url,
            big_url=url + "bigHead",
            r0=0,
        )


@dataclass
class ContactLabel(UserTable):
    __tablename__ = "ContactLabel"

    label_id = Column("LabelID", Integer, primary_key=True)
    label_name = Column("LabelName", String)
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", Integer)
    r3 = Column("Reserved3", String)
    r4 = Column("Reserved4", String)
    res_data = Column("RespData", LargeBinary)
    r5 = Column("Reserved5", LargeBinary)

    @staticmethod
    def mock(seed):
        names = {0: "默认", 1: "家人", 2: "朋友", 3: "同事", 4: "同学", 5: "其他"}
        if seed not in names.keys():
            raise ValueError("seed too large")
        return ContactLabel(label_id=seed, label_name=names[seed])


@singleton
class MicroMsgCache(AbsUserDB):
    def __init__(self, user_cache_db_url, logger=None):
        super().__init__(user_cache_db_url, logger=logger)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])


@singleton
class MicroMsg(AbsUserDB):
    def __init__(self, user_db_url, logger=None):
        super().__init__(user_db_url, logger=logger)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])

    def get_contact_list(self) -> list[Contact]:
        """获取所有联系人信息"""
        res = (
            self.session.query(Contact)
            .filter(and_(Contact.type != 4, Contact.verify_flag == 0))
            .order_by(
                case(
                    (Contact.remark_py_initial == "", Contact.py_initial),
                    else_=Contact.remark_py_initial,
                )
            )
            .all()
        )
        return res

    def get_contact_by_username(self, username: str) -> Contact:
        """根据用户名获取用户信息"""
        contact = (
            self.session.query(Contact)
            .filter(Contact.username == username)
            .one_or_none()
        )
        if not contact:
            return
        contact_img = (
            self.session.query(ContactHeadImgUrl)
            .filter(ContactHeadImgUrl.username == username)
            .one_or_none()
        )
        contact.big_head_img_url = contact_img.big_url
        contact.small_head_img_url = contact_img.small_url
        return contact

    def get_contact_by_fuzzy_name(self, name: str) -> list[Contact]:
        """根据alias获取用户信息"""
        contacts = (
            self.session.query(Contact)
            .filter(
                or_(
                    Contact.remark.like(f"%{name}%"),
                    Contact.nick_name.like(f"%{name}%"),
                )
            )
            .all()
        )
        return contacts

    def get_labels_by_username(self, username: str) -> list[ContactLabel]:
        # :todo: 优化项
        contact = self.get_contact_by_username(username)
        if contact is None:
            return []
        labels = (
            self.session.query(ContactLabel)
            .filter(ContactLabel.label_id.in_(contact.label_id_list.split(",")))
            .all()
        )
        return labels
