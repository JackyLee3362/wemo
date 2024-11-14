from datetime import datetime, timedelta
import logging
from wemo.model.moment import MomentMsg
from wemo.database.db_service import DBService
from wemo.update.avatar_updater import AvatarUpdater
from wemo.update.img_updater import ImageUpdater
from wemo.update.video_updater import VideoUpdater
from wemo.model.user import User


class UserDataUpdateService:

    def __init__(self, user: User, db: DBService, logger: logging.Logger = None):
        self.user = user
        self.db = db
        self.logger = logger or user.logger

    def init(self):
        self.logger.info("[ UPDATE SERVICE ] init update service...")
        self._init_exporter()

    def _init_exporter(self):
        user = self.user
        self.img_updater = ImageUpdater(
            dst_dir=user.data_dir.img_dir,
            src_dir=user.cache_dir.img_dir,
            logger=user.logger,
        )
        self.video_updater = VideoUpdater(
            dst_dir=user.data_dir.video_dir,
            src_dir=user.cache_dir.video_dir,
            logger=user.logger,
        )
        self.avatar_updater = AvatarUpdater(
            db=self.db,
            dst_dir=user.data_dir.avatar_dir,
            logger=user.logger,
        )

    def update_db(self):
        try:
            self.logger.info("[ UPDATE SERVICE ] updating...")
            self.db.update_db()
        except Exception as e:
            self.logger.exception(e)

    # :todo: 这里的服务不能依赖 exporter 才行
    def update_img_video(self, begin: datetime = None, end: datetime = None):
        self.logger.info("[ UPDATE SERVICE ] Img and video start are updating...")

        begin = begin or datetime.now() - timedelta(days=1)
        end = end or datetime.now()

        begin_int = int(begin.timestamp())
        end_int = int(end.timestamp())

        self.db.get_feeds_and_by_duration_and_wxids(begin_int, end_int)
        res = self.db.get_feeds_and_by_duration_and_wxids(begin_int, end_int)
        total = len(res)
        for idx, item in enumerate(res):
            try:
                self.logger.info(
                    f"[ UPDATE SERVICE ] Process({idx+1}/{total}) starting..."
                )
                xml = item.content
                moment = MomentMsg.parse_xml(xml)
                contact = self.db.get_contact_by_username(moment.username)
                contact_name = contact.remark if contact.remark else contact.nick_name
                self.logger.debug(
                    f"[ UPDATE SERVICE ] CreateTime({moment.time}) UserName({contact_name}) Desc({moment.desc_brief})"
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
