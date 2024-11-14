from __future__ import annotations

import random

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_, case

from wemo.database.db import AbsUserDB
from wemo.database.db import UserTable
from wemo.model.dto import ContactDTO
from wemo.utils.utils import mock_url, mock_user, singleton


# 联系人信息


class Contact(UserTable):
    __tablename__ = "Contact"

    user_name = Column("UserName", String, primary_key=True)  # 原始微信号
    alias = Column("Alias", String)  # 更改后的微信号
    encrypt_user_name = Column("EncryptUserName", String)
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
        return f"{self.user_name}-NickName:{self.nick_name}-Remark:{self.remark}"

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

    def mapper2dto(self) -> ContactDTO:
        return ContactDTO(
            user_name=self.user_name,
            alias=self.alias,
            type=self.type,
            remark=self.remark,
            nick_name=self.nick_name,
            py_initial=self.py_initial,
            remark_py_initial=self.remark_py_initial,
            small_head_img_url=self.small_head_img_url,
            big_head_img_url=self.big_head_img_url,
            exTra_buf=self.extra_buf,
            label_name_list=self.label_id_list,
        )


class ContactHeadImgUrl(UserTable):
    __tablename__ = "ContactHeadImgUrl"

    user_name = Column("usrName", String, primary_key=True)
    small_head_img_url = Column("smallHeadImgUrl", String)
    big_head_img_url = Column("bigHeadImgUrl", String)
    head_img_md5 = Column("headImgMd5", String)
    r0 = Column("reverse0", Integer)
    r1 = Column("reverse1", String)

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
        return ContactLabel(LabelID=seed, LabelName=names[seed])


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

    def list_contact(self):
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

    def get_contact_and_labels_by_username(
        self, username: str
    ) -> tuple[Contact, list[ContactLabel]]:
        """根据用户名获取用户信息"""
        contact = (
            self.session.query(Contact)
            .filter(Contact.user_name == username)
            .one_or_none()
        )
        if contact is None:
            return Contact(), []
        contact_img = (
            self.session.query(ContactHeadImgUrl)
            .filter(ContactHeadImgUrl.user_name == username)
            .one_or_none()
        )
        contact.big_head_img_url = contact_img.big_head_img_url
        contact.small_head_img_url = contact_img.small_head_img_url
        contact_labels = (
            self.session.query(ContactLabel)
            .filter(ContactLabel.label_id == contact.label_id_list)
            .all()
        )
        return (contact, contact_labels)
