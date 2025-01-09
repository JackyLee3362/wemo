from __future__ import annotations

from dataclasses import dataclass
import logging
import random
from typing import Optional

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_

from wemo.backend.database.db import AbsUserCache, AbsUserDB
from wemo.backend.database.db import UserTable
from wemo.backend.utils.mock import mock_timestamp, mock_user
from wemo.backend.utils.mock import mock_sns_content


# 朋友圈
logger = logging.getLogger(__name__)


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

    def __eq__(self, o: Feed):
        return self.feed_id == o.feed_id

    def __hash__(self):
        return self.feed_id

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

    def __eq__(self, o: Comment):
        return (
            self.feed_id == o.feed_id
            and self.comment_id == o.comment_id
            and self.comment_type == o.comment_type
            and self.from_username == o.from_username
        )

    def __hash__(self):
        return hash(
            (self.feed_id, self.comment_id, self.comment_type, self.from_username)
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

    def __eq__(self, o: SnsConfig):
        return self.key == o.key

    def __hash__(self):
        return self.key


class SnsCache(AbsUserCache):
    def __init__(self, user_cache_db_url):
        super().__init__(user_cache_db_url)
        self.register_tables(
            [
                Feed,
                Comment,
                SnsConfig,
            ]
        )


class Sns(AbsUserDB):

    def __str__(self):
        return "[ SNS ]"

    def __init__(self, user_db_url):
        super().__init__(user_db_url)
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
            logger.warning(f"{self} feed_id({feed_id}) NOT FIND")
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
