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


class DateWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        f1 = QFormLayout()

        self.begin_label = QLabel(self)
        self.begin_label.setText("开始日期")

        self.end_label = QLabel(self)
        self.end_label.setText("结束日期 ")

        self.begin_date = QDateEdit(self)
        self.end_date = QDateEdit(self)

        self.begin_date.setDisplayFormat("yyyy 年 MM 月 dd 日")
        self.end_date.setDisplayFormat("yyyy 年 MM 月 dd 日")

        self.begin_date.setDate(QDate.currentDate().addDays(-2))
        self.end_date.setDate(QDate.currentDate())

        f1.addRow(self.begin_label, self.begin_date)
        f1.addRow(self.end_label, self.end_date)

        layout.addLayout(f1)

        self.setLayout(layout)
