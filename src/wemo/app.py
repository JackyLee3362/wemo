from pathlib import Path

import wemo.base.constant as constant
from wemo.base.app import App
from wemo.utils.helper import get_wx_info
from wemo.service.sync_service import CacheSyncService
from wemo.service.updater_service import UserDataUpdateService
from wemo.model.user import User


class Wemo(App):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
        self.config.from_object(constant)
        self.user: User

    def init_app(self):
        self._init_user()
        self._init_updaters()

    def _init_user(self):
        self.user = User(
            proj_dir=constant.PROJECT_DIR,
            info=get_wx_info(),
            config=self.config,
            logger=self.logger,
        )
        self.user.init_user_dir()

    def _init_updaters(self):
        self.cache_updater = CacheSyncService(self.user)
        self.user_data_updater = UserDataUpdateService(self.user)

    def run(self):
        self.init_app()
        self.cache_updater.update()
        self.user_data_updater.update()
