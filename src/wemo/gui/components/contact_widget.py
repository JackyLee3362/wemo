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


class ContactsWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
        self.init_signal()

    def init_signal(self):
        self.select_all.clicked.connect(self.select_all_contacts)
        self.reverse_all.clicked.connect(self.reverse_all_contacts)
        self.search_btn.clicked.connect(self.search_contacts)
        self.search_bar.returnPressed.connect(self.search_contacts)
        self.search_reset.clicked.connect(self.reset_search)

    def init_ui(self):
        layout = QVBoxLayout()
        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        f1 = QFormLayout()

        self.list = QListWidget(self)

        self.search_bar = QLineEdit(self)
        self.search_btn = QPushButton("搜索")
        self.search_reset = QPushButton("重置")

        self.select_all = QPushButton("全选")
        self.reverse_all = QPushButton("反选")
        self.flush_all = QPushButton("更新通讯录（如无数据请先同步）")

        self.latest_feed_label = QLabel("最新的朋友圈", self)
        self.latest_feed_info = QLineEdit(self)
        self.latest_feed_info.setReadOnly(True)
        f1.addRow(self.latest_feed_label, self.latest_feed_info)

        self.list.setIconSize(QSize(12, 12))
        self.list.setSelectionMode(QAbstractItemView.MultiSelection)

        h1.addWidget(self.search_bar)
        h1.addWidget(self.search_btn)
        h1.addWidget(self.search_reset)

        h2.addWidget(self.select_all)
        h2.addWidget(self.reverse_all)

        layout.addLayout(h1)
        layout.addWidget(self.flush_all)
        layout.addWidget(self.list)
        layout.addLayout(h2)
        layout.addLayout(f1)

        self.setLayout(layout)

    @property
    def wxids(self):
        return [item.data(Qt.UserRole) for item in self.list.selectedItems()]

    @Slot()
    def search_contacts(self):
        keyword = self.search_bar.text()
        for idx in range(self.list.count()):
            item = self.list.item(idx)
            if keyword not in item.text():
                item.setHidden(True)

    @Slot()
    def reset_search(self):
        for idx in range(self.list.count()):
            item = self.list.item(idx)
            item.setHidden(False)

    @Slot()
    def select_all_contacts(self):
        for idx in range(self.list.count()):
            item = self.list.item(idx)
            item.setSelected(True)

    @Slot()
    def reverse_all_contacts(self):
        for idx in range(self.list.count()):
            item = self.list.item(idx)
            if item.isSelected():
                item.setSelected(False)
            else:
                item.setSelected(True)

    @Slot(dict)
    def update_contacts(self, contacts: dict):
        self.contacts = contacts
        self.list.clear()
        for wxid, name in contacts.items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, wxid)
            self.list.addItem(item)
