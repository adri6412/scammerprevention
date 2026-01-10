from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                               QLineEdit, QPushButton, QHBoxLayout, QMessageBox,
                               QComboBox, QCheckBox, QGroupBox)
from PySide6.QtCore import Qt
import os
import json
import requests
from src.utils import i18n, startup

SETTINGS_FILE = 'settings.json' 
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, 'data')
SETTINGS_PATH = os.path.join(DATA_DIR, 'settings.json')

class SettingsWindow(QWidget):
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.load_settings()
        self.init_ui()

    def load_settings(self):
        self.urls = []
        self.current_lang = "it" # Default
        self.startup_enabled = False

        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, 'r') as f:
                    data = json.load(f)
                    self.urls = data.get('update_urls', [])
                    self.current_lang = data.get('language', 'it')
                    # Startup state is truth from Registry, but we might store expectation? 
                    # Actually better to read from Registry directly for the checkbox state.
            except:
                pass
        
        # Sync I18n
        i18n.set_language(self.current_lang)
        
        # Check actual registry state
        self.startup_enabled = startup.is_autorun_enabled()

    def init_ui(self):
        self.setWindowTitle(i18n.get_text("settings_title"))
        self.setGeometry(300, 300, 500, 500)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # --- General Settings Group ---
        grp_gen = QGroupBox(i18n.get_text("grp_general"))
        gen_layout = QVBoxLayout()
        
        # Language
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(i18n.get_text("lbl_language")))
        self.combo_lang = QComboBox()
        self.combo_lang.addItem("Italiano", "it")
        self.combo_lang.addItem("English", "en")
        # Select current
        index = self.combo_lang.findData(self.current_lang)
        if index >= 0:
            self.combo_lang.setCurrentIndex(index)
        self.combo_lang.currentIndexChanged.connect(self.on_lang_changed)
        lang_layout.addWidget(self.combo_lang)
        gen_layout.addLayout(lang_layout)
        
        # Startup
        self.chk_startup = QCheckBox(i18n.get_text("chk_startup"))
        self.chk_startup.setChecked(self.startup_enabled)
        self.chk_startup.stateChanged.connect(self.on_startup_changed)
        gen_layout.addWidget(self.chk_startup)
        
        grp_gen.setLayout(gen_layout)
        layout.addWidget(grp_gen)

        layout.addSpacing(10)

        # --- Rules Group --- (Existing Logic)
        layout.addWidget(QLabel(i18n.get_text("lbl_manrules")))
        
        # List of URLs
        self.url_list = QListWidget()
        self.url_list.addItems(self.urls)
        layout.addWidget(self.url_list)
        
        # Remove Button
        btn_remove = QPushButton(i18n.get_text("btn_remove_url"))
        btn_remove.clicked.connect(self.remove_url)
        layout.addWidget(btn_remove)

        # Add URL Section
        add_layout = QHBoxLayout()
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("https://.../rules.json OR .txt / .lst")
        add_layout.addWidget(self.input_url)
        
        btn_add = QPushButton(i18n.get_text("btn_add_url"))
        btn_add.clicked.connect(self.add_url)
        add_layout.addWidget(btn_add)
        
        layout.addLayout(add_layout)
        
        layout.addSpacing(20)
        
        # Update Now Button
        self.btn_update = QPushButton(i18n.get_text("btn_update"))
        self.btn_update.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.btn_update.setCursor(Qt.PointingHandCursor)
        self.btn_update.clicked.connect(self.run_update)
        layout.addWidget(self.btn_update)
        
        # Status Label
        self.lbl_status = QLabel(i18n.get_text("status_ready"))
        layout.addWidget(self.lbl_status)

    def on_startup_changed(self, state):
        is_checked = (state == Qt.Checked.value) # PySide6 enum or int
        # Actually state is int. 2 is Checked.
        if isinstance(state, int):
            is_checked = (state == 2)
        
        success = startup.set_autorun(is_checked)
        if not success:
            QMessageBox.warning(self, "Error", "Failed to update registry. Try running as Administrator.")
            # Revert checkbox if failed?
            # self.chk_startup.setChecked(not is_checked) 

    def on_lang_changed(self, index):
        code = self.combo_lang.currentData()
        self.current_lang = code
        i18n.set_language(code)
        self.save_urls() # Save settings
        # Trigger UI refresh? For now, user needs to restart or reopen settings.
        # We can implement a restart prompt.
        QMessageBox.information(self, "Language Changed", "Please restart the application for all changes to take effect.\nRiavvia l'applicazione per applicare le modifiche.")

    def load_urls(self):
        # Deprecated logic, moved to load_settings, but keeping signature if needed or removing
        pass 

    def save_urls(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        data = {
            'update_urls': self.urls,
            'language': self.current_lang
        }
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
        self.lbl_status.setText(i18n.get_text("status_updating"))
        self.btn_update.setEnabled(False)
        self.repaint() # Force refresh
        
        count_success = 0
        total_rules_merged = 0
        
        for url in self.urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    try:
                        # Try parsing as JSON (Standard Format)
                        new_rules = response.json()
                        
                        # Merge Logic for JSON
                        for key in self.detector.rules:
                            if key in new_rules and isinstance(new_rules[key], list):
                                before = len(self.detector.rules[key])
                                current_set = set(self.detector.rules[key])
                                new_items = set(new_rules[key])
                                self.detector.rules[key] = list(current_set.union(new_items))
                                
                                total_rules_merged += (len(self.detector.rules[key]) - before)
                                
                    except ValueError:
                        # Fallback: Parse as raw text list (Phishing Domains)
                        # Assumes line-separated domains
                        print(f"JSON parse failed for {url}, trying as text list...")
                        content = response.text
                        domains = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]
                        
                        if domains:
                            target_key = "phishing_domains"
                            # Ensure key exists
                            if target_key not in self.detector.rules:
                                self.detector.rules[target_key] = []
                            
                            before = len(self.detector.rules[target_key])
                            current_set = set(self.detector.rules[target_key])
                            current_set.update(domains)
                            self.detector.rules[target_key] = list(current_set)
                            
                            added = len(self.detector.rules[target_key]) - before
                            total_rules_merged += added
                            print(f"Merged {added} new domains from text list.")

                    count_success += 1
                else:
                    print(f"Failed to fetch {url}: {response.status_code}")
            except Exception as e:
                print(f"Error updating from {url}: {e}")
        
        # Save merged rules to disk
        self.detector.save_rules()
        self.detector.load_rules() # Reload to be sure
        
        self.lbl_status.setText(i18n.get_text("status_done", success=count_success, total=len(self.urls), merged=total_rules_merged))
        self.btn_update.setEnabled(True)
        QMessageBox.information(self, "Update Complete", i18n.get_text("msg_update_success", count=count_success))
