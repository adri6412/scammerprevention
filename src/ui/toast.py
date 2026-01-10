from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PySide6.QtGui import QScreen

class ToastNotification(QWidget):
    def __init__(self, title, message, duration=10000):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # self.setAttribute(Qt.WA_TranslucentBackground) # Removed to ensure visibility
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.duration = duration
        self.init_ui(title, message)
    
    def init_ui(self, title, message):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # Content Frame
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #333333;
                color: white;
                border: 2px solid #555555;
            }
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        main_layout.addWidget(self.frame)

        content_layout = QVBoxLayout(self.frame)
        
        # Title
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FFCC00;")
        content_layout.addWidget(lbl_title)

        # Message
        lbl_msg = QLabel(message)
        lbl_msg.setStyleSheet("font-size: 12px;")
        lbl_msg.setWordWrap(True)
        content_layout.addWidget(lbl_msg)

        # Click to close
        self.setCursor(Qt.PointingHandCursor)

        # Auto close timer
        QTimer.singleShot(self.duration, self.close_toast)

    def show_toast(self):
        # Position bottom right
        screen = QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        
        width = 450
        height = 140
        
        # Bottom Right with some padding
        x = screen_geom.width() - width - 20
        y = screen_geom.height() - height - 20
        
        self.setGeometry(x, y, width, height)
        self.show()
    
    def mousePressEvent(self, event):
        self.close_toast()

    def close_toast(self):
        self.close()
