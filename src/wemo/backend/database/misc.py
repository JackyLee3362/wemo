from __future__ import annotations

from dataclasses import dataclass
import logging
import random

from sqlalchemy import LargeBinary, Column, String, Integer

from wemo.backend.database.db import AbsUserCache, AbsUserDB
from wemo.backend.database.db import UserTable
from wemo.backend.utils.mock import mock_bytes, mock_user
from wemo.backend.utils.mock import mock_timestamp


# 二进制头像
logger = logging.getLogger(__name__)


class BizContactHeadImg(UserTable):
    __tablename__ = "BizContactHeadImg"

    username = Column("usrName", String, primary_key=True)
    create_time = Column("createTime", Integer)
    buf = Column("smallHeadBuf", LargeBinary)
    md5 = Column("m_headImgMD5", String)

    def __eq__(self, o: BizContactHeadImg):
        return self.username == o.username and self.create_time == o.create_time

    def __hash__(self):
        return hash(self.username)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return BizContactHeadImg(
            username=mock_user(seed),
            create_time=mock_timestamp(),
            buf=mock_bytes(),
        )


@dataclass
class ContactHeadImg1(UserTable):
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

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return ContactHeadImg1(
            username=mock_user(seed),
            create_time=mock_timestamp(),
            buf=mock_bytes(),
        )


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
