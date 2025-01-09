from queue import Queue

from PySide6.QtCore import QObject, Signal, SignalInstance, Slot


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
