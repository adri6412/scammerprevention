import uiautomation as auto
import Levenshtein
from urllib.parse import urlparse
from src.utils.logger import logger

class PhishingDetector:
    def __init__(self):
        self.whitelist = set()
        self.blocklist = set()
        self.keywords = []
        # Cache control patterns
        self.browsers = {
            "chrome.exe": "Address and search bar",
            "msedge.exe": "Address and search bar", # Edge might be different depending on version
            "firefox.exe": "Search with Google or enter address", # Firefox automation id is usually 'urlbar-input'
        }

    def load_rules(self, rules_data):
        """Load lists from the main rules dictionary."""
        self.whitelist = set(rules_data.get("safe_domains", []))
        self.blocklist = set(rules_data.get("phishing_domains", []))
        self.keywords = rules_data.get("phishing_keywords", [])

    def get_browser_url(self):
        """
        Attempts to get the URL from the foreground window if it's a browser.
        Returns: str (URL) or None
        """
        try:
            window = auto.GetForegroundControl()
            if not window:
                return None
            
            pid = window.ProcessId
            try:
                import psutil
                process = psutil.Process(pid)
                proc_name = process.name().lower()
            except:
                return None

            if proc_name not in self.browsers:
                return None

            # Optimization: Look for Edit control directly
            # This is a basic implementation. Browsers update UI often, so this might need robust finding.
            # Chrome/Edge usually have name 'Address and search bar' or ControlType=Edit
            
            # fast search for Edit control
            address_bar = window.EditControl(searchDepth=4, Name=self.browsers.get(proc_name))
            if not address_bar.Exists(0, 0):
                # Fallback: search any edit control that looks like a URL
                # Firefox uses 'Page Address' or similar sometimes
                address_bar = window.EditControl(searchDepth=5) 
            
            if address_bar.Exists(0, 0):
                url_value = address_bar.GetValuePattern().Value
                # Clean up: browsers sometimes show "Search google for..." or empty
                if "." in url_value and " " not in url_value:
                    if not url_value.startswith("http"):
                        url_value = "https://" + url_value
                    return url_value
            
            return None

        except Exception as e:
            # logger.debug(f"UI Automation error: {e}")
            return None

    def check_url(self, url):
        """
        Analyze the URL.
        Returns: (SAFE|PHISHING|SUSPICIOUS, Reason)
        """
        if not url:
            return "SAFE", None

        try:
            domain = urlparse(url).netloc.lower()
            # Remove www.
            if domain.startswith("www."):
                domain = domain[4:]
        except:
            return "SAFE", None # Parse error

        # 1. Blocklist
        if domain in self.blocklist:
            return "PHISHING", f"Known Dangerous Domain: {domain}"
        
        # 2. Whitelist
        # Check exact match or subdomain
        if domain in self.whitelist:
            return "SAFE", None
        for safe in self.whitelist:
            if domain.endswith("." + safe): # e.g. mail.google.com ends with .google.com
                return "SAFE", None

        # 3. Heuristics
        # A. Keywords in domain
        found_kw = next((kw for kw in self.keywords if kw in domain), None)
        
        # B. Levenshtein (Typosquatting against whitelist)
        # Only check if we found a keyword OR if it looks like a bank
        # For performance, only check against whitelist if length is similar
        
        suspicion_score = 0
        reason = []

        if found_kw:
            suspicion_score += 5
            reason.append(f"Suspicious keyword '{found_kw}'")

        # Basic Check: If it contains a keyword but is NOT whitelisted -> Suspicious
        if suspicion_score > 0:
             return "SUSPICIOUS", ", ".join(reason)

        return "SAFE", None
