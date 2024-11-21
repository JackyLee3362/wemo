from __future__ import annotations

from dataclasses import dataclass
import random

from sqlalchemy import LargeBinary, Column, String, Integer

from wemo.backend.database.db import AbsUserDB
from wemo.backend.database.db import UserTable
from wemo.backend.utils.utils import mock_bytes, mock_timestamp, mock_user, singleton


# 二进制头像


class BizContactHeadImg(UserTable):
    __tablename__ = "BizContactHeadImg"

    username = Column("usrName", String, primary_key=True)
    create_time = Column("createTime", Integer)
    buf = Column("smallHeadBuf", LargeBinary)
    md5 = Column("m_headImgMD5", String)

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


@singleton
class MiscCache(AbsUserDB):
    def __init__(self, user_cache_db_url, logger=None):
        super().__init__(user_cache_db_url, logger=logger)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])


@singleton
class Misc(AbsUserDB):
    def __init__(self, user_db_url, logger=None):
        super().__init__(user_db_url, logger=logger)
        self.register_tables([BizContactHeadImg, ContactHeadImg1])

    def get_avatar_buffer(self, username: str) -> ContactHeadImg1:
        return (
            self.session.query(ContactHeadImg1)
            .filter(ContactHeadImg1.username == username)
            .one_or_none()
        )