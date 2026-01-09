from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                               QLineEdit, QPushButton, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt
import os
import json
import requests

SETTINGS_FILE = 'settings.json' # Saved in src/data implied, handled by main/detector paths mostly. 
# We'll use absolute path relative to this file to be safe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')

class SettingsWindow(QWidget):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.setWindowTitle("Settings - ElderlyMonitor Update Manager")
        self.setGeometry(300, 300, 500, 400)
        
        self.urls = self.load_urls()
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        layout.addWidget(QLabel("Manage Protection Rule Sources (JSON URLs)"))
        
        # List of URLs
        self.url_list = QListWidget()
        self.url_list.addItems(self.urls)
        layout.addWidget(self.url_list)
        
        # Remove Button
        btn_remove = QPushButton("Remove Selected URL")
        btn_remove.clicked.connect(self.remove_url)
        layout.addWidget(btn_remove)

        # Add URL Section
        add_layout = QHBoxLayout()
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://example.com/scam_rules.json")
        add_layout.addWidget(self.input_url)
        
        btn_add = QPushButton("Add URL")
        btn_add.clicked.connect(self.add_url)
        add_layout.addWidget(btn_add)
        
        layout.addLayout(add_layout)
        
        layout.addSpacing(20)
        
        # Update Now Button
        self.btn_update = QPushButton("⚡ DOWNLOAD & UPDATE RULES NOW")
        self.btn_update.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self.run_update)
        layout.addWidget(self.btn_update)
        
        # Status Label
        self.lbl_status = QLabel("Ready.")
        layout.addWidget(self.lbl_status)

    def load_urls(self):
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                    return data.get('update_urls', [])
            except:
                pass
        return []

    def save_urls(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        data = {'update_urls': self.urls}
        try:
            with open(SETTINGS_PATH, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def add_url(self):
        url = self.input_url.text().strip()
        if url:
            if url not in self.urls:
                self.urls.append(url)
                self.url_list.addItem(url)
                self.save_urls()
                self.input_url.clear()

    def remove_url(self):
        row = self.url_list.currentRow()
        if row >= 0:
            self.urls.pop(row)
            self.url_list.takeItem(row)
            self.save_urls()

    def run_update(self):
        self.lbl_status.setText("Updating... please wait.")
        self.btn_update.setEnabled(False)
        self.repaint() # Force refresh
        
        count_success = 0
        total_rules_merged = 0
        
        for url in self.urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    new_rules = response.json()
                    
                    # Merge Logic
                    # We expect keys: "rats", "banking_keywords", "suspicious_cmds"
                    for key in self.detector.rules:
                        if key in new_rules and isinstance(new_rules[key], list):
                            before = len(self.detector.rules[key])
                            # Union
                            current_set = set(self.detector.rules[key])
                            new_items = set(new_rules[key])
                            self.detector.rules[key] = list(current_set.union(new_items))
                            
                            total_rules_merged += (len(self.detector.rules[key]) - before)
                    
                    count_success += 1
                else:
                    print(f"Failed to fetch {url}: {response.status_code}")
            except Exception as e:
                print(f"Error updating from {url}: {e}")
        
        # Save merged rules to disk
        self.detector.save_rules()
        self.detector.load_rules() # Reload to be sure
        
        self.lbl_status.setText(f"Update Finished. Success: {count_success}/{len(self.urls)}. New Rules: {total_rules_merged}")
        self.btn_update.setEnabled(True)
        QMessageBox.information(self, "Update Complete", f"Successfully updated rules from {count_success} sources.")
