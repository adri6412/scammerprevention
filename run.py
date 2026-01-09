import sys
import os

# Add the project root (current directory) to sys.path
# This ensures that 'import src.core...' works correctly whether running as script or frozen exe.
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.main import ElderlyMonitorApp

if __name__ == "__main__":
    monitor_app = ElderlyMonitorApp()
    monitor_app.run()
