from datetime import datetime, timedelta
from wemo.database.db import DbCacheTuple
from wemo.database.micro_msg import MicroMsg, MicroMsgCache
from wemo.database.misc import Misc, MiscCache
from wemo.database.sns import Sns, SnsCache
from wemo.model.dto import MomentMsg
from wemo.update.avatar_updater import AvatarUpdater
from wemo.update.img_updater import ImageUpdater
from wemo.update.video_updater import VideoUpdater
from wemo.model.user import User


class UserDataUpdateService:

    def __init__(self, user: User):
        self.user = user
        self.logger = user.logger

    def init_service(self):
        self._init_db()
        self._init_db_set()
        self._init_exporter()

    def _init_db(self):
        user = self.user
        d1 = user.data_dir.db_dir  # 用户数据库数据
        self.sns = Sns(d1.joinpath("Sns.db"), self.logger)
        self.micro_msg = MicroMsg(d1.joinpath("MicroMsg.db"), self.logger)
        self.misc = Misc(d1.joinpath("Misc.db"), self.logger)

    def _init_cache(self):
        self.sns_cache = SnsCache(
            self.user.cache_dir.db_dir.joinpath("Sns.db"), self.logger
        )
        self.micro_msg_cache = MicroMsgCache(
            self.user.cache_dir.db_dir.joinpath("MicroMsg.db"), self.logger
        )
        self.misc_cache = MiscCache(
            self.user.cache_dir.db_dir.joinpath("Misc.db"), self.logger
        )

    def _init_db_set(self):
        self.sns_set = DbCacheTuple(
            self.sns,
            self.sns_cache,
            self.logger,
        )
        self.micro_msg_set = DbCacheTuple(
            self.micro_msg,
            self.micro_msg_cache,
            self.logger,
        )
        self.misc_set = DbCacheTuple(
            self.misc,
            self.misc_cache,
            self.logger,
        )
        self.sns_set.init_db_cache()
        self.micro_msg_set.init_db_cache()
        self.misc_set.init_db_cache()

    def _init_exporter(self):
        user = self.user
        self.img_exporter = ImageUpdater(
            user_data_img_dir=user.data_dir.img_dir,
            user_cache_img_dir=user.cache_dir.img_dir,
            logger=user.logger,
        )
        self.video_exporter = VideoUpdater(
            user_data_video_dir=user.data_dir.video_dir,
            user_cache_video_dir=user.cache_dir.video_dir,
            logger=user.logger,
        )
        self.avatar_exporter = AvatarUpdater(
            user_avatar_dir=user.data_dir.avatar_dir,
            logger=user.logger,
        )

    def update_db(self):
        try:
            self.logger.info("[ UPDATE SERVICE ] start update.")
            self._update_db(self.micro_msg_set)
            self._update_db(self.misc_set)
            self._update_db(self.sns_set)
        except Exception as e:
            self.logger.exception(e)

    def _update_db(self, dcs: DbCacheTuple):
        db_name = dcs.db.db_name
        db = dcs.db
        cache = dcs.cache
        for table_cls in dcs.db.table_cls_list:
            try:
                t_name = table_cls.__name__
                self.logger.debug(
                    f"[ UPDATE SERVICE ] db({db_name}) with table({t_name}) start update."
                )
                n1 = db.count_all(table_cls)
                cache_data = cache.query_all(table_cls)
                db.merge_all(cache_data)
                n2 = db.count_all(table_cls)
                self.logger.debug(
                    f"[ UPDATE SERVICE ] db({db_name}) with table({t_name}) db total is {n1}, cache total is {n2}."
                )
            except Exception as e:
                self.logger.exception(e)

    def update_img_video(self, begin: datetime = None, end: datetime = None):
        self.logger.info("[ UPDATE SERVICE ] start update img and video.")

        begin = begin or datetime.now() - timedelta(days=1)
        end = end or datetime.now()

        begin_int = int(begin.timestamp())
        end_int = int(end.timestamp())

        self.sns.get_feeds_by_duration_and_wxid(begin_int, end_int)
        res = self.sns.get_feeds_by_duration_and_wxid(begin_int, end_int)
        total = len(res)
        for idx, item in enumerate(res):
            try:
                self.logger.info(f"[ UPDATE SERVICE ] Process({idx+1}/{total})")
                xml = item.Content
                moment = MomentMsg.parse_xml(xml)
                contact, _ = self.micro_msg.get_contact_and_labels_by_username(
                    moment.user_name
                )
                contact_name = contact.Remark if contact.Remark else contact.NickName
                self.logger.debug(
                    f"[ UPDATE SERVICE ] CreateTime({moment.time}) UserName({contact_name}) Desc({moment.desc_brief})"
                )

                self.img_exporter.update_by_moment(moment)
                self.video_exporter.update_by_moment(moment)
            except Exception as e:
                self.logger.exception(e)

    def update_avatar(self):
        self.logger.info("[ UPDATE SERVICE ] start update avatar.")
        contacts = self.micro_msg.list_contact()
        for contact in contacts:
            try:
                self.avatar_exporter.get_avatar_by_username(contact.UserName)
            except Exception as e:
                self.logger.exception(e)
