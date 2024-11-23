from pathlib import Path
import time
from datetime import datetime

import wemo.backend.base.constant as constant
from wemo.backend.base.scaffold import Scaffold
from wemo.backend.database.db_service import DBService
from wemo.backend.render.render_service import RenderService
from wemo.backend.sync.sync_service import SyncService
from wemo.backend.update.updater_service import UserDataUpdateService
from wemo.backend.ctx import Context


class BackendImpl(Scaffold):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
        self.config.from_object(constant)
        self.ctx = Context(
            root_dir=self.config.get("PROJECT_PATH"),
            config=self.config,
            logger=self.logger,
        )

    def init(self):
        self.logger.info("[ BACKEND ] init backend...")
        self._init_ctx()
        self._init_db()
        self._init_service()

    def _init_ctx(self):
        self.logger.info("[ BACKEND ] init context...")
        self.ctx.init()

    def _init_db(self):
        self.db = DBService(self.ctx)
        self.db.init()

    def _init_service(self):
        self.syncer = SyncService(self.ctx)
        self.syncer.init()
        self.updater = UserDataUpdateService(self.ctx, self.db)
        self.updater.init()
        self.render = RenderService(self.ctx, self.db)
        self.render.init()

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
        self.ctx.signal.sync_progress.emit(0.0)
        self.syncer.sync_db()

        if not self.ctx.running:
            return
        self.ctx.signal.sync_progress.emit(0.3)
        self.syncer.sync_img(begin, end)

        if not self.ctx.running:
            return
        self.ctx.signal.sync_progress.emit(0.6)
        self.syncer.sync_video(begin, end)

        self.ctx.signal.sync_progress.emit(1.0)
        self.logger.info("[ BACKEND ] sync finish.")

    def api_update(self, begin: datetime, end: datetime, wxids: list[str]):
        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit(0.0)
        self.updater.update_db()

        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit(0.3)
        self.updater.update_img_video(begin, end, wxids)

        if not self.ctx.running:
            return
        self.ctx.signal.update_progress.emit(0.6)
        self.updater.update_avatar()

        self.ctx.signal.update_progress.emit(1.0)
        self.logger.info("[ BACKEND ] update finish.")

    def api_render(self, begin: datetime, end: datetime, wxids: list[str]):
        if not self.ctx.running:
            return
        self.render.render_sns(begin, end, wxids)
        self.logger.info("[ BACKEND ] render finish.")

    def api_test(self, *args, **kwargs):
        self.logger.info(f"[ BACKEND ] api test, args={args}, kwargs={kwargs}")
        for i in range(100):
            time.sleep(0.05)  # 模拟任务
            self.ctx.signal.test_processing.emit(i)
        self.logger.info("[ BACKEND ] api test done")
        return *args, *kwargs
