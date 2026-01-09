# ElderlyMonitor - Anti-Scam Protection Framework

**ElderlyMonitor** is a Windows-based specialized security utility designed to protect non-technical users (elderly, inexperienced) from "Tech Support Scams". 
It sits in the system tray and monitors for suspicious behaviors typical of scammers, such as the usage of Remote Access Tools (RATs) combined with Banking activities, or the execution of fake "hacker" commands in the terminal.

## 🚀 Key Features

*   **Remote Tool Detection**: Identifies usage of AnyDesk, TeamViewer, UltraViewer, RustDesk, and 15+ other remote control software.
*   **Context-Aware Banking Protection**: triggering a **CRITICAL RED ALERT** if a Banking Website is opened while a Remote Tool is active.
*   **Fake Site Protection (Anti-Phishing)**: Detects if you are visiting a suspicious "Login" or "Banking" site that is not in the safe list (e.g., fake PayPal/Bank logins).
*   **Voice Alerts (TTS)**: Uses Windows built-in voice to loudly warn the user ("Security Alert!").
*   **Multilingual Support**: Fully localized in **English** and **Italian**.
*   **Scam Pattern Recognition**: Detects usage of command-line tools used to fake infections (e.g., `tree`, `netstat`, `cipher`).
*   **Educational Warnings**: The alert screen provides clear, large-text warnings.
*   **Remote Updates**: Supports fetching new detection rules (JSON) from remote URLs.
*   **Auto-Start**: Option to automatically start on Windows boot (via Settings).

## 📦 Installation

### Prerequisites
- Windows 10 or 11
- Python 3.10+ (if running from source)

### Quick Start (Pre-packaged)
1.  Download the repository.
2.  Double-click **`install_and_run.bat`**.
    - This script automatically installs dependencies (`PySide6`, `psutil`, `pywin32`, `requests`) and starts the monitor.
3.  The application will appear in the System Tray (bottom right).

## 📦 Installation & Download

### Option 1: Download Pre-built EXE (Recommended)
1.  Go to the **[Releases](https://github.com/adri6412/scammerprevention/releases)** page.
2.  Download `ElderlyMonitor.exe`.
3.  Place it anywhere (e.g., Desktop) and run it.
4.  It will create a `data/` folder next to itself to store your update rules.

### Option 2: Run from Source
1.  Clone this repository.
2.  Run `install_and_run.bat`.

## ⚙️ Configuration & Rules

The detection logic is data-driven.
- **First Run**: The app creates a default `rules.json` in the `data/` folder.
- **Updates**: Use the "Settings" menu in the Tray Icon to download updated rules from the web.

### Rule Format (`rules.json`)
```json
{
    "rats": [
        "AnyDesk.exe",
        "TeamViewer.exe",
        "Supremo.exe"
    ],
    "banking_keywords": [
        "banca",
        "intesa",
        "paypal",
        "refund"
    ],
    "suspicious_cmds": [
        "tree.*",
        "netstat.*",
        "cipher /w"
    ]
}
```

### Remote Updates
1.  Right-click the System Tray icon -> **Settings / Update Rules**.
2.  Add a URL pointing to a raw JSON file (e.g., GitHub Raw).
3.  Click **"Download & Update Rules Now"**.
4.  The system merges the new rules with your local database.

## 🛠️ Development

### Directory Structure
```
c:\Users\adri6\ElderlyMonitor\
├── src\
│   ├── main.py                 # Application Entry Point & Tray
│   ├── core\
│   │   ├── monitor.py          # Background Thread (psutil scanner)
│   │   └── detector.py         # Heuristics Engine (Rule matcher)
│   ├── ui\
│   │   ├── alert_window.py     # Full-Screen Warning Interface
│   │   └── settings.py         # Update Manager UI
│   └── data\
│       └── rules.json          # Detection Database
├── tests\
│   └── simulate_attack.py      # Safe Simulation Script
├── install_and_run.bat         # User Launcher
└── requirements.txt            # Python Dependencies
```

### Dependencies
```bash
pip install -r requirements.txt
```

## ⚠️ Disclaimer
This software is a **preventative measure**. It relies on heuristics (process names, window titles) and does not perform kernel-level inspection or antivirus scanning. It is designed to stop *social engineering* attacks, not sophisticated malware.
Always ensure the user has a proper Antivirus installed.
