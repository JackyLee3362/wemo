import logging
from pathlib import Path
from wemo.database.micro_msg import Contact
from wemo.export.render import Finder, HtmlRender, MdRender, md_template
from wemo.model.moment import MomentMsg
from wemo.model.ctx import Context
from wemo.database.db_service import DBService


class RenderService:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.user_dir = ctx.user_data_dir
        self.logger: logging.Logger = ctx.logger
        self.output_dir: Path = ctx.output_dir
        self.md_render = MdRender(ctx)
        self.html_render = HtmlRender(ctx)
        self.finder = Finder(ctx)

    def export_md(self, contact: Contact, moment: MomentMsg):
        username = moment.username
        create_time = moment.time
        content = moment.desc
        self.logger.debug(
            f"[ EXPORTER ] {create_time} {contact.remark} push moment({moment.desc_brief})"
        )
        img_urls = self.finder.get_img_urls(moment)
        v_urls = self.finder.get_video_urls(moment)
        a_urls = self.finder.get_avatar_url(moment)

        img_content = self.md_render.render_imgs(img_urls)
        v_content = self.md_render.render_videos(v_urls)
        a_content = self.md_render.render_avatar(a_urls)

        # 输出为 md 文件
        md_content = md_template.render(
            avatar_url=a_content,
            username=username,
            nickname=contact.nick_name,
            remark=contact.remark,
            desc=content,
            img_urls=img_content,
            video_urls=v_content,
        )

        username_repr = contact.remark if contact.remark else contact.nick_name
        with open(
            self.output_dir.joinpath(f"{moment.datetime_cn}-{username_repr}.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(md_content)

        avatar_html = self.html_render.render_avatar(a_urls)
        content_html = self.html_render.render_content(img_urls, v_urls, content)
        html_content = self.html_render.render_row(
            avatar_html, username_repr, content_html
        )

        with open(
            self.output_dir.joinpath(f"{moment.datetime_cn}-{username_repr}.html"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(html_content)


class ExportService:

    def __init__(self, ctx: Context, db: DBService, logger: logging.Logger = None):
        self.ctx = ctx
        self.db = db
        self.logger = logger or ctx.logger or logging.getLogger(__name__)

    def init(self):
        self.logger.info("[ EXPORT SERVICE ] init service...")
        self.feed_exporter = RenderService(self.ctx)

    def export(self, begin, end, wx_ids: list[str] = None):
        feeds = self.db.get_feeds_by_dur_ids(begin, end, wx_ids)
        for feed in feeds:
            contact = self.db.get_contact_by_username(feed.username)
            moment = MomentMsg.parse_xml(feed.content)
            self._export_moment(contact, moment)

    def _export_moment(self, contact: Contact, moment: MomentMsg):
        self.logger.info("[ EXPORT SERVICE ] exporting...")
        self.feed_exporter.export_md(contact, moment)
