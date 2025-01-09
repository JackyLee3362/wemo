from __future__ import annotations

import logging
from dataclasses import dataclass

from sqlalchemy import Column, Integer, LargeBinary, String

from wemo.backend.database.db import AbsUserCache, AbsUserDB, WxUserTable

# 二进制头像
logger = logging.getLogger(__name__)


class BizContactHeadImg(WxUserTable):
    __tablename__ = "BizContactHeadImg"

    username = Column("usrName", String, primary_key=True)
    create_time = Column("createTime", Integer)
    buf = Column("smallHeadBuf", LargeBinary)
    md5 = Column("m_headImgMD5", String)

    def __eq__(self, o: BizContactHeadImg):
        return self.username == o.username and self.create_time == o.create_time

    def __hash__(self):
        return hash(self.username)


@dataclass
class ContactHeadImg1(WxUserTable):
    __tablename__ = "ContactHeadImg1"

    username = Column("usrName", String, primary_key=True)
    create_time = Column("createTime", Integer)
    buf = Column("smallHeadBuf", LargeBinary)
    md5 = Column("m_headImgMD5", String)

    def __eq__(self, o: ContactHeadImg1):
        return self.username == o.username and self.create_time == o.create_time

    def __hash__(self):
        return hash(self.username)

    def __repr__(self):
        return f"<联系人头像: {self.username}>"


class MiscCache(AbsUserCache):
    def __init__(self, user_cache_db_url):
        super().__init__(user_cache_db_url)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])


class Misc(AbsUserDB):
    def __init__(self, user_db_url):
        super().__init__(user_db_url)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])

    def get_avatar_buffer(self, username: str) -> ContactHeadImg1:
        return (
            self.session.query(ContactHeadImg1)
            .filter(ContactHeadImg1.username == username)
            .one_or_none()
        )
