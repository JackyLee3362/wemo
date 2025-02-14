import logging
import time
from datetime import datetime

from wemo.backend.ctx import AppContext
from wemo.backend.database.db_service import DBService
from wemo.backend.render.render_service import RenderService
from wemo.backend.sync.sync_service import SyncService
from wemo.backend.update.updater_service import UserDataUpdateService

logger = logging.getLogger(__name__)


class Backend:
    default_config = {}

    def __str__(self):
        return "[ BACKEND ]"

    def __init__(self, ctx: AppContext):
        self.ctx = ctx

    def init(self):
        logger.info(f"{self} init backend...")
        self.db = DBService(self.ctx)
        self.syncer = SyncService(self.ctx)
        self.updater = UserDataUpdateService(self.ctx, self.db)
        self.render = RenderService(self.ctx, self.db)

    def api_flush_db(self):
        logger.info(f"{self} flush db...")
        self.db.flush_db()

    def api_flush_contact(self):
        contacts = self.db.get_contact_list()
        res = {item.username: item.repr_name for item in contacts}
        self.ctx.signal.contacts_update_signal.emit(res)

    def api_flush_latest_feed(self):
        res = self.db.get_latest_feed()
        if res is None:
            self.ctx.signal.latest_feed_update_signal.emit("无")
            return
        d = datetime.fromtimestamp(res.create_time).strftime("%Y-%m-%d %H:%M:%S")
        self.ctx.signal.latest_feed_update_signal.emit(d)

    def api_flush_today(self, begin: datetime, end: datetime, wxids: list[str]):
        self.syncer.sync_db()
        self.syncer.sync_img(begin, end)
        self.syncer.sync_video(begin, end)
        self.updater.update_db()
        self.updater.update_img_video(begin, end, wxids)

    def api_sync(self, begin: datetime, end: datetime):
        if not self.ctx.running:
            return
        self.ctx.signal.sync_progress.emit("开始同步数据库...")
        self.syncer.sync_db()

        if not self.ctx.running:
            return
        self.ctx.signal.sync_progress.emit("开始同步图片...")
        self.syncer.sync_img(begin, end)

        if not self.ctx.running:
            return
        self.ctx.signal.sync_progress.emit("开始同步视频...")
        self.syncer.sync_video(begin, end)
        self.ctx.signal.sync_progress.emit("同步完成")
        logger.info(f"{self} sync finish.")

    def api_update(self, begin: datetime, end: datetime, wxids: list[str]):
        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit("开始更新数据库...")
        self.updater.update_db()

        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit("开始更新图片和视频...")
        self.updater.update_img_video(begin, end, wxids)

        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit("开始更新头像...")
        self.updater.update_avatar()

        self.ctx.signal.update_progress.emit("更新完成")
        logger.info(f"{self} update finish.")

    def api_render(self, begin: datetime, end: datetime, wxids: list[str]):
        if not self.ctx.running:
            return
        self.render.render_sns(begin, end, wxids)
        logger.info(f"{self} render finish.")
        self.ctx.signal.render_progress.emit(
            f"导出完成到 {self.ctx.output_date_dir.user_root_dir}"
        )
        self.ctx.signal.out_dir_signal.emit(str(self.ctx.output_date_dir.user_root_dir))

    def api_test(self, *args, **kwargs):
        logger.info(f"{self} api test, args={args}, kwargs={kwargs}")
        for i in range(100):
            time.sleep(0.05)  # 模拟任务
            self.ctx.signal.test_processing.emit(i)
        logger.info(f"{self} api test done")
        return *args, *kwargs
