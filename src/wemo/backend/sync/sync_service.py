import logging
from datetime import datetime

from wemo.backend.common import constant
from wemo.backend.ctx import AppContext
from wemo.backend.sync.db_syncer import DBSyncer
from wemo.backend.sync.img_syncer import ImgSyncer
from wemo.backend.sync.video_syncer import VideoSync

logger = logging.getLogger(__name__)


class SyncService:
    def __str__(self):
        return "[ SYNC SERVICE ]"

    def __init__(self, ctx: AppContext):
        # 依赖注入
        self.ctx = ctx
        self.cache_dir = ctx.user_cache_dir
        self.wx_sns_cache_dir = ctx.wx_sns_cache_dir
        self.key = ctx.wx_key
        self.wx_dir = ctx.wx_dir
        self.db_name_list = ctx.db_name_list
        self.bin_dir = constant.BIN_DIR
        self.init()

    def init(self):
        logger.info(f"{self} init service...")
        self._init_db_decrypter()
        self._init_img_decrypter()
        self._init_video_decrypter()

    def _init_db_decrypter(self):
        self.db_syncer = DBSyncer(
            wx_key=self.key,
            src_dir=self.wx_dir,
            dst_dir=self.cache_dir.db_dir,
            db_name_list=self.db_name_list,
        )

    def _init_img_decrypter(self):
        self.img_syncer = ImgSyncer(
            src_dir=self.wx_sns_cache_dir, dst_dir=self.cache_dir.img_dir
        )

    def _init_video_decrypter(self):
        self.video_syncer = VideoSync(
            src_dir=self.wx_sns_cache_dir,
            dst_dir=self.cache_dir.video_dir,
            bin_path=self.bin_dir,
        )

    def sync(self, begin: datetime, end: datetime):
        logger.info(f"{self} sync starting...")
        self.sync_db()
        self.sync_img(begin, end)
        self.sync_video(begin, end)

    def sync_db(self):
        if not self.ctx.running:
            logger.debug(f"{self} stop sync db...")
            return
        logger.info(f"{self} db sync start...")
        self.db_syncer.sync()

    def sync_img(self, begin: datetime = None, end: datetime = None):
        if not self.ctx.running:
            logger.debug(f"{self} stop sync img...")
            return
        logger.info(f"{self} img sync starting...")
        self.img_syncer.sync(begin, end)

    def sync_video(self, begin: datetime = None, end: datetime = None):
        if not self.ctx.running:
            logger.debug(f"{self} stop sync video...")
            return
        logger.info(f"{self} video sync starting...")
        self.video_syncer.sync(begin, end)
