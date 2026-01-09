import sys
import os
import json
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QIcon, QAction

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.monitor import SystemMonitor
from src.ui.alert_window import AlertWindow
from src.ui.settings import SettingsWindow, SETTINGS_PATH
from src.utils import i18n
from src.utils.logger import logger

class ElderlyMonitorApp:
    def __init__(self):
        self.load_initial_language()
        
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False) # Keep running even if alert closes

        # Create System Tray Icon
        if os.path.exists("icon.png"):
            icon = QIcon("icon.png")
        else:
            # Fallback to standard icon
            icon = self.app.style().standardIcon(QStyle.SP_ComputerIcon)

        self.tray_icon = QSystemTrayIcon(icon, self.app)
        self.tray_icon.setToolTip(i18n.get_text("tray_tooltip"))
        
        # Tray Menu
        menu = QMenu()
        
        action_settings = QAction(i18n.get_text("tray_settings"), self.app)
        action_settings.triggered.connect(self.open_settings)
        menu.addAction(action_settings)
        
        menu.addSeparator()
        
        action_quit = QAction(i18n.get_text("tray_exit"), self.app)
        action_quit.triggered.connect(self.app.quit)
        menu.addAction(action_quit)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # Start Monitor
        self.monitor = SystemMonitor()
        self.monitor.threat_detected.connect(self.show_alert)
        self.monitor.start()

        # Store alert reference to prevent garbage collection
        self.current_alert = None
        self.settings_window = None

        logger.info("ElderlyMonitor started. Check tray icon.")

    def load_initial_language(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                    i18n.set_language(data.get('language', 'it'))
        except Exception:
            pass

    def open_settings(self):
        if not self.settings_window:
            self.settings_window = SettingsWindow(self.monitor.detector)
        self.settings_window.show()
        self.settings_window.activateWindow()

    def show_alert(self, threat_type, details, pid):
        # We handle PID ignoring in the monitor, but if the UI is already open for this PID, don't recreate.
        if self.current_alert and self.current_alert.isVisible():
            if self.current_alert.process_pid == pid:
                return

        logger.warning(f"THREAT DETECTED: {details}")
        
        # Show the Red Screen
        self.current_alert = AlertWindow(threat_type, details, pid)
        self.current_alert.action_taken.connect(lambda action: self.handle_alert_action(action, pid))
        self.current_alert.show()

    def handle_alert_action(self, action, pid):
        if action == "IGNORE":
            # Check if this was a Phishing alert that the user acknowledged
            if self.current_alert and "PHISHING" in self.current_alert.threat_type:
                 # Snooze phishing detection for 20 seconds to give user time to close tab
                 self.monitor.snooze_phishing(20)
            
            logger.info(f"User ignored threat for PID {pid}")
            self.monitor.add_ignored_pid(pid)


    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    monitor_app = ElderlyMonitorApp()
    monitor_app.run()
