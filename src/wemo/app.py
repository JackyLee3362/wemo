from PySide6.QtWidgets import QApplication

from wemo.backend_thread import BackendThread
from wemo.gui.front_impl import FrontImpl
from wemo.gui.gui_v1 import Gui


class App:
    def __init__(self):
        # 初始化界面
        self.app = QApplication()
        self.gui = Gui()
        # 前置依赖
        self.front = FrontImpl()
        self.bt = BackendThread(self.front)
        # 初始化 backend，才会有 ctx
        self.gui.inject(self.bt, self.front)
        self.gui.init()

    def run(self):
        self.bt.start()
        self.gui.show()
        self.app.exec()
