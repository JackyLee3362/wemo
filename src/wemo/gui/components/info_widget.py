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
    QFormLayout,
)
from PySide6.QtCore import QDate, QObject, Slot, Qt, QSize


class InfoWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.f1 = QFormLayout()

        self.abstract_label = QLabel("摘要信息", self)
        self.abstract_info = QTextEdit(self)
        self.abstract_info.setReadOnly(True)

        layout.addLayout(self.f1)
        layout.addWidget(self.abstract_label)
        layout.addWidget(self.abstract_info)

        self.setLayout(layout)

    @Slot(str, str)
    def add_info(self, key, value):
        self.abstract_info.append(f"{key}: {value}\n")
