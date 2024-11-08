from pathlib import Path
from threading import Thread
from typing import List

from common.logger import LOG
from common.user_constant import RC
from db import MicroMsg, Sns
from model.moment_msg import parse_xml
from export.avatar_exporter import AvatarExporter
from export.image_exporter import ImageExporter
from export.video_exporter import VideoExporter


class FeedExporter(Thread):
    def __init__(self):
        self.user_dir = RC.USER_DIR
        self.output_dir = RC.USER_OUTPUT_DIR
        self.db_sns = Sns()
        self.db_micro_msg = MicroMsg()
        self.image_exporter = ImageExporter()
        self.video_exporter = VideoExporter()
        self.avatar_exporter = AvatarExporter()
        self.db_sns = Sns()
        self.db_micro_msg = MicroMsg()
        super().__init__()

    def parse_feed(self, feed_id: int) -> str:
        feed_obj = self.db_sns.get_feed_by_feed_id(feed_id)
        moment = parse_xml(feed_obj.Content)
        username = moment.user_name
        create_time = moment.create_time
        user, labels = self.db_micro_msg.get_contact_by_username(username)
        desc = moment.desc
        LOG.info(f"[日期:{create_time}][用户:{user.Remark}]: {moment.desc_brief}")

        img_path = self.image_exporter.handle_image_from_moment(moment)
        img_md_content = self.render_img(img_path)

        v_path = self.video_exporter.handle_videos_from_moment(moment)
        v_md_content = self.render_video(v_path)

        a_path = self.avatar_exporter.get_avatar_by_username(username)
        a_md_content = self.render_avatar(a_path)

        # 输出为 md 文件
        md_content = f"""# 朋友圈记录
用户名: {username}
头像: {a_md_content}
自取昵称: {user.NickName}
备注: {user.Remark}
内容: {desc}
图片: 
{img_md_content}
视频:
{v_md_content}
"""
        print(md_content)
        user_name_repr = user.Remark if user.Remark else user.NickName
        with open(
            self.output_dir.joinpath(f"{moment.file_name}-{user_name_repr}.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(md_content)

    def render_img(self, img_path: List[Path]):
        if img_path is None or len(img_path) == 0:
            return ""
        res = []
        for item in img_path:
            t = item.relative_to(self.user_dir).as_posix()
            res.append(f"![image](../{t})")
        return "\n".join(res)

    def render_video(self, video_path: Path):
        if video_path is None:
            return ""

        return f'<video src="../{video_path.relative_to(self.user_dir)}" controls="controls">'

    def render_avatar(self, avatar_path: Path):
        if avatar_path is None:
            return ""
        return f"![avatar](../{avatar_path.relative_to(self.user_dir).as_posix()})"
