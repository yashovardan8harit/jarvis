from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont


class JarvisWindow(QWidget):

    showListeningSignal = pyqtSignal()
    showResponseSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.showListeningSignal.connect(self.show_listening)
        self.showResponseSignal.connect(self.show_response)

        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Label
        self.label = QLabel("Jarvis is sleeping...")
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 14))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Styling: White background + black text
        self.label.setStyleSheet("""
            QLabel {
                background-color: white;
                color: black;
                padding: 20px;
                border-radius: 15px;
            }
        """)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.resize(500, 150)
        self.hide()

    # =========================
    # Listening State
    # =========================
    def show_listening(self):
        self.label.setText("🎤 Listening...")
        self.adjust_size()
        self.show_centered()

    # =========================
    # Response State
    # =========================
    def show_response(self, text):
        self.label.setText(text)
        self.adjust_size()
        self.show_centered()

        QTimer.singleShot(5000, self.hide)

    # =========================
    # Auto Resize
    # =========================
    def adjust_size(self):
        self.label.adjustSize()
        width = 500
        height = self.label.sizeHint().height() + 40
        self.resize(width, height)

    # =========================
    # Position Bottom Center
    # =========================
    def show_centered(self):
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 100
        self.move(x, y)
        self.show()
