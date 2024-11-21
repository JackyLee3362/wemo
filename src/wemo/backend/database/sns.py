from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Optional

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_

from wemo.backend.database.db import AbsUserDB
from wemo.backend.database.db import UserTable
from wemo.backend.utils.utils import (
    mock_sns_content,
    mock_timestamp,
    mock_user,
    singleton,
)


# 朋友圈


@dataclass
class Feed(UserTable):
    __tablename__ = "FeedsV20"
    feed_id = Column("FeedId", Integer, primary_key=True)
    create_time = Column("CreateTime", Integer)
    fault_id = Column("FaultId", Integer)
    type = Column("Type", Integer)
    username = Column("UserName", String)
    status = Column("Status", Integer)
    ext_flag = Column("ExtFlag", Integer)
    priv_flag = Column("PrivFlag", Integer)
    string_id = Column("StringId", String)
    content = Column("Content", String)
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", Integer)
    r3 = Column("Reserved3", String)
    r4 = Column("Reserved4", String)
    r5 = Column("Reserved5", Integer)
    r6 = Column("Reserved6", String)
    extra_buf = Column("ExtraBuf", LargeBinary)
    r7 = Column("Reserved7", LargeBinary)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return Feed(
            feed_id=-mock_timestamp() * 10,
            create_time=mock_timestamp(),
            fault_id=0,
            type=1,
            username=mock_user(seed),
            status=0,
            ext_flag=1,
            priv_flag=0,
            string_id=str(mock_timestamp() * 100),
            content=mock_sns_content(),
        )


@dataclass
class Comment(UserTable):
    __tablename__ = "CommentV20"

    feed_id = Column("FeedId", Integer, primary_key=True)
    comment_id = Column("CommentId", Integer, primary_key=True)
    create_time = Column("Createtime", Integer)
    flag = Column("Flag", Integer)
    comment_type = Column("CommentType", Integer, primary_key=True)
    comment_flag = Column("CommentFlag", Integer)
    content = Column("Content", String)
    from_username = Column("FromUserName", String, primary_key=True)
    client_id = Column("ClientId", Integer)
    reply_id = Column("ReplyId", Integer)
    reply_username = Column("ReplyUserName", String)
    del_flag = Column("DeleteFlag", Integer)
    comment_id_64 = Column("CommentId64", Integer)
    reply_id_64 = Column("ReplyId64", Integer)
    is_ad = Column("IsAd", Integer)
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", Integer)
    r3 = Column("Reserved3", String)
    r4 = Column("Reserved4", String)
    r5 = Column("Reserved5", Integer)
    r6 = Column("Reserved6", String)
    ref_action_buf = Column("RefActionBuf", LargeBinary)
    r7 = Column("Reserved7", LargeBinary)

    @staticmethod
    def mock(seed):
        random.seed(seed)
        return Comment(
            feed_id=-mock_timestamp() * 10,
            comment_id=-mock_timestamp() * 10 + 1,
            create_time=mock_timestamp(),
            flag=0,
            comment_type=1,
            comment_flag=0,
            content="mock comment" + str(seed),
            from_username=mock_user(seed + 1),
            reply_id=0,
            reply_username=0,
            del_flag=0,
            comment_id_64=0,
            reply_id_64=0,
            is_ad=0,
        )


@dataclass
class SnsConfig(UserTable):
    __tablename__ = "SnsConfigV20"

    key = Column("Key", String, primary_key=True)
    i_val = Column("IValue", Integer)
    str_val = Column("StrValue", String)
    buf_val = Column("BufValue", LargeBinary)
    r1 = Column("Reserved1", Integer)
    r2 = Column("Reserved2", String)
    r3 = Column("Reserved3", LargeBinary)

    @staticmethod
    def mock(seed):
        return SnsConfig(key=str(seed), i_val="Ivalue" + str(seed))


@singleton
class SnsCache(AbsUserDB):
    def __init__(self, user_cache_db_url, logger=None):
        super().__init__(user_cache_db_url, logger=logger)
        self.register_tables(
            [
                Feed,
                Comment,
                SnsConfig,
            ]
        )


@singleton
class Sns(AbsUserDB):
    def __init__(self, user_db_url, logger=None):
        super().__init__(user_db_url, logger=logger)
        self.register_tables(
            [
                Feed,
                Comment,
                SnsConfig,
            ]
        )

    def get_feeds_by_dur_and_wxids(
        self, begin: int, end: int, wx_ids: list[str] = None
    ) -> list[Feed]:
        query = self.session.query(Feed).filter(
            and_(
                Feed.create_time >= begin,
                Feed.create_time <= end,
            )
        )
        if wx_ids:
            query = query.filter(Feed.username.in_(wx_ids))
        res = query.order_by(Feed.create_time.desc()).all()
        return res

    def get_feed_by_feed_id(self, feed_id: int) -> Feed:
        res = self.session.query(Feed).filter(Feed.feed_id == feed_id).first()
        if res is None:
            self.logger.warning(f"[ SNS ] feed_id({feed_id}) NOT FIND")
            return Feed()
        return res

    def get_comment_by_feed_id(self, feed_id: int) -> Optional[Comment]:
        res = (
            self.session.query(Comment)
            .filter(Comment.feed_id == feed_id)
            .order_by(Comment.create_time.desc())
            .all()
        )
        return res

    def get_cover_url(self) -> str:
        res = self.session.query(SnsConfig).filter(SnsConfig.key == "6").one_or_none()
        return res.str_val
