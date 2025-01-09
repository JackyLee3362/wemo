import logging
from queue import Queue
from threading import Thread
from time import sleep

from wemo.backend.backend import Backend
from wemo.backend.ctx import AppContext
from wemo.gui_signal import GuiSignal

logger = logging.getLogger(__name__)


class BackendThread(Thread):

    def __init__(self, name: str, signal: GuiSignal):
        super().__init__()
        self.task_queue = Queue()
        self.ctx = AppContext(name)
        self.backend = Backend(self.ctx)
        self.front_api = signal

    def run(self):
        # 必须保证初始化用户信息才能继续
        while not self.ctx.has_init_user:
            self.ctx.init_user_wx_info()
            sleep(1)
        self.ctx.init_user_dir()
        self.ctx.inject(self.front_api)
        self.backend.init()
        while True:
            try:
                func, args, kwargs = self.task_queue.get()
                func(*args, **kwargs)
            except Exception as e:
                logger.exception(e)

    def add_task(self, func, *args, **kwargs):
        self.backend_running()
        self.task_queue.put((func, args, kwargs))

    def backend_running(self):
        self.ctx.running = True

    def backend_stop(self):
        self.ctx.running = False
