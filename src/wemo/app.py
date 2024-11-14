from datetime import datetime
from pathlib import Path

import wemo.base.constant as constant
from wemo.base.scaffold import AbsApp
from wemo.service.export_service import ExportService
from wemo.utils.helper import get_wx_info
from wemo.service.sync_service import CacheSyncService
from wemo.service.updater_service import UserDataUpdateService
from wemo.model.user import User


class Wemo(AbsApp):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
        self.config.from_object(constant)
        self.user: User

    def init_app(self):
        self.logger.info("[ APP ] init app...")
        self._init_user()
        self._init_service()

    def _init_user(self):
        self.logger.info("[ APP ] init user...")
        self.user = User(
            proj_dir=constant.PROJECT_DIR,
            info=get_wx_info(),
            config=self.config,
            logger=self.logger,
        )
        self.user.init_user_dir()


    def _init_service(self):
        self.logger.info("[ APP ] init service...")
        self.cache_sync_service = CacheSyncService(self.user)
        self.cache_sync_service.init_service()
        self.data_update_service = UserDataUpdateService(self.user)
        self.export_service = ExportService(self.user)
