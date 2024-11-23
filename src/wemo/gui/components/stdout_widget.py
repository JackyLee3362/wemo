import sys
from queue import Queue
import time
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QApplication,
)
from PySide6.QtCore import QDate, QObject, Slot, Qt, Signal, QThread, SignalInstance
from PySide6.QtGui import QTextCursor


class MyReceiver(QObject):
    log_signal: SignalInstance = Signal(str)

    def __init__(self, queue: Queue, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        self.queue = queue

    @Slot()
    def run(self):
        while True:
            text = self.queue.get()
            self.log_signal.emit(text)
