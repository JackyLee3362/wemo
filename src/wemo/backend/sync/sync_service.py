from datetime import datetime
import logging
from wemo.backend.ctx import Context
from wemo.backend.sync.video_syncer import VideoSync
from wemo.backend.sync.db_syncer import DBSyncer
from wemo.backend.sync.img_syncer import ImgSyncer


class SyncService:
    def __init__(self, ctx: Context, logger: logging.Logger = None):
        # 依赖注入
        self.ctx = ctx
        self.cache_dir = ctx.cache_dir
        self.wx_sns_cache_dir = ctx.wx_sns_cache_dir
        self.key = ctx.wx_key
        self.wx_dir = ctx.wx_dir
        self.db_name_list = ctx.db_name_list
        self.bin_dir = ctx.config.get("BIN_DIR")
        self.logger = logger or ctx.logger or logging.getLogger(__name__)

    def init(self):
        self.logger.info("[ SYNC SERVICE ] init service...")
        self._init_db_decrypter()
        self._init_img_decrypter()
        self._init_video_decrypter()

    def _init_db_decrypter(self):
        self.db_decrypter = DBSyncer(
            wx_key=self.key,
            src_dir=self.wx_dir,
            dst_dir=self.cache_dir.db_dir,
            db_name_list=self.db_name_list,
            logger=self.logger,
        )

    def _init_img_decrypter(self):
        self.img_decrypter = ImgSyncer(
            src_dir=self.wx_sns_cache_dir,
            dst_dir=self.cache_dir.img_dir,
            logger=self.logger,
        )

    def _init_video_decrypter(self):
        self.video_decrypter = VideoSync(
            src_dir=self.wx_sns_cache_dir,
            dst_dir=self.cache_dir.video_dir,
            bin_path=self.bin_dir,
            logger=self.logger,
        )

    def sync(self, begin: datetime, end: datetime):
        self.logger.info("[ SYNC SERVICE ] sync starting...")
        self.sync_db()
        self.sync_img(begin, end)
        self.sync_video(begin, end)

    def sync_db(self):
        if not self.ctx.running:
            self.logger.debug("[ SYNC SERVICE ] stop sync db...")
            return
        self.logger.info("[ SYNC SERVICE ] db sync start...")
        self.db_decrypter.sync()

    def sync_img(self, begin: datetime = None, end: datetime = None):
        if not self.ctx.running:
            self.logger.debug("[ SYNC SERVICE ] stop sync img...")
            return
        self.logger.info("[ SYNC SERVICE ] img sync starting...")
        self.img_decrypter.sync(begin, end)

    def sync_video(self, begin: datetime = None, end: datetime = None):
        if not self.ctx.running:
            self.logger.debug("[ SYNC SERVICE ] stop sync video...")
            return
        self.logger.info("[ SYNC SERVICE ] video sync starting...")
        self.video_decrypter.sync(begin, end)
