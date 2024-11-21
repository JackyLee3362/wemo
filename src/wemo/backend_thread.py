from queue import Queue
from PySide6.QtCore import QThread

from wemo.backend.backend import BackendImpl
from wemo.comm_interface import InterfaceFront


class BackendThread(QThread):

    def __init__(self, front_api: InterfaceFront):
        super().__init__()
        self.is_running = True
        self.task_queue = Queue()
        self.backend = BackendImpl(__name__)
        self.front_api = front_api

    def run(self):
        self.backend.ctx.inject(self.front_api)
        self.backend.init()
        while self.is_running:
            func, args, kwargs = self.task_queue.get()
            func(*args, **kwargs)

    def add_task(self, func, *args, **kwargs):
        self.task_queue.put((func, args, kwargs))

    def backend_running(self):
        self.is_running = True

    def backend_stop(self):
        self.is_running = False
