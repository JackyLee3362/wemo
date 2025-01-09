import logging
from datetime import datetime, timedelta

from wemo.backend.common.model import MomentMsg
from wemo.backend.ctx import Context
from wemo.backend.database.db_service import DBService
from wemo.backend.update.avatar_updater import AvatarUpdater
from wemo.backend.update.img_updater import ImageUpdater
from wemo.backend.update.video_updater import VideoUpdater

logger = logging.getLogger(__name__)


class UserDataUpdateService:

    def __str__(self):
        return "[ UPDATE SERVICE ]"

    def __init__(self, ctx: Context, db: DBService):
        self.db = db
        self.ctx = ctx
        self.img_dir = ctx.user_data_dir.img_dir
        self.cache_img_dir = ctx.user_cache_dir.img_dir
        self.video_dir = ctx.user_data_dir.video_dir
        self.cache_video_dir = ctx.user_cache_dir.video_dir
        self.avatar_dir = ctx.user_data_dir.avatar_dir
        self.init()

    def init(self):
        logger.info(f"{self} init update service...")
        self._init_exporter()

    def _init_exporter(self):
        self.img_updater = ImageUpdater(
            dst_dir=self.img_dir, src_dir=self.cache_img_dir
        )
        self.video_updater = VideoUpdater(
            dst_dir=self.video_dir, src_dir=self.cache_video_dir
        )
        self.avatar_updater = AvatarUpdater(db=self.db, dst_dir=self.avatar_dir)

    def update_db(self):
        if not self.ctx.running:
            logger.debug(f"{self} stop update db...")
            return
        try:
            logger.info(f"{self} updating...")
            self.db.update_db()
        except Exception as e:
            logger.exception(e)

    # :todo: 这里的服务不能依赖 exporter 才行
    def update_img_video(
        self, begin: datetime = None, end: datetime = None, wx_ids: list[str] = None
    ):
        logger.info(f"{self} Img and video start are updating...")

        begin = begin or datetime.now() - timedelta(days=1)
        end = end or datetime.now()

        begin_int = int(begin.timestamp())
        end_int = int(end.timestamp())

        res = self.db.get_feeds_and_by_duration_and_wxids(
            begin_int, end_int, wx_ids=wx_ids
        )
        total = len(res)
        for idx, feed in enumerate(res):
            if not self.ctx.running:
                logger.debug(f"{self} stop update img and video...")
                break
            try:
                logger.info(
                    f"{self} Process({idx+1}/{total}) start handing feed_id({feed.feed_id})..."
                )
                xml = feed.content
                try:
                    moment = MomentMsg.parse_xml(xml)
                except Exception:
                    logger.error(f"parse xml error: {feed.feed_id}")
                    continue
                contact = self.db.get_contact_by_username(moment.username)
                logger.debug(
                    f"{self} {moment.time}-{contact.repr_name}-{feed.feed_id}\nDesc({moment.desc_brief})"
                )

                suffix = f"{contact.repr_name}-{feed.feed_id}"

                self.img_updater.update_by_moment(moment, suffix)
                self.video_updater.update_by_moment(moment, suffix)
            except Exception as e:
                logger.exception(e)

    def update_avatar(self):
        logger.info(f"{self} avatar is updating...")
        contacts = self.db.get_contact_list()
        for contact in contacts:
            if not self.ctx.running:
                logger.debug(f"{self} stop update avatar...")
                break
            try:
                self.avatar_updater.update_by_username(contact.username)
            except Exception as e:
                logger.exception(e)
