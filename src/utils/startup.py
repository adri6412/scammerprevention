import winreg
import sys
import os

APP_NAME = "ElderlyMonitor"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def get_app_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        # If running from source, we might want to run via pythonw or bat?
        # For simplicity in source mode, we point to the python executable running the script
        # BUT this is tricky. Let's assume for source dev we might skip or point to the .bat if possible.
        # Actually, best implementation for source is pointing to install_and_run.bat or python executable.
        # Let's point to sys.executable + " " + script path
        script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'run.py')
        return f'"{sys.executable}" "{os.path.abspath(script)}"'

def is_autorun_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error checking autorun: {e}")
        return False

def set_autorun(enabled):
    path = get_app_path()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_WRITE)
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, path)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass # Already deleted
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error setting autorun: {e}")
        return False
