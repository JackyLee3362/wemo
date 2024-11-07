from dataclasses import dataclass, field
from typing import Optional
from dataclasses_json import dataclass_json, config

from utils.helper import timestamp_convert


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


@dataclass_json
@dataclass
class Thumb:
    # type=2 表示普通图片，5表示微信音乐
    type: str = field(metadata=config(field_name="@type"))
    text: str = field(metadata=config(field_name="#text"))
    token: str = field(metadata=config(field_name="@token"), default="")
    enc_idx: str = field(metadata=config(field_name="@enc_idx"), default="")


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

    @property
    def create_date(self) -> str:
        return timestamp_convert(self.createTime).strftime("%Y-%m-%d")

    @property
    def create_time(self) -> str:
        return timestamp_convert(self.createTime).strftime("%Y-%m-%d %H:%M:%S")

    @property
    def create_year_month(self) -> str:
        return timestamp_convert(self.createTime).strftime("%Y-%m")


@dataclass_json
@dataclass
class MomentMsg:
    timelineObject: TimelineObject = field(metadata=config(field_name="TimelineObject"))

    def from_dict(*args, **kwargs): ...
