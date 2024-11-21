from functools import cached_property

from jinja2 import Template

from wemo.backend.database.micro_msg import Contact
from wemo.backend.model.moment import MomentMsg
from wemo.backend.ctx import Context
from wemo.backend.utils.utils import (
    find_img_thumb_by_url,
    find_video_by_md5_or_duration,
)


class RenderTemplate:
    def __init__(self, ctx: Context):
        self.render_dir = ctx.static_dir.joinpath("template")
        self.logger = ctx.logger
        pass

    def get_template(self, name: str):
        full_name = name + ".html"
        with open(self.render_dir.joinpath(full_name), "r", encoding="utf-8") as f:
            temp = f.read()
        return Template(temp)

    @cached_property
    def temp_banner(self) -> Template:
        return self.get_template("banner")

    @cached_property
    def temp_moment_msg(self) -> Template:
        return self.get_template("moment")

    @cached_property
    def temp_sns(self) -> Template:
        return self.get_template("sns")


class HtmlRender:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_data_dir = ctx.user_data_dir
        self.finder = ResourceManager(ctx)
        self.template = RenderTemplate(ctx)
        self.logger = self.ctx.logger

    def render(self, contact: Contact, moment: MomentMsg):
        self.logger.debug(
            f"[ RENDER SERVICE ] {moment.time} {contact.remark} push moment({moment.desc_brief})"
        )
        self.logger.info(f"[ RENDER SERVICE ] contentStyle({moment.style})")
        for item in moment.medias:
            self.logger.info(f"[ RENDER SERVICE ] media({item.type})")
        desc = moment.desc.replace("\n", "<br>") if moment.desc is not None else ""
        images = self.finder.get_imgs(moment)
        videos = self.finder.get_videos(moment)
        avatar_url = self.finder.get_avatar_url(moment)
        links = self.finder.get_links(moment)
        musics = self.finder.get_musics(moment)
        finders = self.finder.get_finders(moment)
        location = moment.location
        create_time = moment.time

        name = contact.repr_name

        return self.template.temp_moment_msg.render(
            avatar_url=avatar_url,
            desc=desc,
            name=name,
            images=images,
            videos=videos,
            links=links,
            musics=musics,
            finders=finders,
            location=location,
            create_time=create_time,
        )

    def render_banner(self, cover_url, contact: Contact):
        avatar_url = self.finder.get_avatar_url(contact)
        name = contact.nick_name
        res = self.template.temp_banner.render(
            cover_url=cover_url, avatar_url=avatar_url, name=name
        )
        return res


class ResourceManager:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_dir = ctx.user_data_dir
        self.logger = ctx.logger

    def get_imgs(self, moment: MomentMsg):
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for img in moment.imgs:
            # 检查是否存在
            urn_dir = img.url.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_path, thm_path = find_img_thumb_by_url(year_month_dir, urn_dir)
            if img_path is None and thm_path is None:
                continue
            img.url = img_path
            img.thumb = thm_path
            res.append(img)
        return res

    def get_videos(self, moment: MomentMsg):
        res = []
        data_video_path = self.ctx.user_data_dir.video_dir.joinpath(moment.year_month)
        for video in moment.videos:
            video_path = find_video_by_md5_or_duration(
                data_video_path, video.url.md5, video.videoDuration
            )
            video.url = video_path
            res.append(video)
        return res

    def get_avatar_url(self, moment: MomentMsg):
        dst_dir = self.ctx.user_data_dir.avatar_dir
        file_name = moment.username + ".png"
        dst_path = dst_dir.joinpath(file_name)
        if dst_path.exists():
            return dst_path
        self.logger.warning("Avatar not found.")
        return self.ctx.user_data_dir.avatar_dir.joinpath("default_avatar.jpg")

    def get_links(self, moment: MomentMsg):
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for link in moment.links:
            urn_dir = link.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            link.thumb = img_url
            link.url = link.url.text
            res.append(link)
        return res

    def get_musics(self, moment: MomentMsg):
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for music in moment.musics:
            urn_dir = music.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            music.thumb = img_url
            music.url = music.url.url
            res.append(music)
        return res

    def get_finders(self, moment: MomentMsg):
        res = []
        data_img_path = self.ctx.user_data_dir.img_dir
        for finder in moment.finders:
            urn_dir = finder.thumb.urn
            year_month_dir = data_img_path.joinpath(moment.year_month)
            img_url, _ = find_img_thumb_by_url(year_month_dir, urn_dir)
            finder.thumb = img_url
            finder.title = finder.title or ""
            finder.description = finder.description or ""
            res.append(finder)
        return res
