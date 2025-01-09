from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import Column, Integer, LargeBinary, String, and_, case, not_, or_

from wemo.backend.database.db import AbsUserCache, AbsUserDB, WxUserTable

logger = logging.getLogger(__name__)
# 联系人信息

WX_SYS_USERNAME = [
    "tmessage",
    "medianote",
    "floatbottle",
    "fmessage",
    "qqmail",
    "filehelper",
]


class Contact(WxUserTable):
    __tablename__ = "Contact"

    # qmessage qq离线消息, tmessage, medianote 语音记事本, floatbottle 漂流瓶
    # fmessage 朋友推荐消息, qqmail qq邮箱, filehelper 文件传输助手
    username = Column("UserName", String, primary_key=True)  # 原始微信号

    alias = Column("Alias", String)  # 更改后的微信号
    encrypt_username = Column("EncryptUserName", String)
    del_flag = Column("DelFlag", Integer)
    # type（不是很准确，猜测）
    # 4 表示是群友
    # 2 表示群组
    # 33 表示qq邮箱
    # 2050 表示置顶群组
    # 2051 表示星标公众号和置顶好友
    # 65537 表示不看 Ta
    # 65539 表示不看 Ta pyq
    # 8388609 表示仅聊天
    # 8388611 表示仅聊天
    # 8454147 表示仅聊天
    type = Column("Type", Integer)
    verify_flag = Column("VerifyFlag", Integer)  # 0 表示是好友
    r1 = Column("Reserved1", Integer)
    # r2 = 1 表示好友，2 表示群组用户
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
    # r5 = 2048 表示置顶好友 和 文件传输助手
    r5 = Column("Reserved5", Integer)
    # r6 备注
    r6 = Column("Reserved6", String)
    r7 = Column("Reserved7", String)
    extra_buf = Column("ExtraBuf", LargeBinary)
    r8 = Column("Reserved8", Integer)
    r9 = Column("Reserved9", Integer)
    r10 = Column("Reserved10", String)
    r11 = Column("Reserved11", String)

    @property
    def repr_name(self):
        return self.remark or self.nick_name or self.username

    def __eq__(self, o: Contact):
        return (
            self.username == o.username
            and self.remark == o.remark
            and self.nick_name == o.nick_name
        )

    def __hash__(self):
        return hash(self.username)

    def __repr__(self):
        return f"{self.username}-NickName:{self.nick_name}-Remark:{self.remark}"


@dataclass
class ContactHeadImgUrl(WxUserTable):
    __tablename__ = "ContactHeadImgUrl"

    username = Column("usrName", String, primary_key=True)
    small_url = Column("smallHeadImgUrl", String)
    big_url = Column("bigHeadImgUrl", String)
    md5 = Column("headImgMd5", String)
    r0 = Column("reverse0", Integer)
    r1 = Column("reverse1", String)

    def __eq__(self, o: ContactHeadImgUrl):
        return (
            self.username == o.username
            and self.small_url == o.small_url
            and self.big_url == o.big_url
        )

    def __hash__(self):
        return hash(self.username)


@dataclass
class ContactLabel(WxUserTable):
    __tablename__ = "ContactLabel"

    label_id = Column("LabelID", Integer, primary_key=True)
    label_name = Column("LabelName", String)
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", Integer)
    r3 = Column("Reserved3", String)
    r4 = Column("Reserved4", String)
    res_data = Column("RespData", LargeBinary)
    r5 = Column("Reserved5", LargeBinary)

    def __eq__(self, o: ContactLabel):
        return self.label_id == o.label_id and self.label_name == o.label_name

    def __hash__(self):
        return hash(self.label_id)


class MicroMsgCache(AbsUserCache):
    def __init__(self, user_cache_db_url):
        super().__init__(user_cache_db_url)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])


class MicroMsg(AbsUserDB):
    def __init__(self, user_db_url):
        super().__init__(user_db_url)
        self.register_tables([Contact, ContactHeadImgUrl, ContactLabel])

    def get_contact_list(self) -> list[Contact]:
        """获取所有联系人信息"""
        # qmessage qq离线消息, tmessage, medianote 语音记事本, floatbottle 漂流瓶
        # fmessage 朋友推荐消息, qqmail qq邮箱, filehelper 文件传输助手
        res = (
            self.session.query(Contact)
            .filter(and_(Contact.r2 == 1, Contact.verify_flag == 0))
            .filter(not_(Contact.username.contains("@chatroom")))
            .filter(Contact.username.not_in(WX_SYS_USERNAME))
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
        """根据备注或昵称获取用户信息"""
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
