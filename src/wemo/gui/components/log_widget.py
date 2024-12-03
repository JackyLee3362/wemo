from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFormLayout,
    QPlainTextEdit,
)
from PySide6.QtGui import QTextOption


class LogWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        f1 = QFormLayout()
        self.console = QPlainTextEdit(self)
        self.console.setWordWrapMode(QTextOption.NoWrap)
        self.console.setReadOnly(True)
        self.log_label = QLabel("日志", self)

        self.clear_btn = QPushButton("清空日志", self)
        self.clear_btn.clicked.connect(self.console.clear)

        f1.addRow(self.log_label, self.clear_btn)
        layout.addLayout(f1)
        layout.addWidget(self.console)

        self.setLayout(layout)
