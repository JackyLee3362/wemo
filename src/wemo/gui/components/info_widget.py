from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFormLayout,
    QPlainTextEdit,
)
from PySide6.QtGui import QTextOption


class InfoWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        f1 = QFormLayout()

        self.abstract_label = QLabel("错误信息", self)
        self.console = QPlainTextEdit(self)
        self.console.setWordWrapMode(QTextOption.NoWrap)
        self.console.setReadOnly(True)

        self.clear_btn = QPushButton("清空信息", self)
        self.clear_btn.clicked.connect(self.console.clear)

        f1.addRow(self.abstract_label, self.clear_btn)

        layout.addLayout(f1)
        layout.addWidget(self.console)

        self.setLayout(layout)
