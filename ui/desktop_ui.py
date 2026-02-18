from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal

import sys

class JarvisWindow(QWidget):
    showListeningSignal = pyqtSignal()
    showResponseSignal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        self.showListeningSignal.connect(self.show_listening)
        self.showResponseSignal.connect(self.show_response)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setFixedSize(400, 150)

        layout = QVBoxLayout()

        self.label = QLabel("Jarvis is sleeping...")
        self.label.setFont(QFont("Arial", 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.hide()

    def show_listening(self):
        self.label.setText("🎤 Listening...")
        self.show_centered()

    def show_response(self, text):
        self.label.setText(text)
        self.show_centered()

        QTimer.singleShot(4000, self.hide)

    def show_centered(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 100
        self.move(x, y)
        self.show()
