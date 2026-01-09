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
        "alert_bank_tips": "We detected a Remote Tool accessing your Bank.\nThis is ALWAYS a SCAM. BLOCK IT NOW.",
        "alert_details": "Details: {details}",
        "alert_question": "Is someone unexpected trying to control your computer?",
        "btn_block": "⛔ BLOCK CONNECTION (Recommended)",
        "btn_ignore": "I am doing this myself (Ignore)",
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
        "tts_alert": "Security Alert! Do not close this window. Potential scam detected."
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
        "alert_bank_tips": "Rilevato strumento remoto sul sito della Banca.\nÈ QUASI CERTAMENTE UNA TRUFFA. BLOCCA ORA.",
        "alert_details": "Dettagli: {details}",
        "alert_question": "Qualcuno sta controllando il tuo computer?",
        "btn_block": "⛔ BLOCCA CONNESSIONE (Consigliato)",
        "btn_ignore": "Sto operando io (Ignora)",
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
        "tts_alert": "Attenzione! Avviso di sicurezza. Possibile truffa in corso. Non chiudere questa finestra."
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
