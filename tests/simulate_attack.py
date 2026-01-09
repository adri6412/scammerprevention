import sys
import os
import shutil
import subprocess
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class FakeBankSite(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Intesa Sanpaolo - Login - Bank Transfer")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        label = QLabel("THIS IS A FAKE BANKING SITE FOR TESTING")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

def create_fake_rat():
    """Create a dummy executable named 'AnyDesk.exe' to trigger the detector."""
    target_name = "AnyDesk.exe"
    
    # Use ping.exe as the base host because it's standalone and robust
    system32 = os.path.join(os.environ['SystemRoot'], 'System32')
    source_exe = os.path.join(system32, "ping.exe")

    if not os.path.exists(target_name):
        print(f"Creating fake RAT: {target_name} (Copy of {source_exe})")
        try:
            shutil.copy(source_exe, target_name)
        except Exception as e:
            print(f"Failed to copy exe: {e}")
            return None
    
    print(f"Launching {target_name}...")
    # Run: AnyDesk.exe 127.0.0.1 -n 60 (Run for ~60 seconds)
    return subprocess.Popen([os.path.abspath(target_name), "127.0.0.1", "-n", "60"], stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    print("--- SCAM SIMULATION STARTED ---")
    
    # 1. Launch Fake RAT
    rat_process = create_fake_rat()
    print(f"Fake RAT started with PID: {rat_process.pid}")

    # 2. Open Fake Bank Site
    print("Opening Fake Banking Window...")
    window = FakeBankSite()
    window.show()

    print("\nEXPECTATION: The ElderlyMonitor should detect 'AnyDesk.exe' AND 'Bank' title.")
    print("It should show the RED ALERT screen.")
    print("If you click BLOCK, this fake AnyDesk process should be killed.")

    try:
        sys.exit(app.exec())
    finally:
        # Cleanup
        if rat_process.poll() is None:
            rat_process.kill()
        if os.path.exists("AnyDesk.exe"):
            try:
                os.remove("AnyDesk.exe")
            except:
                pass
