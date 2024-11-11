from wemo import constant
from wemo.base.db import AbsUserDB, UserTable
import logging

from wemo.decrypter import DBDecrypter, ImageDecrypter, VideoDecrypter
from wemo.user import User


class CacheUpdater:
    def __init__(self, user: User):
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
        self.img_decryper = ImageDecrypter(
            src_dir=user.wx_sns_cache_dir, dst_dir=user.cache_dir.img_dir, logger=logger
        )
        self.video_decrypert = VideoDecrypter(
            src_dir=user.wx_sns_cache_dir,
            dst_dir=user.cache_dir.video_dir,
            bin_path=bin_path,
            logger=logger,
        )

    def update_db(self):
        self.db_decrypter.decrypt()

    def update_img(self):
        self.img_decryper.decrypt()

    def update_video(self):
        self.video_decrypert.decrypt()


class UserDataUpdater:
    def __init__(self, db: AbsUserDB, cache: AbsUserDB, logger: logging.Logger = None):
        self.db = db
        self.cache = cache
        self.logger = logger or logging.getLogger(__name__)

    def update_db(self):
        db_name = self.db.db_name
        for table_cls in self.db.table_cls_list:
            t_name = table_cls.__name__
            self.logger.debug(f"[ {db_name}::{t_name} ] ----- START -----")
            self._update_db_table(table_cls)
            self.logger.debug(f"[ {db_name}::{t_name} ] -----  END  -----")

    def _update_db_table(self, table_cls: UserTable):
        db_name = self.db.db_name
        t_name = table_cls.__tablename__
        # 查询所有数据
        before = self.db.count_all(table_cls)
        cache_data = self.cache.query_all(table_cls)
        after = self.db.count_all(table_cls)
        self.logger.debug(
            f"[ {db_name}::{t_name} ] DB Total {before}, Cache Total: {after}"
        )

        # 开始合并
        self.db.merge_all(cache_data)

    def update_image():
        pass

    def update_video():
        pass
