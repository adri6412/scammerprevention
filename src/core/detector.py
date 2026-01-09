import re
import json
import os
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
RULES_FILE = os.path.join(DATA_DIR, 'rules.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')

class Detector:
    def __init__(self):
        self.ensure_data_dir()
        
        # Default Hardcoded Rules (Fallback)
        self.rules = {
            "rats": [
                'TeamViewer.exe', 'AnyDesk.exe', 'tv_w32.exe', 'tv_x64.exe',
                'Supremo.exe', 'LogMeIn.exe', 'vncviewer.exe', 'hstart.exe',
                'screenconnect.windowsclient.exe', 'lmi_rescue.exe', 'zohoassist.exe',
                'splashtop.exe', 'rustdesk.exe', 'ultraviewer.exe', 'ammyy.exe',
                'alpemix.exe', 'showmypc.exe', 'mikogo.exe'
            ],
            "banking_keywords": [
                'bank', 'banca', 'banque', 'banco',
                'login', 'accedi', 'sign in', 'log in',
                'account', 'conto', 'cuenta', 'compte',
                'transfer', 'bonifico', 'wire',
                'paypal', 'stripe', 'wise', 'revolut',
                'intesa', 'unicredit', 'poste', 'chase', 'fargo', 'citibank', 'hsbc',
                'barclays', 'lloyds', 'natwest', 'american express'
            ],
            "suspicious_cmds": [
                r'tree.*', r'dir\s*/s', r'netstat.*', 
                r'eventvwr', r'assoc', r'syskey'
            ]
        }
        
        # Load local overrides if they exist
        self.load_rules()

    def ensure_data_dir(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    def load_rules(self):
        """Load rules from JSON file, merging with defaults."""
        if os.path.exists(RULES_FILE):
            try:
                with open(RULES_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Simple merge: replace keys if they exist, extend lists?
                    # For security/simplicity: If JSON exists, it OVERWRITES the categorization 
                    # specific to that key, OR we can union. 
                    # Let's do Union to be safe (Hardcoded + Downloaded).
                    for key in self.rules:
                        if key in loaded:
                            # Union of unique items
                            current_set = set(self.rules[key])
                            new_items = set(loaded[key])
                            self.rules[key] = list(current_set.union(new_items))
                    print("Rules loaded and merged from rules.json")
            except Exception as e:
                print(f"Failed to load rules.json: {e}")

    def save_rules(self):
        """Save current rules to disk."""
        try:
            with open(RULES_FILE, 'w') as f:
                json.dump(self.rules, f, indent=4)
        except Exception as e:
            print(f"Failed to save rules: {e}")

    def is_rat(self, process_name):
        """Check if the process name is on the blacklist."""
        return process_name.lower() in [r.lower() for r in self.rules['rats']]

    def is_banking_window(self, window_title):
        """Check if the window title suggests banking activity."""
        if not window_title:
            return False
        title_lower = window_title.lower()
        for kw in self.rules['banking_keywords']:
            if kw in title_lower:
                return True
        return False

    def is_suspicious_command(self, cmdline):
        """Check if a command line string matches known scam patterns."""
        if not cmdline:
            return False
        if isinstance(cmdline, list):
            cmd_str = ' '.join(cmdline).lower()
        else:
            cmd_str = cmdline.lower()

        for pattern in self.rules['suspicious_cmds']:
            if re.search(pattern, cmd_str):
                return True
        return False
