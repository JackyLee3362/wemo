from __future__ import annotations
import sqlite3
from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import or_, and_, asc, desc, case

from utils import singleton

from .userdb import Base, UserDB

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
class MicroMsg(UserDB):
    def __init__(self):
        super().__init__(MICRO_MSG)
        self.register_table(Contact)
        self.register_table(ContactHeadImgUrl)
        self.register_table(ContactLabel)
        self.connect()
        self.init_session()

    def get_contact(self):
        res = (
            self.session.query(Contact, ContactHeadImgUrl, ContactLabel)
            .filter(Contact.UserName == ContactHeadImgUrl.usrName)
            .filter(Contact.LabelIdList == ContactLabel.LabelID)
            .filter(and_(Contact.Type != 4, Contact.VerifyFlag == 0))
            .order_by(
                case(
                    (Contact.RemarkPYInitial == "", Contact.PYInitial),
                    else_=Contact.RemarkPYInitial,
                )
            ).all()
        )
        return res

    def get_contact_by_username_old(self, username: object) -> object:
        try:
            sql = """
                   SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,ContactLabel.LabelName
                   FROM Contact
                   INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                   LEFT JOIN ContactLabel ON Contact.LabelIDList = ContactLabel.LabelId
                   WHERE UserName = ?
                """
            result = self.execute_sql(sql, [username], fetchAll=False)
        except sqlite3.OperationalError:
            # 解决ContactLabel表不存在的问题
            # lock.acquire(True)
            sql = """
                   SELECT UserName, Alias, Type, Remark, NickName, PYInitial, RemarkPYInitial, ContactHeadImgUrl.smallHeadImgUrl, ContactHeadImgUrl.bigHeadImgUrl,ExTraBuf,"None"
                   FROM Contact
                   INNER JOIN ContactHeadImgUrl ON Contact.UserName = ContactHeadImgUrl.usrName
                   WHERE UserName = ?
            """
            result = self.execute_sql(sql, [username], fetchAll=False)
        return result

    def get_chatroom_info(self, chatroomname):
        """
        获取群聊信息
        """
        sql = """SELECT ChatRoomName, RoomData FROM ChatRoom WHERE ChatRoomName = ?"""
        return self.execute_sql(sql, [chatroomname], fetchAll=False)
