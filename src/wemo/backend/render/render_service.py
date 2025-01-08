from datetime import datetime
import logging
from pathlib import Path

from wemo.backend.database.sns import Feed
from wemo.backend.render.render import HtmlRender
from wemo.backend.model.moment import MomentMsg
from wemo.backend.database.db_service import DBService
from wemo.backend.ctx import Context
from wemo.backend.res.res_manager import ResourceManager

logger = logging.getLogger(__name__)


class RenderService:
    def __init__(self, ctx: Context, db: DBService):
        self.ctx = ctx
        self.db = db
        self.output_dir: Path = ctx.output_dir
        self.init()

    def init(self):
        """初始化"""
        logger.info("[ RENDER SERVICE ] init render service...")
        self.res_manager = ResourceManager(self.ctx)
        self.html_render = HtmlRender(self.ctx, self.res_manager)

    def render_sns_by_feed_id(self, feed_id: int):
        logger.info("[ RENDER SERVICE ] rendering sns by feed id...")
        feed = self.db.get_feed_by_feed_id(feed_id)
        moment_msg = self.render_moment([feed])

        file_name = datetime.now().strftime("%Y-%m-%d %H-%M-%S.html")
        temp = self.html_render.template.temp_sns
        html = temp.render(moment_msg=moment_msg)
        with open(self.ctx.output_dir.joinpath(file_name), "w", encoding="utf-8") as f:
            f.write(html)

    def render_sns(self, begin: datetime, end: datetime, wx_ids: list[str] = None):
        logger.info("[ RENDER SERVICE ] rendering sns...")
        self.ctx.generate_output_date_dir()
        out_index = self.ctx.output_date_dir.joinpath("index.html")
        b_int = int(begin.timestamp())
        e_int = int(end.timestamp())
        feeds = self.db.get_feeds_by_dur_wxids(b_int, e_int, wx_ids)
        moment_msg = self.render_moment(feeds)

        temp = self.html_render.template.temp_sns
        html = temp.render(moment_msg=moment_msg)
        with open(out_index, "w", encoding="utf-8") as f:
            f.write(html)

    def render_banner(self):
        logger.info("[ RENDER SERVICE ] rendering banner...")
        cover_url = self.db.get_cover_url()
        contact = self.db.get_contact_by_username(self.ctx.wx_id)
        banner_html = self.html_render.render_banner(cover_url, contact)
        return banner_html

    def render_moment(self, feeds: list[Feed]):
        logger.info("[ RENDER SERVICE ] rendering moment...")
        html = ""
        banner_html = self.render_banner()
        html += banner_html
        total_feeds = len(feeds)
        for idx, feed in enumerate(feeds):
            if not self.ctx.running:
                logger.debug("[ RENDER SERVICE ] stop rendering...")
                break
            try:
                self.ctx.signal.render_progress.emit((idx + 1) / total_feeds)
                contact = self.db.get_contact_by_username(feed.username)
                logger.debug(
                    f"[ RENDER SERVICE ] rendering feed({feed.feed_id}), user({contact.repr_name})..."
                )
                try:
                    moment = MomentMsg.parse_xml(feed.content)
                except Exception:
                    logger.debug(f"parse xml error: {feed.feed_id}")
                    continue
                html_part = self.html_render.render(contact, moment)
                html += html_part
            except Exception as e:
                logger.exception(e)
        return html
