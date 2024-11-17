from pathlib import Path
import re

from jinja2 import Template

from wemo.model.moment import Media, MomentMsg
from wemo.model.ctx import Context
from wemo.utils.utils import find_img_thumb_by_url, find_video_by_md5_or_duration


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


md_template = Template(
    """# 朋友圈记录
头像: {{ avatar_url }}
用户名: {{ username }}
昵称: {{ nickname }}
备注: {{ remark }}
内容: 
{{ desc }}
图片: 
{{ img_urls }}
视频:
{{ video_urls }}
"""
)


class HtmlRender:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_data_dir = ctx.user_data_dir

    def render_avatar(self, avatar_path: Path):
        if avatar_path is None:
            return ""
        return f'<img src="{avatar_path}" />'

    def render_remark(self, remark: str):
        return f'<p class="p1">{remark}</p>'

    def render_imgs(self, images):
        img_content = ""
        for thumb_path, image_path in images:
            img_content += f"""
            <img 
            src="{thumb_path}" 
            full_img="{image_path}" 
            onclick="openFullSize(event)" 
            style="{get_img_css(len(images))}"/>
        """
        return img_content

    def render_video(self, videos):
        video_content = ""
        for video_path in videos:
            video_content += f"""
            <video controls height="500">
            <source src="{video_path}" type="video/mp4">
            </video>
        """
        return video_content

    def render_desc(self, desc):
        return f'<p class="p2">{desc}</p>'

    def render_content(self, images, videos, desc):
        html = ""
        img_html = self.render_imgs(images)
        video_html = self.render_video(videos)
        desc_html = self.render_desc(desc)

        html += f"""<div 
                style="width:{10 if len(images) == 1 else 19}rem; overflow:hidden">
                {desc_html}
                {img_html}
                {video_html}
            </div>"""
        return html

    def render_row(self, avatar_html: str, remark_html: str, content_desc_html: str):

        return f"""
        <div class="col-xs-2">
            <div class="logo01_box">{avatar_html}</div>
        </div>
    <div class="col-xs-10 xs8">
        <div class="towp">
        {remark_html}
        {content_desc_html}
    </div>
    """


class MdRender:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_data_dir = ctx.user_data_dir

    def render_avatar(self, avatar_path: Path):
        if avatar_path is None:
            return ""
        return f"![avatar]({avatar_path})"

    def render_imgs(self, img_paths: list[Path]):
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


class Finder:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_dir = ctx.user_data_dir
        self.logger = ctx.logger

    def get_img_urls(self, moment: MomentMsg):
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for img in moment.imgs:
            # 检查是否存在
            dir_name = img.url.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_path, thm_path = find_img_thumb_by_url(year_month_dir, dir_name)
            if img_path:
                res.append((img_path, thm_path))
        return res

    def get_video_urls(self, moment: MomentMsg):
        res = []
        data_video_path = self.ctx.user_data_dir.video_dir.joinpath(moment.year_month)
        for video in moment.videos:
            video_path = find_video_by_md5_or_duration(
                data_video_path, video.url.md5, video.videoDuration
            )
            if video_path:
                res.append(video_path)
        return res

    def get_avatar_url(self, moment: MomentMsg):
        dst_dir = self.ctx.user_data_dir.avatar_dir
        file_name = moment.username + ".png"
        dst_path = dst_dir.joinpath(file_name)
        if dst_path.exists():
            return dst_path
        self.logger.warning("Avatar not found.")
        return self.ctx.user_data_dir.avatar_dir.joinpath("default_avatar.jpg")
