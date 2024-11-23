from queue import Queue
from PySide6.QtCore import QThread

from wemo.backend.backend import BackendImpl
from wemo.gui_signal import GuiSignal


class BackendThread(QThread):

    def __init__(self, name: str, front_api: GuiSignal):
        super().__init__()
        self.task_queue = Queue()
        self.backend = BackendImpl(name)
        self.front_api = front_api

    def run(self):
        self.backend.ctx.inject(self.front_api)
        self.backend.init()
        while True:
            func, args, kwargs = self.task_queue.get()
            func(*args, **kwargs)

    def add_task(self, func, *args, **kwargs):
        self.backend_running()
        self.task_queue.put((func, args, kwargs))

    def backend_running(self):
        self.backend.ctx.running = True

    def backend_stop(self):
        self.backend.ctx.running = False
