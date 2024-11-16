import logging

from wemo.model.ctx import Context
from wemo.database.db_service import DBService
from wemo.export.export_service import ExportService
from wemo.sync.sync_service import SyncService
from wemo.update.updater_service import UserDataUpdateService


class Backend:
    def __init__(self, ctx: Context, logger: logging.Logger = None):
        self.ctx = ctx
        self.logger = logger or ctx.logger

    def init(self):
        self.logger.info("[ CLIENT ] init backend...")
        self._init_db()
        self._init_service()

    def _init_db(self):
        self.db = DBService(self.ctx)
        self.db.init()

    def _init_service(self):
        self.syncer = SyncService(self.ctx)
        self.syncer.init()
        self.updater = UserDataUpdateService(self.ctx, self.db)
        self.updater.init()
        self.exporter = ExportService(self.ctx, self.db)
        self.exporter.init()
