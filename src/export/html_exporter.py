import datetime
import shutil
import threading
import time
from typing import Tuple

import xmltodict

from common.user_constant import RC
from db.micro_msg import MicroMsg
from db.sns import Sns
from model.comment import Comment
from model.contact import Contact
from .avatar_exporter import AvatarExporter
from .emoji_exporter import EmojiExporter
from .image_exporter import ImageExporter
from .video_exporter import VideoExporter
from model.moment_msg import MomentMsg, parse_xml
from pathlib import Path
from common import LOG


def get_img_div_css(size: int) -> str:
    if size == 1:
        return "width:10rem; overflow:hidden"
    else:
        return "width:19rem; overflow:hidden"


def get_img_css(size: int) -> str:
    """object-fit: cover; 预览图居中裁剪
    cursor:pointer; 手形鼠标
    """
    img_style = "object-fit:cover;cursor:pointer;"
    if size == 1:
        return f"width:10rem;height:10rem;{img_style}"
    elif size == 2:
        return f"width:8rem;height:8rem;float:left;margin-bottom:0.2rem;margin-right:0.2rem;{img_style}"
    elif size == 4:
        return f"width:8rem;height:8rem;float:left;margin-bottom:0.2rem;margin-right:0.2rem;{img_style}"
    else:
        return f"width:5rem;height:5rem;float:left;margin-bottom:0.2rem;margin-right:0.2rem;{img_style}"


def is_music_msg(msg: MomentMsg) -> bool:
    """判断一个msg是否为音乐分享"""
    o = msg.timelineObject.ContentObject
    if o and o.mediaList and o.mediaList.media:
        media = msg.timelineObject.ContentObject.mediaList.media[0]
        if media.type == "5":
            return True
    return False


def get_music_info(msg: MomentMsg) -> Tuple[str, str, str]:
    """获取音乐标题，演唱者，音乐源"""
    title = ""
    musician = ""
    src = ""
    o = msg.timelineObject.ContentObject
    if o and o.mediaList and o.mediaList.media:
        media = msg.timelineObject.ContentObject.mediaList.media[0]
        title = media.title
        musician = media.description
        if media.url:
            src = media.url.text
    return title, musician, src


class HtmlExporter(threading.Thread):

    def __init__(
        self,
        dir_name: str,
        contacts_map: dict[str, Contact],
        begin_date: datetime.date,
        end_date: datetime.date,
    ):
        self.dir_name = dir_name
        if Path(f"output/{self.dir_name}").exists():
            shutil.rmtree(f"output/{self.dir_name}")
        shutil.copytree("resource/template/", f"output/{self.dir_name}")

        self.avatar_exporter = AvatarExporter(dir_name)
        self.image_exporter = ImageExporter(dir_name)
        self.video_exporter = VideoExporter(dir_name)
        self.html_head = None
        self.html_end = None
        self.file = None
        self.contacts_map = contacts_map
        self.begin_date = begin_date
        self.end_date = end_date
        self.db_micro_msg = MicroMsg()
        self.db_sns = Sns()
        self.wxid = RC.WX_ID
        super().__init__()

    def run(self) -> None:

        with open("resource/template.html", encoding="utf-8") as f:
            content = f.read()
            self.html_head, self.html_end = content.split("/*内容分割线*/")
        self.file = open(f"output/{self.dir_name}/index.html", "w", encoding="utf-8")

        if self.gui.account_info and self.gui.account_info.get("wxid"):
            self.avatar_exporter.get_avatar_by_username(self.wxid)
            self.html_head = self.html_head.replace("{my_wxid}", f"{self.wxid}")

            my_info = self.db_micro_msg.get_contact_by_username(self.wxid)
            self.html_head = self.html_head.replace("{my_name}", f"{my_info[4]}")

        cover_url = self.db_sns.get_cover_url()
        if cover_url:
            cover_path = self.image_exporter.save_image((cover_url, "", ""), "image")
            self.html_head = self.html_head.replace("{cover_path}", cover_path)

        self.file.write(self.html_head)
        # 加一天
        end_date = self.end_date + datetime.timedelta(days=1)
        begin_time = time.mktime(
            datetime.datetime(
                self.begin_date.year, self.begin_date.month, self.begin_date.day
            ).timetuple()
        )
        end_time = time.mktime(
            datetime.datetime(end_date.year, end_date.month, end_date.day).timetuple()
        )

        message_datas = self.db_sns.get_feeds_by_duration(begin_time, end_time)
        for index, message_data in enumerate(message_datas):
            if message_data[0] in self.contacts_map:
                comments_datas = self.db_sns.get_comment_by_feed_id(message_data[2])
                comments: list[Comment] = []
                for c in comments_datas:
                    contact = Comment(c[0], c[1], c[2])
                    comments.append(contact)
                self.export_msg(message_data[1], comments, self.contacts_map)
                # 更新进度条 前30%视频处理  后70%其他处理
        self.finish_file()

    def export_msg(
        self, message: str, comments: list[Comment], contacts_map: dict[str, Contact]
    ) -> None:

        LOG.info(message)
        # force_list: 强制要求转media为list
        msg = parse_xml(message)

        # 微信ID
        username = msg.timelineObject.username
        # 头像路径
        avatar_path = self.avatar_exporter.get_avatar_by_username(username)

        contact = contacts_map.get(username)
        # 备注， 或用户名
        remark = contact.remark if contact.remark else contact.nickName

        # 朋友圈图片
        images = self.image_exporter.handle_image_from_moment(msg)

        # 朋友圈视频
        videos = self.video_exporter.handle_videos_from_moment(msg)

        # 样式   3:链接样式
        content_style = msg.timelineObject.ContentObject.contentStyle

        html = ' <div class="row item">\n'
        html += '    <div class="col-xs-2">\n'
        html += '         <div class="logo01_box">\n'
        html += f'             <img src="{avatar_path}" />\n'
        html += "         </div>\n"
        html += "    </div>\n"
        html += '    <div class="col-xs-10 xs8">\n'
        html += '          <div class="towp">\n'
        html += f'              <p class="p1">{remark}</p>\n'
        if msg.timelineObject.contentDesc:
            content_desc = msg.timelineObject.contentDesc.replace("\n", "<br>")
            content_desc = EmojiExporter.replace_emoji(content_desc)
            html += f'              <p class="p2">{content_desc}</p>\n'
        html += "          </div>\n"

        # 超链接
        if content_style == 3:
            html += f'  <a href="{msg.timelineObject.ContentObject.contentUrl}" target="_blank">\n'
            html += '      <div class ="out_link" >\n'
            if images:
                thumb_path, image_path = images[0]
                html += f'        <img src = "{thumb_path}"/>\n'
            html += f'       <div class ="text" >{msg.timelineObject.ContentObject.title}</div>\n'
            html += "      </div >\n"
            html += "   </a>\n"
        # 音乐
        elif is_music_msg(msg):

            title, musician, src = get_music_info(msg)
            html += f'  <a href="{msg.timelineObject.ContentObject.contentUrl}" target="_blank">\n'
            html += '      <div class ="music_link" >\n'
            html += '        <div class ="music_des" >\n'
            if images:
                thumb_path, image_path = images[0]
                html += f'        <img src = "{thumb_path}"/>\n'
            html += '             <div class = "music_title_musician">\n'
            html += f'               <div class = "music_title">{title}</div>\n'
            html += f'               <div class = "music_musician">{musician}</div>\n'
            html += "             </div>\n"
            html += "         </div>\n"
            html += '        <audio class = "music_audio" controls>'
            html += f'             <source src="{src}" type="audio/mpeg">'
            html += "        </audio>"
            html += "      </div >\n"
            html += "   </a>\n"
        # 视频号
        elif msg.timelineObject.ContentObject.finderFeed:
            html += '     <div style="width:10rem; overflow:hidden">\n'
            # 视频号图片
            thumb_path = self.image_exporter.get_finder_images(msg)
            html += f"""       <img src=\"{thumb_path}\" onclick=\"openWarningOverlay(event)\" 
                               style=\"width:10rem;height:10rem;object-fit:cover;cursor:pointer;\"/>\n"""
            html += "      </div>\n"

            # 视频号说明
            html += '          <div class="texts_box">\n'
            nickname = msg.timelineObject.ContentObject.finderFeed.nickname
            desc = msg.timelineObject.ContentObject.finderFeed.desc
            html += (
                f'            <p class="location">视频号 · {nickname} · {desc}</p>\n'
            )
            html += "         </div>\n"
        # 普通朋友圈
        else:
            html += f'     <div style="{get_img_div_css(len(images))}">\n'
            for thumb_path, image_path in images:
                html += f"""     <img src="{thumb_path}" full_img="{image_path}" onclick="openFullSize(event)" 
                                 style="{get_img_css(len(images))}"/>\n"""
            html += "      </div>\n"

            html += "      <div>\n"
            for video_path in videos:
                html += '     <video controls height="500">\n'
                html += f'        <source  src="{video_path}" type="video/mp4">\n'
                html += "     <video>\n"
            html += "      </div>\n"

        html += '          <div class="texts_box">\n'
        if msg.timelineObject.location and msg.timelineObject.location.poiName:
            html += f'        <p class="location">{msg.timelineObject.location.poiName}</p>\n'
        html += f'            <p class="time">{msg.timelineObject.create_time}</p>\n'
        html += "         </div>\n"
        html += "    </div>\n"
        html += "</div>\n"
        self.file.write(html)

    def finish_file(self):
        self.file.write(self.html_end)
        self.file.close()