from functools import cached_property

from jinja2 import Template

from wemo.backend.database.micro_msg import Contact
from wemo.backend.model.moment import MomentMsg
from wemo.backend.ctx import Context
from wemo.backend.res.res_manager import ResourceManager


class RenderTemplate:
    def __init__(self, ctx: Context):
        self.temp_dir = ctx.template_dir
        self.logger = ctx.logger

    def get_template(self, name: str):
        full_name = name + ".html"
        with open(self.temp_dir.joinpath(full_name), "r", encoding="utf-8") as f:
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
    def __init__(self, ctx: Context, res_manager: ResourceManager):
        self.ctx = ctx
        self.user_data_dir = ctx.user_data_dir
        self.res_manager = res_manager
        self.template = RenderTemplate(ctx)
        self.logger = self.ctx.logger

    def render(self, contact: Contact, moment: MomentMsg):
        self.logger.debug(
            f"[ RENDER SERVICE ] {moment.time} {contact.remark} push moment({moment.desc_brief})"
        )
        # self.logger.info(f"[ RENDER SERVICE ] contentStyle({moment.style})")
        # for item in moment.medias:
        #     self.logger.info(f"[ RENDER SERVICE ] media({item.type})")
        desc = moment.desc.replace("\n", "<br>") if moment.desc is not None else ""
        images = self.res_manager.get_imgs(moment)
        videos = self.res_manager.get_videos(moment)
        avatar_url = self.res_manager.get_avatar_url(moment)
        links = self.res_manager.get_links(moment)
        musics = self.res_manager.get_musics(moment)
        finders = self.res_manager.get_finders(moment)
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
        avatar_url = self.res_manager.get_avatar_url(contact)
        name = contact.nick_name
        res = self.template.temp_banner.render(
            cover_url=cover_url, avatar_url=avatar_url, name=name
        )
        return res
