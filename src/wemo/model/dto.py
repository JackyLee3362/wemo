from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple, Optional

import xmltodict
from dataclasses_json import dataclass_json, config

from wemo.utils.utils import timestamp_convert


@dataclass_json
@dataclass
class Location:
    poiName: str = field(metadata=config(field_name="@poiName"), default="")
    longitude: str = field(metadata=config(field_name="@longitude"), default="")
    latitude: str = field(metadata=config(field_name="@latitude"), default="")
    country: str = field(metadata=config(field_name="@country"), default="")


@dataclass_json
@dataclass
class Url:
    type: str = field(metadata=config(field_name="@type"))
    text: str = field(metadata=config(field_name="#text"), default="")
    md5: str = field(metadata=config(field_name="@md5"), default="")
    token: str = field(metadata=config(field_name="@token"), default="")
    enc_idx: str = field(metadata=config(field_name="@enc_idx"), default="")

    @property
    def url(self):
        return self.text

    @property
    def urn(self):
        return self.text.split("/")[-2]

    @property
    def params(self):
        res = {}
        if self.token not in ("", None):
            res["token"] = self.token
        if self.enc_idx not in ("", None):
            res["enc_idx"] = self.enc_idx
        return res


@dataclass_json
@dataclass
class Thumb:
    # type=2 表示普通图片，5表示微信音乐
    type: str = field(metadata=config(field_name="@type"))
    text: str = field(metadata=config(field_name="#text"))
    token: str = field(metadata=config(field_name="@token"), default="")
    enc_idx: str = field(metadata=config(field_name="@enc_idx"), default="")

    @property
    def url(self):
        return self.text

    @property
    def urn(self):
        return self.text.split("/")[-2]

    @property
    def params(self):
        res = {}
        if self.token not in ("", None):
            res["token"] = self.token
        if self.enc_idx not in ("", None):
            res["enc_idx"] = self.enc_idx
        return res


@dataclass_json
@dataclass
class Media:
    id: Optional[str] = None
    type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[Url] | str = None
    thumb: Optional[Thumb] = None
    thumbUrl: Optional[str] = None
    videoDuration: Optional[str] = None

    @property
    def thumbUrn(self):
        return self.thumbUrl.split("/")[-2]


@dataclass_json
@dataclass
class MediaList:
    media: list[Media]


@dataclass_json
@dataclass
class FinderFeed:
    feedType: Optional[str] = ""
    nickname: Optional[str] = ""
    desc: Optional[str] = ""
    mediaList: Optional[MediaList] = None


@dataclass_json
@dataclass
class ContentObject:
    # contentStyle = 3 表示超链接
    contentStyle: int
    contentUrl: Optional[str] = ""
    title: Optional[str] = ""
    description: Optional[str] = ""
    mediaList: Optional[MediaList] = None
    # 视频号消息
    finderFeed: Optional[FinderFeed] = None


@dataclass_json
@dataclass
class TimelineObject:
    id: int
    username: str
    location: Location
    ContentObject: ContentObject
    createTime: int
    contentDesc: Optional[str] = ""


@dataclass_json
@dataclass
class MomentMsg:
    timelineObject: TimelineObject = field(metadata=config(field_name="TimelineObject"))

    def from_dict(self, *args, **kwargs) -> MomentMsg: ...

    @property
    def imgs(self) -> list[Media]:
        res = []
        medias: MediaList = self.medias
        for media in medias:
            if media.type == "2":
                res.append(media)
            elif media.type == 5 or self.style == 3:
                media.url = media.thumb
                res.append(media)
        return res

    @property
    def videos(self) -> list[Media]:
        res = []
        for media in self.medias:
            if media.type == "6":
                res.append(media)
        return res

    @property
    def medias(self) -> list[Media]:
        return self.timelineObject.ContentObject.mediaList.media

    @property
    def finder(self) -> list[Media]:
        finder_feed = self.timelineObject.ContentObject.finderFeed
        if not finder_feed or not finder_feed.mediaList:
            return []
        return finder_feed.mediaList

    @property
    def date(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime("%Y-%m-%d")

    @property
    def time(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @property
    def datetime_cn(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime(
            "%Y年%m月%d日%H时%M分%S秒"
        )

    @property
    def year_month(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime("%Y-%m")

    @property
    def user_name(self) -> str:
        return self.timelineObject.username

    @property
    def desc(self) -> str:
        return self.timelineObject.contentDesc

    @property
    def desc_brief(self) -> str:
        COUNT = 20
        desc = self.desc or ""
        desc = desc.replace("\n", " ")
        return (desc[: COUNT - 3] + "...") if len(desc) > COUNT else desc.ljust(COUNT)

    @property
    def style(self):
        return self.timelineObject.ContentObject.contentStyle

    @classmethod
    def parse_xml(cls, xml: str) -> MomentMsg:
        try:
            msg_dict = cls.parse_xml_to_dict(xml)
        except Exception as e:
            print(e)
            return None
        return MomentMsg.from_dict(msg_dict)

    @staticmethod
    def parse_xml_to_dict(xml: str) -> dict:
        msg_dict = xmltodict.parse(xml, force_list={"media"})
        return msg_dict


@dataclass
class Contact:
    userName: str
    alias: str
    type: int
    remark: str
    nickName: str
    pYInitial: str
    remarkPYInitial: str
    smallHeadImgUrl: str
    bigHeadImgUrl: str
    exTraBuf: str
    labelName: str
    latestTalkTime: int


@dataclass
class Comment:
    from_user_name: str
    comment_type: int
    content: str
