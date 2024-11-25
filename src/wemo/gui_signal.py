import logging
from PySide6.QtCore import QObject, Signal, SignalInstance


class GuiSignal(QObject):
    test_processing: SignalInstance = Signal(int)

    sync_progress: SignalInstance = Signal(str)
    update_progress: SignalInstance = Signal(str)
    render_progress: SignalInstance = Signal(str)

    contacts_update_signal: SignalInstance = Signal(dict)
    latest_feed_update_signal: SignalInstance = Signal(str)

    out_dir_signal: SignalInstance = Signal(str)

    logging_signal: SignalInstance = Signal(str, logging.LogRecord)

    def __init__(self):
        super().__init__()
