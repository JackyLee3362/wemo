from datetime import datetime
import logging
from pathlib import Path

from wemo.backend.database.sns import Feed
from wemo.backend.render.render import HtmlRender
from wemo.backend.model.moment import MomentMsg
from wemo.backend.database.db_service import DBService
from wemo.backend.ctx import Context


class RenderService:
    def __init__(self, ctx: Context, db: DBService):
        self.ctx = ctx
        self.db = db
        self.logger: logging.Logger = ctx.logger
        self.output_dir: Path = ctx.output_dir
        self.html_render = HtmlRender(ctx)

    def init(self):
        """初始化"""
        self.logger.info("[ RENDER SERVICE ] init render service...")

    def render_sns_by_feed_id(self, feed_id: int):
        self.logger.info("[ RENDER SERVICE ] rendering sns by feed id...")
        feed = self.db.get_feed_by_feed_id(feed_id)
        moment_msg = self.render_moment([feed])

        file_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S.html")
        temp = self.html_render.template.temp_sns
        html = temp.render(moment_msg=moment_msg)
        with open(self.ctx.output_dir.joinpath(file_name), "w", encoding="utf-8") as f:
            f.write(html)

    def render_sns(self, begin, end, wx_ids: list[str] = None):
        self.logger.info("[ RENDER SERVICE ] rendering sns...")
        feeds = self.db.get_feeds_by_dur_wxids(begin, end, wx_ids)
        moment_msg = self.render_moment(feeds)

        file_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S.html")
        temp = self.html_render.template.temp_sns
        html = temp.render(moment_msg=moment_msg)
        with open(self.ctx.output_dir.joinpath(file_name), "w", encoding="utf-8") as f:
            f.write(html)

    def render_banner(self):
        self.logger.info("[ RENDER SERVICE ] rendering banner...")
        cover_url = self.db.get_cover_url()
        contact = self.db.get_contact_by_username(self.ctx.wx_id)
        banner_html = self.html_render.render_banner(cover_url, contact)
        return banner_html

    def render_moment(self, feeds: list[Feed]):
        self.logger.info("[ RENDER SERVICE ] rendering moment...")
        html = ""
        banner_html = self.render_banner()
        html += banner_html
        for feed in feeds:
            try:
                contact = self.db.get_contact_by_username(feed.username)
                moment = MomentMsg.parse_xml(feed.content)
                html_part = self.html_render.render(contact, moment)
                html += html_part
            except Exception as e:
                self.logger.exception(e)
        return html
