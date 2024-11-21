from datetime import datetime, timedelta
import logging
from wemo.backend.model.moment import MomentMsg
from wemo.backend.database.db_service import DBService
from wemo.backend.update.avatar_updater import AvatarUpdater
from wemo.backend.update.img_updater import ImageUpdater
from wemo.backend.update.video_updater import VideoUpdater
from wemo.backend.ctx import Context


class UserDataUpdateService:

    def __init__(self, ctx: Context, db: DBService, logger: logging.Logger = None):
        self.db = db
        self.img_dir = ctx.user_data_dir.img_dir
        self.cache_img_dir = ctx.cache_dir.img_dir
        self.video_dir = ctx.user_data_dir.video_dir
        self.cache_video_dir = ctx.cache_dir.video_dir
        self.avatar_dir = ctx.user_data_dir.avatar_dir
        self.logger = logger or ctx.logger or logging.getLogger(__name__)

    def init(self):
        self.logger.info("[ UPDATE SERVICE ] init update service...")
        self._init_exporter()

    def _init_exporter(self):
        self.img_updater = ImageUpdater(
            dst_dir=self.img_dir, src_dir=self.cache_img_dir, logger=self.logger
        )
        self.video_updater = VideoUpdater(
            dst_dir=self.video_dir, src_dir=self.cache_video_dir, logger=self.logger
        )
        self.avatar_updater = AvatarUpdater(
            db=self.db, dst_dir=self.avatar_dir, logger=self.logger
        )

    def update_db(self):
        try:
            self.logger.info("[ UPDATE SERVICE ] updating...")
            self.db.update_db()
        except Exception as e:
            self.logger.exception(e)

    # :todo: 这里的服务不能依赖 exporter 才行
    def update_img_video(
        self, begin: datetime = None, end: datetime = None, wx_ids: list[str] = None
    ):
        self.logger.info("[ UPDATE SERVICE ] Img and video start are updating...")

        begin = begin or datetime.now() - timedelta(days=1)
        end = end or datetime.now()

        begin_int = int(begin.timestamp())
        end_int = int(end.timestamp())

        res = self.db.get_feeds_and_by_duration_and_wxids(
            begin_int, end_int, wx_ids=wx_ids
        )
        total = len(res)
        for idx, feed in enumerate(res):
            try:
                self.logger.info(
                    f"[ UPDATE SERVICE ] Process({idx+1}/{total}) start handing feed_id({feed.feed_id})..."
                )
                xml = feed.content
                moment = MomentMsg.parse_xml(xml)
                contact = self.db.get_contact_by_username(moment.username)
                contact_name = contact.remark if contact.remark else contact.nick_name
                self.logger.debug(
                    f"[ UPDATE SERVICE ] CreateTime({moment.time}) UserName({contact_name}) wxid({contact.username}) \nDesc({moment.desc_brief})"
                )

                self.img_updater.update_by_moment(moment)
                self.video_updater.update_by_moment(moment)
            except Exception as e:
                self.logger.exception(e)

    def update_avatar(self):
        self.logger.info("[ UPDATE SERVICE ] avatar is updating...")
        contacts = self.db.get_contact_list()
        for contact in contacts:
            try:
                self.avatar_updater.update_by_username(contact.username)
            except Exception as e:
                self.logger.exception(e)
