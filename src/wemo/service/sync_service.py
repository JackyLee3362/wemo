from wemo.base import constant
from wemo.decrypt.video_decrypter import VideoDecrypter
from wemo.decrypt.db_decrypter import DBDecrypter
from wemo.decrypt.img_decrypter import ImageDecrypter
from wemo.model.user import User


class CacheSyncService:
    def __init__(self, user: User):
        """使用 User 初始化"""
        self.user = user

        logger = user.logger
        wx_key = user.wx_key
        wx_dir = user.wx_dir
        self.db_decrypter = DBDecrypter(
            wx_key=wx_key,
            src_dir=wx_dir,
            dst_dir=user.cache_dir.db_dir,
            db_name_list=user.db_name_list,
            logger=logger,
        )
        bin_path = constant.BIN_DIR
        self.img_decrypter = ImageDecrypter(
            src_dir=user.wx_sns_cache_dir, dst_dir=user.cache_dir.img_dir,
            logger=logger
        )
        self.video_decrypter = VideoDecrypter(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.video_dir,
            bin_path=bin_path,
            logger=logger,
        )

    def update(self):
        self.update_db()
        self.update_img()
        self.update_video()

    def update_db(self):
        self.db_decrypter.decrypt()

    def update_img(self):
        self.img_decrypter.decrypt()

    def update_video(self):
        self.video_decrypter.decrypt()
