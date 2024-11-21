from typing import override
from PySide6.QtCore import QObject, Signal, SignalInstance

from wemo.comm_interface import InterfaceFront


class FrontImpl(QObject, InterfaceFront):
    test_processing: SignalInstance = Signal(int)
    sync_processing: SignalInstance = Signal(int)
    update_processing: SignalInstance = Signal(int)
    render_processing: SignalInstance = Signal(int)
    info_update: SignalInstance = Signal(dict)

    def __init__(self):
        super().__init__()

    @override
    def emit_test_processing(self, value: int):
        self.test_processing.emit(value)

    @override
    def emit_info_update(self, info):
        pass
