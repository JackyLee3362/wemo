from datetime import datetime
import logging
from wemo.model.user import User
from wemo.sync.video_syncer import VideoSync
from wemo.sync.db_syncer import DBSyncer
from wemo.sync.img_syncer import ImgSyncer


class SyncService:
    def __init__(self, user: User, logger: logging.Logger = None):
        self.user = user
        self.logger = logger or user.logger

    def init(self):
        self.logger.info("[ SYNC SERVICE ] init service...")
        self._init_db_decrypter()
        self._init_img_decrypter()
        self._init_video_decrypter()

    def _init_db_decrypter(self):
        user = self.user
        self.db_decrypter = DBSyncer(
            wx_key=user.wx_key,
            src_dir=user.wx_dir,
            dst_dir=user.cache_dir.db_dir,
            db_name_list=user.db_name_list,
            logger=self.logger,
        )

    def _init_img_decrypter(self):
        user = self.user
        self.img_decrypter = ImgSyncer(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.img_dir,
            logger=self.logger,
        )

    def _init_video_decrypter(self):
        user = self.user
        self.video_decrypter = VideoSync(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.video_dir,
            bin_path=user.config.get("BIN_DIR"),
            logger=self.logger,
        )

    def sync(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] sync starting...")
        self.sync_db()
        self.sync_img(begin, end)
        self.sync_video(begin, end)

    def sync_db(self):
        self.logger.info("[ SYNC SERVICE ] db sync start...")
        self.db_decrypter.sync()

    def sync_img(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] img sync starting...")
        self.img_decrypter.sync(begin, end)

    def sync_video(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] video sync starting...")
        self.video_decrypter.sync(begin, end)
