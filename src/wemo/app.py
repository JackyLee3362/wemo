from pathlib import Path

import wemo.base.constant as constant
from wemo.backend import Backend
from wemo.base.scaffold import AbsApp
from wemo.utils.helper import get_wx_info
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
        self._init_backend()
        self._init_frontend()

    def _init_user(self):
        self.logger.info("[ APP ] init user...")
        self.user = User(
            proj_dir=constant.PROJECT_DIR,
            info=get_wx_info(),
            config=self.config,
            logger=self.logger,
        )
        self.user.init_user()

    def _init_backend(self):
        self.logger.info("[ APP ] init backend...")
        self.backend = Backend(self.user)
        self.backend.init()

    def _init_frontend(self):
        self.logger.info("[ APP ] init frontend...")

    def run(self):
        self.logger.info("[ APP ] runing app...")
        self.init_app()
