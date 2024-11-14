import logging
from pathlib import Path
from threading import Thread
from typing import List

from wemo.database.micro_msg import Contact
from wemo.model.dto import MomentMsg
from wemo.model.user import User
from wemo.utils.utils import find_img_thumb_by_url, find_video_by_md5_or_duration


class ElementRender:
    def __init__(self, user: User):
        self.user = user
        self.user_data_dir = user.data_dir

    def render_imgs(self, img_paths: List[Path]):
        if img_paths is None or len(img_paths) == 0:
            return ""
        res = []
        for item in img_paths:
            # t = item.relative_to(self.user_data_dir).as_posix()
            res.append(f"![image]({item[0]})")
        return "\n".join(res)

    def render_videos(self, video_path: list[Path]):
        if video_path is None:
            return ""
        res = []
        for item in video_path:
            res.append(f'<video src="{item}" controls="controls">')
        return "\n".join(res)

    def render_avatar(self, avatar_path: Path):
        if avatar_path is None:
            return ""
        return f"![avatar]({avatar_path})"


class MarkdownExporter(Thread):
    def __init__(self, user: User):
        self.user = user
        self.user_dir = user.data_dir
        self.logger: logging.Logger = user.logger
        self.output_dir: Path = user.config.get("OUTPUT_DIR")
        self.render = ElementRender(user)
        super().__init__()

    def export_moment(self, user: Contact, moment: MomentMsg) -> str:
        username = moment.user_name
        create_time = moment.time
        desc = moment.desc
        self.logger.debug(
            f"[ EXPORTER ] {create_time} {user.Remark} push moment({moment.desc_brief})"
        )

        img_paths = self.find_imgs(moment)
        img_md_content = self.render.render_imgs(img_paths)

        v_path = self.find_videos(moment)
        v_md_content = self.render.render_videos(v_path)

        a_path = self.find_avater(moment)
        a_md_content = self.render.render_avatar(a_path)

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
        user_name_repr = user.Remark if user.Remark else user.NickName
        with open(
            self.output_dir.joinpath(f"{moment.datetime_cn}-{user_name_repr}.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(md_content)

    def find_imgs(self, moment: MomentMsg):
        res = []
        data_img_path = self.user.data_dir.img_dir
        for img in moment.imgs:
            # 检查是否存在
            dir_name = img.url.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_path, thm_path = find_img_thumb_by_url(year_month_dir, dir_name)
            if img_path:
                res.append((img_path, thm_path))
        return res

    def find_videos(self, moment: MomentMsg):
        res = []
        data_video_path = self.user.data_dir.video_dir.joinpath(moment.year_month)
        for video in moment.videos:
            video_path = find_video_by_md5_or_duration(
                data_video_path, video.url.md5, video.videoDuration
            )
            if video_path:
                res.append(video_path)
        return res

    def find_avater(self, moment: MomentMsg):
        dst_dir = self.user.data_dir.avatar_dir
        file_name = moment.user_name + ".png"
        dst_path = dst_dir.joinpath(file_name)
        if dst_path.exists():
            return dst_path
        self.logger.warning("Avatar not found.")
        return self.user.data_dir.avatar_dir.joinpath("default_avatar.jpg")
