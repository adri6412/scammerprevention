import psutil
import time
import win32gui
import win32process
from PySide6.QtCore import QThread, Signal
from src.core.detector import Detector

class SystemMonitor(QThread):
    # Signal emitted when a threat is detected
    # Arguments: threat_type (str), details (str), process_pid (int)
    threat_detected = Signal(str, str, int)

    def __init__(self):
        super().__init__()
        self.detector = Detector()
        self.running = True
        self.monitor_interval = 2  # Seconds
        self.ignored_pids = set() # PIDs that user explicitly allowed

    def add_ignored_pid(self, pid):
        """User accepted this process, do not alert again unless context changes critically."""
        print(f"Monitor: Adding PID {pid} to ignore list.")
        self.ignored_pids.add(pid)

    def run(self):
        print("ElderlyMonitor: Background Service Started")
        while self.running:
            try:
                self.scan_processes()
                self.scan_windows()
            except Exception as e:
                print(f"Monitor Loop Error: {e}")
            
            time.sleep(self.monitor_interval)

    def stop(self):
        self.running = False

    def scan_processes(self):
        """Iterate over running processes to find RATs or suspicious commands."""
        # Using process_iter is efficient
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                p_name = proc.info['name']
                p_pid = proc.info['pid']
                p_cmd = proc.info['cmdline']

                if p_pid in self.ignored_pids:
                    continue

                # 1. Check for RATs
                if self.detector.is_rat(p_name):
                    # Found a remote tool. Logic: 
                    # If it's just running, maybe warn? 
                    # For now, we report it. The UI decides if it's a "Critical Alert" based on context (like banking).
                    # We need to know if it has active network connections to be "Active".
                    if self.has_active_connections(proc):
                        # Use a slightly less scary message if it's just the tool
                        self.threat_detected.emit("RAT_ACTIVE", f"Remote Support Tool Detected: {p_name}", p_pid)
                        # We add to ignore list immediately to prevent spamming while the UI is open? 
                        # No, the UI handles deduplication.

                # 2. Check for suspicious commands (e.g. 'tree', 'netstat')
                # We check both the process name (e.g. tree.com) and the command line arguments
                check_str = p_name
                if p_cmd:
                    check_str += " " + " ".join(p_cmd)
                
                if self.detector.is_suspicious_command(check_str):
                     self.threat_detected.emit("SCAM_CMD", f"Suspicious Command/Process: {p_name}", p_pid)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

    def scan_windows(self):
        """Check active windows for Banking keywords + Active RAT combination."""
        # This part requires cross-referencing. 
        # For simplicity in V1: If we see a Bank Window AND we recently saw a RAT, we scream.
        
        # Get foreground window title
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        
        if self.detector.is_banking_window(window_title):
            # Check if any RAT is currently running
            rats = self.get_running_rats()
            if rats:
                # CRITICAL: Banking site detected while Remote Tool is running!
                # We ALERT even if the PID was previously ignored, because the context is now dangerous (Banking).
                rat_proc = rats[0]
                rat_pid = rat_proc['pid']
                rat_name = rat_proc['name']
                
                # Check if we already alerted for this specific BANKING risk to avoid loop
                # We can use a separate "high risk" ignore logic or just rely on UI deduplication.
                # For safety, we always emit BANKING_RISK.
                self.threat_detected.emit(
                    "BANKING_RISK", 
                    f"CRITICAL: Banking site detected ('{window_title}') while {rat_name} is active!", 
                    rat_pid # Blame the first RAT
                )

    def get_running_rats(self):
        """Return a list of running RAT processes."""
        rats = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if self.detector.is_rat(proc.info['name']):
                     rats.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return rats

    def has_active_connections(self, proc):
        """Check if process has established external network connections."""
        try:
            connections = proc.connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False # Can't inspect, assume safe or handle otherwise
        return False
