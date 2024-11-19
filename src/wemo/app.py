from pathlib import Path

import wemo.base.constant as constant
from wemo.backend import Backend
from wemo.base.scaffold import Scaffold
from wemo.utils.helper import get_wx_info
from wemo.model.ctx import Context


class Wemo(Scaffold):
    default_config = {}

    def __init__(self, import_name, root_path: Path = None):
        super().__init__(import_name, root_path)
        self.config.from_object(constant)
        self.ctx = self._init_ctx()

    def init(self):
        self.logger.info("[ APP ] init app...")
        self._init_ctx()
        self._init_backend()
        self._init_gui()

    def _init_ctx(self):
        self.logger.info("[ APP ] init user...")
        self.ctx = Context(
            root_dir=self.config.get("PROJECT_PATH"),
            info=get_wx_info(),
            config=self.config,
            logger=self.logger,
        )
        self.ctx.init()

    def _init_backend(self):
        self.logger.info("[ APP ] init client...")
        self.backend = Backend(self.ctx)
        self.backend.init()

    def _init_gui(self):
        self.logger.info("[ APP ] init gui...")

    def run(self):
        self.logger.info("[ APP ] runing app...")
        self.init()
