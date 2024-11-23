import logging
from PySide6.QtCore import QObject, Signal, SignalInstance


class GuiSignal(QObject):
    test_processing: SignalInstance = Signal(int)

    sync_progress: SignalInstance = Signal(float)
    update_progress: SignalInstance = Signal(float)
    render_progress: SignalInstance = Signal(float)

    contacts_update_signal: SignalInstance = Signal(dict)
    latest_feed_update_signal: SignalInstance = Signal(str)

    out_dir_signal: SignalInstance = Signal(str)

    info_update_signal: SignalInstance = Signal(str, str)
    logging_signal: SignalInstance = Signal(str, logging.LogRecord)

    def __init__(self):
        super().__init__()
