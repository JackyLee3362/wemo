from datetime import datetime
import logging
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QHBoxLayout,
    QPlainTextEdit,
)
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QTextOption

from wemo.backend_thread import BackendThread
from wemo.gui.components.info_widget import InfoWidget
from wemo.gui_signal import GuiSignal
from wemo.gui.components.date_widget import DateWidget
from wemo.gui.components.contact_widget import ContactsWidget
from wemo.gui.components.misson_widget import MissonWidget

DARK_THEME_COLORS = {
    logging.DEBUG: "#0dbc6a",
    logging.INFO: "#4e8ed3",
    logging.WARNING: "yellow",
    logging.ERROR: "#f14c4c",
    logging.CRITICAL: "violet",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    @Slot(str, logging.LogRecord)
    def append_text(self, status: str, record: logging.LogRecord):
        color = DARK_THEME_COLORS.get(record.levelno, "black")
        s = '<pre><font color="%s">%s</font></pre>' % (color, status)
        self.log_widget.appendHtml(s)

    def inject(self, backend_thread: BackendThread, signal: GuiSignal):
        self.bt = backend_thread
        self.signal = signal
        self.flush_contacts()
        self.mission_widget.link_start.clicked.connect(self.submit_tasks)
        self.signal.contacts_update_signal.connect(self.contact_widget.update_contacts)
        self.contact_widget.flush_all.clicked.connect(
            lambda: self.bt.add_task(self.bt.backend.api_flush_contact)
        )
        self.signal.logging_signal.connect(self.append_text)
        self.signal.latest_feed_update_signal.connect(
            lambda feed: self.contact_widget.latest_feed_info.setText(feed)
        )
        self.signal.sync_progress.connect(self.mission_widget.update_sync_info)
        self.signal.update_progress.connect(self.mission_widget.update_update_info)
        self.signal.render_progress.connect(self.mission_widget.update_render_info)
        self.mission_widget.stop_btn.clicked.connect(self.bt.backend_stop)

    def init_ui(self):
        # 界面布局
        self.setWindowTitle("Wemo - 微信朋友圈备份工具")

        layout = QHBoxLayout()

        v1 = QVBoxLayout()
        v2 = QVBoxLayout()

        self.contact_widget = ContactsWidget(self)
        self.date_widget = DateWidget(self)
        self.mission_widget = MissonWidget(self)

        v1.addWidget(self.date_widget)
        v1.addWidget(self.contact_widget)
        v1.addWidget(self.mission_widget)

        self.info_widget = InfoWidget(self)
        self.log_widget = QPlainTextEdit(self)
        self.log_widget.setWordWrapMode(QTextOption.NoWrap)
        self.log_widget.setReadOnly(True)

        # v2.addWidget(self.info_widget)
        v2.addWidget(self.log_widget)

        layout.addLayout(v1)
        layout.addLayout(v2)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def flush_contacts(self):
        self.bt.add_task(self.bt.backend.api_flush_contact)
        self.bt.add_task(self.bt.backend.api_flush_latest_feed)

    def get_params(self):
        b = self.date_widget.begin_date.date()
        e = self.date_widget.end_date.date().addDays(-1)
        begin = datetime(b.year(), b.month(), b.day())
        end = datetime(e.year(), e.month(), e.day())
        wxids = self.contact_widget.wxids
        return begin, end, wxids

    @Slot()
    def submit_test_task(self):
        begin, end, wxids = self.get_params()
        self.bt.add_task(self.bt.backend.api_test, begin, end, wxids)

    @Slot()
    def submit_tasks(self):
        begin, end, wxids = self.get_params()
        if self.mission_widget.sync_check.checkState() == Qt.Checked:
            self.bt.add_task(self.bt.backend.api_sync, begin, end)
        if self.mission_widget.update_check.checkState() == Qt.Checked:
            self.bt.add_task(self.bt.backend.api_update, begin, end, wxids)
        if self.mission_widget.render_check.checkState() == Qt.Checked:
            self.bt.add_task(self.bt.backend.api_render, begin, end, wxids)
