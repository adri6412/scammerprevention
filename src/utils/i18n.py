import json
import os
import sys

# Constants matching settings.json structure
LANG_EN = "en"
LANG_IT = "it"

# Strings Dictionary
STRINGS = {
    "en": {
        "tray_tooltip": "ElderlyMonitor: Protected",
        "tray_settings": "Settings / Update Rules",
        "tray_exit": "Exit Monitor",
        "alert_rat_header": "SECURITY WARNING",
        "alert_rat_sub": "REMOTE ACCESS TOOL DETECTED",
        "alert_bank_header": "CRITICAL SECURITY RISK",
        "alert_bank_sub": "BANKING DATA AT RISK",
        "alert_rat_tips": (
            "HOW TO SPOT A SCAMMER:\n"
            "• A REAL technician will NEVER ask for your passwords.\n"
            "• A REAL technician will NEVER ask you to log into your bank.\n"
            "• A REAL technician will NEVER ask for Gift Cards."
        ),
        "alert_phishing_header": "FAKE WEBSITE DETECTED",
        "alert_phishing_sub": "DO NOT ENTER YOUR PASSWORD",
        "alert_phishing_tips": "This website looks suspicious and might be trying to steal your data.\nIt is NOT in your Safe List.",
        "alert_bank_tips": "We detected a Remote Tool accessing your Bank.\nThis is ALWAYS a SCAM. BLOCK IT NOW.",
        "alert_details": "Details: {details}",
        "toast_phishing_title": "ℹ️ Banking/Payment Site",
        "toast_phishing_body": "This site uses words related to security or payments.\nMany official sites use them, but paying attention is advised.",
        "toast_rat_download_title": "⚠️ Remote Tool Download",
        "toast_rat_download_body": "You are on a site to download remote control software.\nDid someone on the phone tell you to do this? Be careful!",
        "alert_question": "Is someone unexpected trying to control your computer?",
        "btn_block": "⛔ BLOCK CONNECTION (Recommended)",
        "btn_ignore": "I am doing this myself (Ignore)",
        "btn_understand": "✅ I UNDERSTAND (I will close the site)",
        "settings_title": "Settings - ElderlyMonitor",
        "lbl_manrules": "Manage Protection Rule Sources (JSON URLs)",
        "btn_remove_url": "Remove Selected URL",
        "btn_add_url": "Add URL",
        "btn_update": "⚡ DOWNLOAD & UPDATE RULES NOW",
        "status_ready": "Ready.",
        "status_updating": "Updating... please wait.",
        "status_done": "Update Finished. Success: {success}/{total}. New Rules: {merged}",
        "msg_update_success": "Successfully updated rules from {count} sources.",
        "grp_general": "General Settings",
        "lbl_language": "Language / Lingua:",
        "chk_startup": "Run automatically when Windows starts",
        "tts_alert": "Security Alert! Do not close this window. Potential scam detected.",
        "wizard_title": "ElderlyMonitor Setup",
        "wizard_welcome_title": "Welcome to ElderlyMonitor",
        "wizard_welcome_text": "ElderlyMonitor protects your computer from scams.\n\nIt monitors your system for malicious remote access tools and dangerous actions, alerting you if it detects a potential threat.\n\nLet's set it up!",
        "wizard_lang_title": "Select Language",
        "wizard_lang_text": "Please select your preferred language:",
        "wizard_rules_title": "Configure Rules URL",
        "wizard_rules_text": "ElderlyMonitor needs a rules file to detect threats.\nYou can provide a URL to download rules from.",
        "wizard_rules_placeholder": "https://.../rules.json",
        "wizard_finish_title": "Setup Complete",
        "wizard_finish_text": "ElderlyMonitor is now configured and will protect you in the background.",
        "btn_next": "Next",
        "btn_back": "Back",
        "btn_finish": "Finish"
    },
    "it": {
        "tray_tooltip": "ElderlyMonitor: Protetto",
        "tray_settings": "Impostazioni / Aggiorna Regole",
        "tray_exit": "Esci",
        "alert_rat_header": "AVVISO DI SICUREZZA",
        "alert_rat_sub": "ACCESSO REMOTO RILEVATO",
        "alert_bank_header": "RISCHIO SICUREZZA CRITICO",
        "alert_bank_sub": "DATI BANCARI A RISCHIO",
        "alert_rat_tips": (
            "COME RICONOSCERE UNA TRUFFA:\n"
            "• Un VERO tecnico non chiede MAI le tue password.\n"
            "• Un VERO tecnico non ti chiede MAI di accedere alla banca.\n"
            "• Un VERO tecnico non chiede MAI Buoni Regalo (Amazon/Google)."
        ),
        "alert_phishing_header": "SITO FALSO RILEVATO",
        "alert_phishing_sub": "NON INSERIRE PASSWORD",
        "alert_phishing_tips": "Questo sito sembra sospetto e potrebbe rubare i tuoi dati.\nNON è nella lista dei siti Sicuri.",
        "alert_bank_tips": "Rilevato strumento remoto sul sito della Banca.\nÈ QUASI CERTAMENTE UNA TRUFFA. BLOCCA ORA.",
        "alert_details": "Dettagli: {details}",
        "toast_phishing_title": "ℹ️ Sito Bancario/Pagamenti",
        "toast_phishing_body": "Questo sito usa parole relative a sicurezza o pagamenti.\nMolti siti legittimi le usano, ma presta attenzione se questo non è il tuo solito sito.",
        "toast_rat_download_title": "⚠️ Download Tool Remoto",
        "toast_rat_download_body": "Sei su un sito per scaricare software di controllo remoto.\nTe l'ha chiesto qualcuno al telefono? Fai attenzione!",
        "alert_question": "Qualcuno sta controllando il tuo computer?",
        "btn_block": "⛔ BLOCCA CONNESSIONE (Consigliato)",
        "btn_ignore": "Sto operando io (Ignora)",
        "btn_understand": "✅ HO CAPITO (Chiudo il sito)",
        "settings_title": "Impostazioni - ElderlyMonitor",
        "lbl_manrules": "Gestione Sorgenti Regole (URL JSON)",
        "btn_remove_url": "Rimuovi URL Selezionato",
        "btn_add_url": "Aggiungi URL",
        "btn_update": "⚡ SCARICA E AGGIORNA REGOLE ORA",
        "status_ready": "Pronto.",
        "status_updating": "Aggiornamento in corso...",
        "status_done": "Aggiornamento Finito. Successi: {success}/{total}. Nuove Regole: {merged}",
        "msg_update_success": "Regole aggiornate da {count} sorgenti.",
        "grp_general": "Impostazioni Generali",
        "lbl_language": "Lingua / Language:",
        "chk_startup": "Avvia automaticamente con Windows",
        "tts_alert": "Attenzione! Avviso di sicurezza. Possibile truffa in corso. Non chiudere questa finestra.",
        "wizard_title": "Configurazione ElderlyMonitor",
        "wizard_welcome_title": "Benvenuto in ElderlyMonitor",
        "wizard_welcome_text": "ElderlyMonitor protegge il tuo computer dalle truffe.\n\nMonitora il tuo sistema alla ricerca di strumenti di accesso remoto dannosi e azioni pericolose, avvisandoti se rileva una potenziale minaccia.\n\nIniziamo la configurazione!",
        "wizard_lang_title": "Seleziona Lingua",
        "wizard_lang_text": "Seleziona la tua lingua preferita:",
        "wizard_rules_title": "Configura URL Regole",
        "wizard_rules_text": "ElderlyMonitor ha bisogno di un file di regole per rilevare le minacce.\nPuoi fornire un URL per scaricare le regole.",
        "wizard_rules_placeholder": "https://.../rules.json",
        "wizard_finish_title": "Configurazione Completata",
        "wizard_finish_text": "ElderlyMonitor è ora configurato e ti proteggerà in background.",
        "btn_next": "Avanti",
        "btn_back": "Indietro",
        "btn_finish": "Fine"
    }
}

# Default language
CURRENT_LANG = "it"

def get_text(key, **kwargs):
    """Retrieve translated string formatted with kwargs."""
    global CURRENT_LANG
    lang_dict = STRINGS.get(CURRENT_LANG, STRINGS["en"])
    text = lang_dict.get(key, f"[{key}]")
    if kwargs:
        return text.format(**kwargs)
    return text

def set_language(lang_code):
    global CURRENT_LANG
    if lang_code in STRINGS:
        CURRENT_LANG = lang_code
