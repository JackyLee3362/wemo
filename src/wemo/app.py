from pathlib import Path

from colorama import init

from wemo.base.app import App
import wemo.constant as constant
from wemo.helper import get_wx_info
from wemo.updater import CacheUpdater
from wemo.user import User


class Wemo(App):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
        self.config.from_object(constant)
        self.user: User = None

    def init_user(self):
        self.user = User(
            proj_dir=constant.PROJECT_DIR,
            info=get_wx_info(),
            config=self.config,
            logger=self.logger,
        )
        self.user.init_user_dir()

    def init_updater(self):
        self.cache_updater = CacheUpdater(self.user)
        # :todo: 还有一个 UserDataUpdater

    def _get_wx_info(self):
        infos = get_wx_info()
        return infos

    def run(self):
        self.init_user()
        self.init_updater()
        self.cache_updater.update_db()
        self.cache_updater.update_img()
        self.cache_updater.update_video()
