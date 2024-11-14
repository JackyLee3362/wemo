import logging

from wemo.model.user import User
from wemo.database.db_service import DBService
from wemo.export.export_service import ExportService
from wemo.sync.sync_service import SyncService
from wemo.update.updater_service import UserDataUpdateService


class Backend:
    def __init__(self, user: User, logger: logging.Logger = None):
        self.user = user
        self.logger = logger or user.logger

    def init(self):
        self.logger.info("[ BACKEND ] init backend...")
        self._init_db()
        self._init_service()

    def _init_db(self):
        self.db = DBService(self.user)
        self.db.init()

    def _init_service(self):
        self.syncer = SyncService(self.user)
        self.syncer.init()
        self.data_updater = UserDataUpdateService(self.user, self.db)
        self.data_updater.init()
        self.exporter = ExportService(self.user, self.db)
        self.exporter.init()
