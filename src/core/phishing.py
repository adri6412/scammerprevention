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
            "brave.exe": "Address and search bar",
            "opera.exe": "Address and search bar"
        }

    def load_rules(self, rules_data):
        """Load lists from the main rules dictionary."""
        self.whitelist = set(rules_data.get("safe_domains", []))
        self.blocklist = set(rules_data.get("phishing_domains", []))
        self.keywords = rules_data.get("phishing_keywords", [])
        self.rat_downloads = set(rules_data.get("rat_download_domains", []))

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

            # DEBUG: Uncomment to see what window is in focus
            # print(f"DEBUG: Focused App: {proc_name}")

            if proc_name not in self.browsers:
                return None
            
            # print(f"DEBUG: Browser Detected: {proc_name}")

            # STRATEGY: Brute-force Walk.
            # Modern browsers are complex trees. The URL bar might be an Edit, a Text, or a Custom element.
            # We walk the tree and stop at the FIRST element that contains a valid-looking URL.
            # We limit depth to avoid performance issues.
            
            found_url = None
            
            # Helper to check if string is URL
            def is_likely_url(text):
                if not text or len(text) < 4:
                    return False
                # Must have dot, no spaces (or limited spaces if it's "Search ...")
                # But we want strict URL for phishing check.
                if " " in text:
                    return False
                if "." not in text:
                    return False
                # Exclude common false positives
                if text.lower().endswith(".exe") or text.lower().endswith(".dll"):
                    return False
                return True

            count = 0
            # Walk depth 10 is usually enough to find the address bar in Chrome/Brave
            for control, depth in auto.WalkControl(window, maxDepth=10):
                count += 1
                if count > 500: # Safety break
                    break
                
                # Check ValuePattern (Editable text)
                try:
                    # Note: GetValuePattern() might throw if pattern not supported
                    # But checking properties is safer?
                    # In python uiautomation, valid controls usually expose pattern methods
                    # We try specific pattern
                    val = control.GetValuePattern().Value
                    if is_likely_url(val):
                        found_url = val
                        # print(f"DEBUG: Found URL via ValuePattern in {control.ControlTypeName}: {val}")
                        break
                except:
                    pass

                # Check Name (sometimes generic UI exposes URL as name)
                # But usually Name is "Address and search bar", not the URL itself.
                # However, for 'Text' controls (static URL display), Name IS the content.
                if is_likely_url(control.Name):
                     # Double check it's not the window title itself?
                     # Window Name is usually "Page Title - Browser Name"
                     if " - " not in control.Name:
                         found_url = control.Name
                         # print(f"DEBUG: Found URL via Name in {control.ControlTypeName}: {found_url}")
                         break
            
            if found_url:
                # Normalize
                if not found_url.startswith("http"):
                    found_url = "https://" + found_url
                return found_url

            # print(f"DEBUG: Scanned {count} controls, no URL found.")
            return None

        except Exception as e:
            print(f"DEBUG: UI Automation error: {e}")
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

        # RAT Download Check
        for rat_domain in self.rat_downloads:
            if domain == rat_domain or domain.endswith("." + rat_domain):
                return "RAT_DOWNLOAD", f"Remote Tool Download: {domain}"

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

        # Typosquatting Check against whitelist
        # We check if the domain is very similar to a whitelisted domain
        for safe_domain in self.whitelist:
            # Check length similarity first to avoid unnecessary Levenshtein distance calculations
            if abs(len(domain) - len(safe_domain)) <= 2:
                dist = Levenshtein.distance(domain, safe_domain)
                # If distance is small but not exactly 0 (which would be caught by whitelist check earlier)
                # Distance of 1 or 2 is considered typosquatting for most domains, especially short ones
                # For very short domains (e.g. g.co), we might want to be careful, but we'll use dist <= 2
                if 0 < dist <= 2:
                    suspicion_score += 10
                    reason.append(f"Typosquatting of '{safe_domain}'")
                    break

        # Basic Check: If it contains a keyword but is NOT whitelisted -> Suspicious
        if suspicion_score >= 10:
             return "PHISHING", ", ".join(reason)
        elif suspicion_score > 0:
             return "SUSPICIOUS", ", ".join(reason)

        return "SAFE", None
