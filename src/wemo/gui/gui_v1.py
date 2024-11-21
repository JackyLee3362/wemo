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
)
from PySide6.QtCore import QDate, Signal, QObject, SignalInstance, Slot

from wemo.backend_thread import BackendThread
from wemo.comm_interface import InterfaceBackend, InterfaceFront
from wemo.gui.front_impl import FrontImpl


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def inject(self, backend_thread: BackendThread, signal: FrontImpl):
        self.bt = backend_thread
        self.signal = signal

    def init_ui(self):
        # 界面布局
        self.setWindowTitle("Task Submission Example")
        layout = QVBoxLayout()

        self.begin_label = QLabel(self)
        self.begin_label.setText("Begin Date")

        self.end_label = QLabel(self)
        self.end_label.setText("End Date")

        self.begin_date = QDateEdit(self)
        self.begin_date.setDate(QDate.currentDate().addDays(-1))

        self.end_date = QDateEdit(self)
        self.end_date.setDate(QDate.currentDate())

        self.submit_button = QPushButton("Submit Task", self)

        self.output = QLabel(self)
        self.output.setText("Result will appear here")

        layout.addWidget(self.begin_label)
        layout.addWidget(self.begin_date)

        layout.addWidget(self.end_label)
        layout.addWidget(self.end_date)

        layout.addWidget(self.submit_button)
        layout.addWidget(self.output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init(self):
        self.submit_button.clicked.connect(self.submit_task)
        self.signal.test_processing.connect(self.show_result)

    @Slot(datetime, datetime)
    def submit_task(self):
        self.output.setText("Task started")
        b = self.begin_date.date()
        e = self.end_date.date()
        begin = datetime(b.year(), b.month(), b.day())
        end = datetime(e.year(), e.month(), e.day())
        self.bt.add_task(self.bt.backend.api_test, begin, end)

    @Slot(int)
    def show_result(self, progress):
        if progress < 99:
            self.output.setText(f"Task ({progress}/100)")
        else:
            self.output.setText("Task completed")
