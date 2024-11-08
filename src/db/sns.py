from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, String, Integer, LargeBinary
from sqlalchemy import and_

from utils import singleton

from .abstract_db import AbstractUserDB, Base

# 朋友圈
SNS = "Sns"


class FeedsV20(Base):
    __tablename__ = "FeedsV20"
    FeedId = Column("FeedId", Integer, primary_key=True)
    CreateTime = Column("CreateTime", Integer)
    FaultId = Column("FaultId", Integer)
    Type = Column("Type", Integer)
    UserName = Column("UserName", String)
    Status = Column("Status", Integer)
    ExtFlag = Column("ExtFlag", Integer)
    PrivFlag = Column("PrivFlag", Integer)
    StringId = Column("StringId", String)
    Content = Column("Content", String)
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", Integer)
    Reserved3 = Column("Reserved3", String)
    Reserved4 = Column("Reserved4", String)
    Reserved5 = Column("Reserved5", Integer)
    Reserved6 = Column("Reserved6", String)
    ExtraBuf = Column("ExtraBuf", LargeBinary)
    Reserved7 = Column("Reserved7", LargeBinary)

    def __hash__(self):
        return self.FeedId

    def __eq__(self, o: FeedsV20):
        return (
            self.CreateTime == o.CreateTime
            and self.FaultId == o.FaultId
            and self.UserName == o.UserName
            and self.Content == o.Content
            and self.CreateTime == o.CreateTime
        )


class CommentV20(Base):
    __tablename__ = "CommentV20"

    FeedId = Column("FeedId", Integer, primary_key=True)
    CommentId = Column("CommentId", Integer, primary_key=True)
    Createtime = Column("Createtime", Integer)
    Flag = Column("Flag", Integer)
    CommentType = Column("CommentType", Integer, primary_key=True)
    CommentFlag = Column("CommentFlag", Integer)
    Content = Column("Content", String)
    FromUserName = Column("FromUserName", String, primary_key=True)
    ClientId = Column("ClientId", Integer)
    ReplyId = Column("ReplyId", Integer)
    ReplyUserName = Column("ReplyUserName", String)
    DeleteFlag = Column("DeleteFlag", Integer)
    CommentId64 = Column("CommentId64", Integer)
    ReplyId64 = Column("ReplyId64", Integer)
    IsAd = Column("IsAd", Integer)
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", Integer)
    Reserved3 = Column("Reserved3", String)
    Reserved4 = Column("Reserved4", String)
    Reserved5 = Column("Reserved5", Integer)
    Reserved6 = Column("Reserved6", String)
    RefActionBuf = Column("RefActionBuf", LargeBinary)
    Reserved7 = Column("Reserved7", LargeBinary)

    def __hash__(self):
        return (
            str(self.CommentId)
            + str(self.FeedId)
            + str(self.FromUserName)
            + str(self.CommentType)
        )

    def __eq__(self, o: CommentV20):
        return (
            self.CommentId == o.CommentId
            and self.FeedId == o.FeedId
            and self.Content == o.Content
            and self.CommentType == o.CommentType
            and self.FromUserName == o.FromUserName
        )


class SnsConfigV20(Base):
    __tablename__ = "SnsConfigV20"

    Key = Column("Key", String, primary_key=True)
    IValue = Column("IValue", Integer)
    StrValue = Column("StrValue", String)
    BufValue = Column("BufValue", LargeBinary)
    Reserved1 = Column("Reserved1", Integer)
    Reserved2 = Column("Reserved2", String)
    Reserved3 = Column("Reserved3", LargeBinary)

    def __hash__(self):
        return self.Key

    def __eq__(self, o: SnsConfigV20):
        return (
            self.Key == o.Key
            and self.StrValue == o.StrValue
            and self.IValue == o.IValue
        )


@singleton
class SnsCache(AbstractUserDB):
    def __init__(self, user_cache_db_dir, logger):
        super().__init__(user_cache_db_dir, SNS, logger)
        self.register_tables(
            [
                FeedsV20,
                CommentV20,
                SnsConfigV20,
            ]
        )
        self.connect_db()


@singleton
class Sns(AbstractUserDB):
    def __init__(self, user_cache_db_dir, logger):
        super().__init__(user_cache_db_dir, SNS, logger)
        self.register_tables(
            [
                FeedsV20,
                CommentV20,
                SnsConfigV20,
            ]
        )
        self.connect_db()

    def get_feeds_by_duration(
        self, begin_timestamp: int, end_timestamp: int
    ) -> Optional[list[FeedsV20]]:
        res = (
            self.session.query(FeedsV20)
            .filter(
                and_(
                    FeedsV20.CreateTime >= begin_timestamp,
                    FeedsV20.CreateTime <= end_timestamp,
                )
            )
            .order_by(FeedsV20.CreateTime.desc())
            .all()
        )
        return res

    def get_feed_by_feed_id(self, feed_id: int) -> FeedsV20:
        res = self.session.query(FeedsV20).filter(FeedsV20.FeedId == feed_id).first()
        if res is None:
            self.logger.error(f"feed_id:{feed_id} 未找到")
            return FeedsV20()
        return res

    def get_comment_by_feed_id(self, feed_id: int) -> Optional[CommentV20]:
        res = (
            self.session.query(CommentV20)
            .filter(CommentV20.FeedId == feed_id)
            .order_by(CommentV20.Createtime.desc())
            .all()
        )
        return res

    def get_cover_url(self) -> Optional[SnsConfigV20]:
        res = (
            self.session.query(SnsConfigV20)
            .filter(SnsConfigV20.Key == "6")
            .one_or_none()
        )
        return res
