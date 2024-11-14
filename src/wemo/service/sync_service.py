from datetime import datetime
from wemo.decrypt.video_decrypter import VideoDecrypter
from wemo.decrypt.db_decrypter import DBDecrypter
from wemo.decrypt.img_decrypter import ImageDecrypter
from wemo.model.user import User


class CacheSyncService:
    def __init__(self, user: User):
        """使用 User 初始化"""
        self.user = user
        self.logger = user.logger

    def init_service(self):
        self.logger.info("[ SYNC SERVICE ] init service.")
        self._init_db_decrypter()
        self._init_img_decrypter()
        self._init_video_decrypter()

    def _init_db_decrypter(self):
        user = self.user
        self.db_decrypter = DBDecrypter(
            wx_key=user.wx_key,
            src_dir=user.wx_dir,
            dst_dir=user.cache_dir.db_dir,
            db_name_list=user.db_name_list,
            logger=self.logger,
        )

    def _init_img_decrypter(self):
        user = self.user
        self.img_decrypter = ImageDecrypter(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.img_dir,
            logger=self.logger,
        )

    def _init_video_decrypter(self):
        user = self.user
        self.video_decrypter = VideoDecrypter(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.video_dir,
            bin_path=user.config.get("BIN_DIR"),
            logger=self.logger,
        )

    def sync(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] start sync.")
        self.sync_db()
        self.sync_img(begin, end)
        self.sync_video(begin, end)

    def sync_db(self):
        self.logger.info("[ SYNC SERVICE ] start sync db.")
        self.db_decrypter.decrypt()

    def sync_img(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] start sync img.")
        self.img_decrypter.decrypt(begin, end)

    def sync_video(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] start sync video.")
        self.video_decrypter.decrypt(begin, end)
