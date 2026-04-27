import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.logger import logger
import json
import os
import sys

def get_settings_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, 'data', 'settings.json')

def send_alert_email(threat_type, details):
    """Sends an email alert if SMTP is configured in settings."""
    settings_path = get_settings_path()
    if not os.path.exists(settings_path):
        return

    try:
        with open(settings_path, 'r') as f:
            data = json.load(f)
            smtp_config = data.get('smtp')

            if not smtp_config or not smtp_config.get('enabled'):
                return

            server = smtp_config.get('server')
            port = smtp_config.get('port', 587)
            user = smtp_config.get('user')
            password = smtp_config.get('password')
            recipient = smtp_config.get('recipient')

            if not all([server, port, user, password, recipient]):
                logger.warning("SMTP config incomplete, not sending email.")
                return

            msg = MIMEMultipart()
            msg['From'] = user
            msg['To'] = recipient
            msg['Subject'] = f"ElderlyMonitor Alert: {threat_type}"

            body = f"ElderlyMonitor detected a critical threat.\n\nType: {threat_type}\nDetails: {details}\n\nPlease check on the user immediately."
            msg.attach(MIMEText(body, 'plain'))

            # Use SSL/TLS
            if port == 465:
                smtp = smtplib.SMTP_SSL(server, port)
                smtp.login(user, password)
            else:
                smtp = smtplib.SMTP(server, port)
                smtp.starttls()
                smtp.login(user, password)

            smtp.send_message(msg)
            smtp.quit()
            logger.info(f"Alert email sent to {recipient}")

    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
