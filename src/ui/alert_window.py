import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                               QPushButton, QHBoxLayout, QApplication)
from PySide6.QtCore import Qt, Signal
import psutil

class AlertWindow(QMainWindow):
    # Signal emitted when user chooses an action
    action_taken = Signal(str) # "BLOCK" or "IGNORE"

    def __init__(self, threat_type, threat_details, process_pid):
        super().__init__()
        self.threat_type = threat_type
        self.threat_details = threat_details
        self.process_pid = process_pid

        self.init_ui()

    def init_ui(self):
        # Window flags to make it full screen and always on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.showFullScreen()
        
        # Main Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(layout)

        if "BANKING" in self.threat_type:
             header_text = "CRITICAL SECURITY RISK"
             sub_text = "BANKING DATA AT RISK"
             start_color = "#8B0000" # Deep Red
             warning_tips = "We detected a Remote Tool accessing your Bank.\nThis is ALWAYS a SCAM. BLOCK IT NOW."
        else:
             header_text = "SECURITY WARNING"
             sub_text = "REMOTE ACCESS TOOL DETECTED"
             start_color = "#CC8800" # Orange-ish for warning
             warning_tips = (
                 "HOW TO SPOT A SCAMMER:\n"
                 "• A REAL technician will NEVER ask for your passwords.\n"
                 "• A REAL technician will NEVER ask you to log into your bank.\n"
                 "• A REAL technician will NEVER ask for Gift Cards (Google Play, Amazon)."
             )

        central_widget.setStyleSheet(f"background-color: {start_color}; color: white;")

        header = QLabel(f"⚠️ {header_text} ⚠️")
        header.setStyleSheet("font-size: 48px; font-weight: bold; color: yellow;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        sub_header = QLabel(sub_text)
        sub_header.setStyleSheet("font-size: 32px; font-weight: bold;")
        sub_header.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_header)

        # Scam Warnings Box
        warning_box = QLabel(warning_tips)
        warning_box.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.3);
            color: #FFFFE0;
            font-size: 20px;
            font-weight: bold;
            padding: 20px;
            border-radius: 10px;
            margin: 20px;
        """)
        warning_box.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning_box)

        # Details
        details_label = QLabel(f"\nDetails: {self.threat_details}\n")
        details_label.setStyleSheet("font-size: 24px;")
        details_label.setAlignment(Qt.AlignCenter)
        details_label.setWordWrap(True)
        layout.addWidget(details_label)

        # Question
        question = QLabel("Is someone unexpected trying to control your computer?")
        question.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px;")
        question.setAlignment(Qt.AlignCenter)
        layout.addWidget(question)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(50)
        
        # Block Button (Big and Clear)
        self.btn_block = QPushButton("⛔ BLOCK CONNECTION (Recommended)")
        self.btn_block.setCursor(Qt.PointingHandCursor)
        self.btn_block.setStyleSheet("""
            QPushButton {
                background-color: white; 
                color: #8B0000; 
                font-size: 24px; 
                padding: 20px; 
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFCCCC;
            }
        """)
        self.btn_block.clicked.connect(self.on_block)
        btn_layout.addWidget(self.btn_block)

        # Ignore Button (Smaller)
        self.btn_ignore = QPushButton("I am doing this myself (Ignore)")
        self.btn_ignore.setCursor(Qt.PointingHandCursor)
        self.btn_ignore.setStyleSheet("""
            QPushButton {
                background-color: transparent; 
                color: #CCCCCC; 
                font-size: 16px; 
                border: 1px solid #CCCCCC; 
                padding: 10px; 
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.btn_ignore.clicked.connect(self.on_ignore)
        btn_layout.addWidget(self.btn_ignore)

        layout.addLayout(btn_layout)

    def on_block(self):
        # Kill the suspicious process
        try:
            p = psutil.Process(self.process_pid)
            p.terminate() # Try graceful first
            try:
                p.wait(timeout=1)
            except psutil.TimeoutExpired:
                p.kill() # Force kill
            
            print(f"Process {self.process_pid} killed by user.")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Failed to kill process: {e}")
        
        self.close()
        self.action_taken.emit("BLOCK")

    def on_ignore(self):
        self.close()
        self.action_taken.emit("IGNORE")
