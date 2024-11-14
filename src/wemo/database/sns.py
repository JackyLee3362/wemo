from __future__ import annotations

import random
from typing import Optional

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_

from wemo.database.db import AbsUserDB
from wemo.database.db import UserTable
from wemo.utils.utils import mock_sns_content, mock_timestamp, mock_user, singleton


# 朋友圈


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
            FeedId=-mock_timestamp() * 10,
            CreateTime=mock_timestamp(),
            FaultId=0,
            Type=1,
            UserName=mock_user(seed),
            Status=0,
            ExtFlag=1,
            PrivFlag=0,
            StringId=str(mock_timestamp() * 100),
            Content=mock_sns_content(),
        )


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
            FeedId=-mock_timestamp() * 10,
            CommentId=-mock_timestamp() * 10 + 1,
            Createtime=mock_timestamp(),
            Flag=0,
            CommentType=1,
            CommentFlag=0,
            Content="mock comment" + str(seed),
            FromUserName=mock_user(seed + 1),
            ReplyId=0,
            ReplyUserName=0,
            DeleteFlag=0,
            CommentId64=0,
            ReplyId64=0,
            IsAd=0,
        )


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
        return SnsConfig(Key=str(seed), IValue="Ivalue" + str(seed))


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

    def get_cover_url(self) -> Optional[SnsConfig]:
        res = self.session.query(SnsConfig).filter(SnsConfig.key == "6").one_or_none()
        return res
