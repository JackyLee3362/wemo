import os
from datetime import datetime
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QListWidgetItem,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QMainWindow,
    QDateEdit,
    QDateTimeEdit,
    QTextEdit,
    QListWidget,
    QAbstractItemView,
    QHBoxLayout,
    QCheckBox,
    QFormLayout,
    QProgressBar,
)
from PySide6.QtCore import QDate, QObject, Slot, Qt, QSize

from wemo.backend.backend import BackendImpl
from wemo.backend_thread import BackendThread
from wemo.gui_signal import GuiSignal


class MissonWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.temp_process = "进度 ({}%)"
        self.out_dir = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        f1 = QFormLayout()

        self.sync_check = QCheckBox("同步数据", self)
        self.sync_check.setCheckState(Qt.Checked)
        self.sync_info = QProgressBar(self)
        self.sync_info.setMaximum(1)

        self.update_check = QCheckBox("更新数据", self)
        self.update_check.setCheckState(Qt.Checked)
        self.update_info = QProgressBar(self)
        self.update_info.setMaximum(1)

        self.render_check = QCheckBox("导出", self)
        self.render_check.setCheckState(Qt.Checked)
        self.render_info = QProgressBar(self)
        self.render_info.setMaximum(1)

        f1.addRow(self.sync_check, self.sync_info)
        f1.addRow(self.update_check, self.update_info)
        f1.addRow(self.render_check, self.render_info)

        self.link_start = QPushButton("启动!", self)
        self.link_start.setMinimumSize(QSize(150, 100))
        self.stop_btn = QPushButton("停止", self)

        self.out_dir_btn = QPushButton("打开输出文件夹")
        self.out_dir_btn.setDisabled(True)
        self.out_dir_btn.clicked.connect(
            lambda: os.system(f'explorer.exe "{self.out_dir}"')
        )

        layout.addLayout(f1)
        layout.addWidget(self.out_dir_btn)
        layout.addWidget(self.link_start)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

    def update_sync_info(self, value: float):
        self.sync_info.setValue(value)

    def update_update_info(self, value: float):
        self.update_info.setValue(value)

    def update_render_info(self, value: float):
        self.render_info.setValue(value)

    def update_out_dir(self, value: str):
        self.out_dir = value
        self.out_dir_btn.setDisabled(False)
