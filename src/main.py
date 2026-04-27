import sys
import os
import json
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QIcon, QAction

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.monitor import SystemMonitor
from src.ui.alert_window import AlertWindow
from src.ui.toast import ToastNotification
from src.ui.settings import SettingsWindow, SETTINGS_PATH
from src.utils import i18n
from src.utils.logger import logger
from src.utils.mailer import send_alert_email
import datetime
import threading
import keyboard
from PySide6.QtGui import QScreen

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

        # Clipboard Monitor
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.check_clipboard)

        # Panic Button Hook (Ctrl+Alt+S)
        try:
            keyboard.add_hotkey('ctrl+alt+s', self.execute_panic_mode)
            logger.info("Panic button hotkey (Ctrl+Alt+S) registered successfully.")
        except Exception as e:
            logger.error(f"Failed to register panic button hotkey: {e}")

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
        
        # DIFFERENTIAL ALERTING
        if threat_type == "PHISHING_WARNING":
            # Low confidence / Keyword match -> Show unobtrusive Toast
            # We don't block the screen, just warn.
            title = i18n.get_text("toast_phishing_title")
            message = i18n.get_text("toast_phishing_body")
            
            # Use the new generic friendly message, ignore the raw detail
            toast = ToastNotification(title, message)
            toast.show_toast()
            
            # We must store reference to prevent garbage collection?
            # Toast auto-closes but if garbage collected instantly it might disappear.
            self.last_toast = toast 
            return

        elif threat_type == "RAT_DOWNLOAD_WARNING":
            title = i18n.get_text("toast_rat_download_title")
            message = i18n.get_text("toast_rat_download_body")

            toast = ToastNotification(title, message)
            toast.show_toast()
            self.last_toast = toast
            return

        # Send Email Alert (Async) if Critical
        if "BANKING_RISK" in threat_type or "PHISHING_CRITICAL" in threat_type:
            threading.Thread(target=send_alert_email, args=(threat_type, details), daemon=True).start()

        # Log and Screenshot before showing the Red Screen
        self.log_and_screenshot(threat_type, details)

        # Show the Red Screen (Critical)
        self.current_alert = AlertWindow(threat_type, details, pid)
        self.current_alert.action_taken.connect(lambda action: self.handle_alert_action(action, pid))
        self.current_alert.show()

    def log_and_screenshot(self, threat_type, details):
        """Creates a screenshot and saves a log entry to data/logs."""
        try:
            # Running as compiled exe or source
            if getattr(sys, 'frozen', False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            logs_dir = os.path.join(base_dir, 'data', 'logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = os.path.join(logs_dir, "threats.log")

            # Write text log
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] TYPE: {threat_type} | DETAILS: {details}\n")

            # Take Screenshot
            screen = self.app.primaryScreen()
            if screen:
                screenshot = screen.grabWindow(0)
                img_path = os.path.join(logs_dir, f"screenshot_{timestamp}.png")
                screenshot.save(img_path, 'png')
                logger.info(f"Screenshot saved to {img_path}")

        except Exception as e:
            logger.error(f"Failed to log/screenshot threat: {e}")

    def check_clipboard(self):
        try:
            text = self.clipboard.text().lower()
            if not text:
                return

            # Check for suspicious strings often used by scammers to copy-paste into cmd/powershell
            suspicious_keywords = ["powershell", "certutil", "invoke-webrequest", "iex(", "wscript", "cscript"]

            for keyword in suspicious_keywords:
                if keyword in text:
                    logger.warning(f"Suspicious clipboard content detected and cleared: {text[:50]}...")
                    self.clipboard.clear()

                    # Show toast warning
                    title = "⚠️ Appunti Sospetti / Suspicious Clipboard"
                    message = "Un comando potenzialmente pericoloso è stato rimosso dagli appunti.\nA potentially dangerous command was removed from the clipboard."
                    toast = ToastNotification(title, message)
                    toast.show_toast()
                    self.last_toast = toast
                    break
        except Exception as e:
            logger.error(f"Error checking clipboard: {e}")

    def execute_panic_mode(self):
        """Silently and aggressively kills all known browsers and remote control software."""
        logger.warning("PANIC MODE ACTIVATED via hotkey! Killing browsers and RATs...")

        import psutil

        target_processes = [
            # Browsers
            "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe", "iexplore.exe",
            # RATs
            "teamviewer.exe", "anydesk.exe", "tv_w32.exe", "tv_x64.exe",
            "supremo.exe", "logmein.exe", "vncviewer.exe", "screenconnect.windowsclient.exe",
            "lmi_rescue.exe", "zohoassist.exe", "splashtop.exe", "rustdesk.exe",
            "ultraviewer.exe", "ammyy.exe", "alpemix.exe", "showmypc.exe", "mikogo.exe"
        ]

        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                if proc_name and proc_name.lower() in target_processes:
                    proc.kill()
                    killed_count += 1
                    logger.info(f"Panic Mode killed: {proc_name} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        logger.info(f"Panic Mode finished. Killed {killed_count} processes.")

    def handle_alert_action(self, action, pid):
        if action == "IGNORE":
            # Check if this was a Phishing alert that the user acknowledged
            if self.current_alert and "PHISHING" in self.current_alert.threat_type:
                 # Snooze phishing detection for 20 seconds to give user time to close tab
                 self.monitor.snooze_phishing(20)
            
            logger.info(f"User ignored threat for PID {pid}")
            self.monitor.add_ignored_pid(pid)
        
        elif action == "BLOCK":
            # User chose to block (kill) the process.
            # We add it to ignore list immediately to prevent the background monitor 
            # from detecting it again while it is terminating (race condition).
            logger.info(f"User blocked threat for PID {pid}. Adding to ignore list during termination.")
            self.monitor.add_ignored_pid(pid)
            
            # Global pause to prevent alert loops while system cleans up
            self.monitor.pause_scanning(10)


    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    monitor_app = ElderlyMonitorApp()
    monitor_app.run()
