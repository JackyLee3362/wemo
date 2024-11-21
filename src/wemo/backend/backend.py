from pathlib import Path
import time
from datetime import datetime
from typing import override

from wemo.comm_interface import InterfaceBackend
import wemo.backend.base.constant as constant
from wemo.backend.base.scaffold import Scaffold
from wemo.backend.database.db_service import DBService
from wemo.backend.render.render_service import RenderService
from wemo.backend.sync.sync_service import SyncService
from wemo.backend.update.updater_service import UserDataUpdateService
from wemo.backend.ctx import Context


class BackendImpl(Scaffold, InterfaceBackend):
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
        self.logger.info("[ BACKEND ] init app...")
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

    @override
    def api_flush_today(self, begin: datetime, end: datetime, wxids: list[str]):
        self.syncer.sync_db()
        self.syncer.sync_img(begin, end)
        self.syncer.sync_video(begin, end)
        self.updater.update_db()
        self.updater.update_img_video(begin, end, wxids)

    @override
    def api_sync(self, begin: datetime, end: datetime):
        self.syncer.sync_db()
        self.syncer.sync_img(begin, end)
        self.syncer.sync_video(begin, end)

    @override
    def api_update(self, begin: datetime, end: datetime, wxids: list[str]):
        self.updater.update_db()
        self.updater.update_img_video(begin, end, wxids)
        self.updater.update_avatar()

    @override
    def api_render(self, begin: datetime, end: datetime, wxids: list[str]):
        self.render.render_sns(begin, end, wxids)

    @override
    def api_test(self, *args, **kwargs):
        self.logger.info(f"[ BACKEND ] api test, args={args}, kwargs={kwargs}")
        for i in range(100):
            time.sleep(0.05)  # 模拟任务
            self.ctx.signal.emit_test_processing(i)
        self.logger.info("[ BACKEND ] api test done")
        return *args, *kwargs
