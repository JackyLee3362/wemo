import os
import webbrowser
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QCheckBox,
    QFormLayout,
    QProgressBar,
    QLineEdit,
)
from PySide6.QtCore import Qt, QSize


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
        self.sync_check.setCheckState(Qt.Unchecked)
        self.sync_info = QLineEdit(self)
        self.sync_info.setReadOnly(True)

        self.update_check = QCheckBox("更新数据", self)
        self.update_check.setCheckState(Qt.Unchecked)
        self.update_info = QLineEdit(self)
        self.update_info.setReadOnly(True)

        self.render_check = QCheckBox("导出", self)
        self.render_check.setCheckState(Qt.Unchecked)
        self.render_info = QLineEdit(self)
        self.render_info.setReadOnly(True)

        f1.addRow(self.sync_check, self.sync_info)
        f1.addRow(self.update_check, self.update_info)
        f1.addRow(self.render_check, self.render_info)

        self.link_start = QPushButton("启动!", self)
        self.link_start.setMinimumSize(QSize(150, 100))
        self.stop_btn = QPushButton("停止", self)

        self.out_dir_btn = QPushButton("浏览器打开")
        self.out_dir_btn.setDisabled(True)
        self.out_dir_btn.clicked.connect(
            lambda: webbrowser.open(self.out_dir + "./index.html")
        )

        layout.addLayout(f1)
        layout.addWidget(self.out_dir_btn)
        layout.addWidget(self.link_start)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)

    def update_sync_info(self, value: str):
        self.sync_info.setText(value)

    def update_update_info(self, value: str):
        self.update_info.setText(value)

    def update_render_info(self, value: str):
        self.render_info.setText(value)

    def update_out_dir(self, value: str):
        self.out_dir = value
        self.out_dir_btn.setDisabled(False)
