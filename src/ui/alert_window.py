import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLabel, 
                               QPushButton, QHBoxLayout, QApplication)
from PySide6.QtCore import Qt, Signal, QTimer
import psutil
try:
    import win32com.client
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from src.utils import i18n
from src.utils.logger import logger

class AlertWindow(QMainWindow):
    # Signal emitted when user chooses an action
    action_taken = Signal(str) # "BLOCK" or "IGNORE"

    def __init__(self, threat_type, threat_details, process_pid):
        super().__init__()
        self.threat_type = threat_type
        self.threat_details = threat_details
        self.process_pid = process_pid

        self.init_ui()
        # Delay TTS slightly to ensure window is fully visible first
        QTimer.singleShot(200, self.play_tts_alert)

    def play_tts_alert(self):
        if TTS_AVAILABLE:
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                # 1 = SVSFlagsAsync (Create async voice so it doesn't block UI)
                speaker.Speak(i18n.get_text("tts_alert"), 1)
            except Exception as e:
                logger.error(f"TTS Error: {e}")

    def init_ui(self):
        is_warning_only = ("BANKING" not in self.threat_type and "PHISHING" not in self.threat_type)

        # Window flags
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)

        if is_warning_only:
            # Show as large notification bottom-left
            screen = QApplication.primaryScreen()
            screen_geom = screen.availableGeometry()
            width = int(screen_geom.width() * 0.4)  # 40% of screen width
            height = int(screen_geom.height() * 0.4) # 40% of screen height
            # Bottom Left with padding
            x = 20
            y = screen_geom.height() - height - 20
            self.setGeometry(x, y, width, height)
        else:
            self.showFullScreen()
        
        # Main Widget and Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        central_widget.setLayout(layout)

        if "BANKING" in self.threat_type:
             header_text = i18n.get_text("alert_bank_header")
             sub_text = i18n.get_text("alert_bank_sub")
             start_color = "#8B0000" # Deep Red
             warning_tips = i18n.get_text("alert_bank_tips")
             font_scale = 1.0
        elif "PHISHING" in self.threat_type:
             header_text = i18n.get_text("alert_phishing_header")
             sub_text = i18n.get_text("alert_phishing_sub")
             start_color = "#B22222" # FireBrick Red
             warning_tips = i18n.get_text("alert_phishing_tips")
             font_scale = 1.0
        else:
             header_text = i18n.get_text("alert_rat_header")
             sub_text = i18n.get_text("alert_rat_sub")
             start_color = "#CC8800" # Orange-ish for warning
             warning_tips = i18n.get_text("alert_rat_tips")
             font_scale = 0.6  # Scale down fonts for smaller window

        central_widget.setStyleSheet(f"background-color: {start_color}; color: white; ")

        header = QLabel(f"⚠️ {header_text} ⚠️")
        header.setStyleSheet(f"font-size: {int(48 * font_scale)}px; font-weight: bold; color: yellow;")
        header.setAlignment(Qt.AlignCenter)
        header.setWordWrap(True)
        layout.addWidget(header)

        sub_header = QLabel(sub_text)
        sub_header.setStyleSheet(f"font-size: {int(32 * font_scale)}px; font-weight: bold;")
        sub_header.setAlignment(Qt.AlignCenter)
        sub_header.setWordWrap(True)
        layout.addWidget(sub_header)

        # Scam Warnings Box
        warning_box = QLabel(warning_tips)
        warning_box.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 0.3);
            color: #FFFFE0;
            font-size: {int(20 * font_scale)}px;
            font-weight: bold;
            padding: {int(20 * font_scale)}px;
            border-radius: 10px;
            margin: {int(20 * font_scale)}px;
        """)
        warning_box.setAlignment(Qt.AlignCenter)
        warning_box.setWordWrap(True)
        layout.addWidget(warning_box)

        # Details
        details_label = QLabel(f"\n{i18n.get_text('alert_details', details=self.threat_details)}\n")
        details_label.setStyleSheet(f"font-size: {int(24 * font_scale)}px;")
        details_label.setAlignment(Qt.AlignCenter)
        details_label.setWordWrap(True)
        layout.addWidget(details_label)

        # Question
        # Different question for phishing
        q_text = i18n.get_text("alert_question")
        if "PHISHING" in self.threat_type:
            q_text = "" # No generic question needed, tips are enough

        if q_text:
            question = QLabel(q_text)
            question.setStyleSheet(f"font-size: {int(28 * font_scale)}px; font-weight: bold; margin-bottom: {int(20 * font_scale)}px;")
            question.setAlignment(Qt.AlignCenter)
            question.setWordWrap(True)
            layout.addWidget(question)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(50)
        
        if "PHISHING" in self.threat_type:
            # Special Button for Phishing: "I Understand (Close Site)" - effectively ignores/closes alert
            self.btn_understand = QPushButton(i18n.get_text("btn_understand"))
            self.btn_understand.setCursor(Qt.PointingHandCursor)
            self.btn_understand.setStyleSheet("""
                QPushButton {
                    background-color: white; 
                    color: #006400; 
                    font-size: 24px; 
                    padding: 20px; 
                    border-radius: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #CCFFCC;
                }
            """)
            self.btn_understand.clicked.connect(self.on_ignore) # Treat as ignore (close window)
            btn_layout.addWidget(self.btn_understand)
        
        else:
            # Standard RAT/Banking Buttons
            # Block Button (Big and Clear)
            self.btn_block = QPushButton(i18n.get_text("btn_block"))
            self.btn_block.setCursor(Qt.PointingHandCursor)
            self.btn_block.setStyleSheet(f"""
                QPushButton {{
                    background-color: white; 
                    color: #8B0000; 
                    font-size: {int(24 * font_scale)}px;
                    padding: {int(20 * font_scale)}px;
                    border-radius: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FFCCCC;
                }}
            """)
            self.btn_block.clicked.connect(self.on_block)
            btn_layout.addWidget(self.btn_block)

            # Ignore Button (Smaller)
            self.btn_ignore = QPushButton(i18n.get_text("btn_ignore"))
            self.btn_ignore.setCursor(Qt.PointingHandCursor)
            self.btn_ignore.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent; 
                    color: #CCCCCC; 
                    font-size: {int(16 * font_scale)}px;
                    border: 1px solid #CCCCCC; 
                    padding: {int(10 * font_scale)}px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255, 255, 255, 0.1);
                }}
            """)
            self.btn_ignore.clicked.connect(self.on_ignore)
            btn_layout.addWidget(self.btn_ignore)

        layout.addLayout(btn_layout)

        # Show explicitly if we didn't show fullscreen earlier
        if is_warning_only:
            self.show()

    def on_block(self):
        # Kill the suspicious process tree
        # Strategy: Get the name of the process, then kill ALL instances of it.
        # This handles multi-process apps like AnyDesk/TeamViewer.
        target_name = None
        try:
            p = psutil.Process(self.process_pid)
            target_name = p.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.error(f"Process {self.process_pid} already dead or inaccessible.")

        # If we found the name, kill everything with that name
        if target_name:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] == target_name:
                         proc.kill()
                         logger.info(f"Killed related process: {proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            # Fallback: Just try to kill the PID blindly if we couldn't get the name
             try:
                p = psutil.Process(self.process_pid)
                p.kill()
             except:
                 pass

        self.close()
        self.action_taken.emit("BLOCK")

    def on_ignore(self):
        self.close()
        self.action_taken.emit("IGNORE")
