from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from typing import Optional
from urllib.parse import urlparse

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
        return urlparse(self.text).path.split("/")[-2]

    @property
    def params(self):
        res = {}
        if self.token not in ("", None):
            res["token"] = self.token
        if self.enc_idx not in ("", None):
            res["idx"] = self.enc_idx
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
        return urlparse(self.text).path.split("/")[-2]

    @property
    def params(self):
        res = {}
        if self.token not in ("", None):
            res["token"] = self.token
        if self.enc_idx not in ("", None):
            res["idx"] = self.enc_idx
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
    link: Optional[str] = None

    @property
    def thumbUrn(self):
        return urlparse(self.thumbUrl).path.split("/")[-2]


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
    contentDesc: str = ""

    @staticmethod
    def mock():
        return TimelineObject(
            id=0,
            username="mock-from-time-object",
            location=None,
            ContentObject=None,
            createTime=1730123456,
            contentDesc="",
        )


@dataclass_json
@dataclass
class MomentMsg:
    timelineObject: TimelineObject = field(metadata=config(field_name="TimelineObject"))

    def from_dict(self, *args, **kwargs) -> MomentMsg: ...

    @cached_property
    def msg_repr(self) -> str:
        return f"contentStyle({self.style})"

    @cached_property
    def update_pic(self) -> dict[str, list[Media]]:
        res = {}
        if len(self.musics) > 0:
            res["music"] = self.musics
        if len(self.imgs) > 0:
            res["img"] = self.imgs
        if len(self.videos) > 0:
            res["video"] = self.videos
        if len(self.finders) > 0:
            res["finder"] = self.finders
        if len(self.links) > 0:
            res["link"] = self.links
        return res

    @cached_property
    def imgs(self) -> list[Media]:
        res = []
        # 普通图片
        if self.style == 1:
            for media in self.medias:
                res.append(media)
        return res

    @cached_property
    def musics(self) -> list[Media]:
        res = []
        # 微信音乐
        if self.style == 42:
            for media in self.medias:
                media.link = self.timelineObject.ContentObject.contentUrl
                media.title = self.timelineObject.ContentObject.title
                media.description = self.timelineObject.ContentObject.description
                res.append(media)
        return res

    @cached_property
    def links(self) -> list[Media]:
        res = []
        # 超链接
        if self.style in (3, 5):
            for media in self.medias:
                media.link = self.timelineObject.ContentObject.contentUrl
                media.title = self.timelineObject.ContentObject.title
                media.description = self.timelineObject.ContentObject.description
                res.append(media)
        return res

    @cached_property
    def videos(self) -> list[Media]:
        res = []
        if self.style == 15:
            for media in self.medias:
                res.append(media)
        return res

    @cached_property
    def medias(self) -> list[Media]:
        try:
            return self.timelineObject.ContentObject.mediaList.media
        except Exception:
            return []

    @cached_property
    def finders(self) -> list[Media]:
        res = []
        if self.style == 28:
            try:
                media = self.timelineObject.ContentObject.finderFeed.mediaList.media
                for item in media:
                    item.thumb = Thumb(
                        type="", text=item.thumbUrl, token="", enc_idx=""
                    )
                    res.append(item)
            except Exception as e:
                print(e)
        return res

    @property
    def location(self) -> str:
        return self.timelineObject.location.poiName

    @property
    def date(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime("%Y-%m-%d")

    @property
    def time(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    @property
    def year_month(self) -> str:
        return timestamp_convert(self.timelineObject.createTime).strftime("%Y-%m")

    @property
    def username(self) -> str:
        return self.timelineObject.username

    @property
    def desc(self) -> str:
        return self.timelineObject.contentDesc

    @property
    def desc_brief(self) -> str:
        COUNT = 32
        desc = self.desc or ""
        desc = desc.replace("\n", " ")
        return (desc[: COUNT - 3] + "...") if len(desc) > COUNT else desc

    @property
    def style(self) -> int:
        return self.timelineObject.ContentObject.contentStyle

    @classmethod
    def parse_xml(cls, xml: str) -> MomentMsg:
        try:
            msg_dict = xmltodict.parse(xml, force_list={"media"})
        except Exception as e:
            print("[ XML PARSE ERROR ]", e)
            return MomentMsg.mock()
        return MomentMsg.from_dict(msg_dict)  # type: ignore

    @staticmethod
    def mock():
        return MomentMsg(TimelineObject.mock())
