import logging
from PySide6.QtWidgets import QApplication

from wemo.backend_thread import BackendThread
from wemo.gui_signal import GuiSignal
from wemo.gui.log_handler import add_signal_handler
from wemo.gui.main_window import MainWindow


class App:
    def __init__(self, name: str):
        # 初始化界面
        self.signal = GuiSignal()
        add_signal_handler(name, logging.DEBUG, self.signal.logging_signal)
        self.app = QApplication()
        self.gui = MainWindow()
        # 前置依赖
        self.bt = BackendThread(name, self.signal)
        # 初始化 backend，才会有 ctx
        self.gui.inject(self.bt, self.signal)

    def run(self):
        self.bt.start()
        self.gui.show()
        self.app.exec()
