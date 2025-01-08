import logging
from PySide6.QtCore import SignalInstance


class QHandler(logging.Handler):
    def __init__(self, signal: SignalInstance):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg, record)


def add_signal_handler(name, level, signal):
    logger = logging.getLogger(name)
    handler = QHandler(signal)
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    return logger
