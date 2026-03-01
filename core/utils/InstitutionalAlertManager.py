"""
💎 Institutional Alert Manager
Handles high-priority notifications via Email and WhatsApp/Telegram.
Target: +91 9172645866 | warghade2012@gmail.com
"""

import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

class InstitutionalAlertManager:
    def __init__(self):
        self.user_mobile = "+919172645866"
        self.user_email = "warghade2012@gmail.com"
        self.sender_email = os.environ.get("SENDER_EMAIL", "genesis.alerts@gmail.com")
        self.smtp_pass = os.environ.get("SMTP_PASSWORD", "")
        
    def send_email_alert(self, subject, body):
        """Sends a professional-grade HTML email report."""
        if not self.smtp_pass:
            print(f"[PREVIEW ONLY] Email to {self.user_email}: {subject}")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.user_email
            msg['Subject'] = f"💎 GENESIS SYSTEM3: {subject}"

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.smtp_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Email Failed: {e}")
            return False

    def send_whatsapp_alert(self, message):
        """
        Placeholder for WhatsApp API (Twilio/Interakt).
        For now, logs to a high-priority alert file for the dashboard to pick up.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        alert_msg = f"[WHATSAPP TO {self.user_mobile}] [{timestamp}] {message}"
        print(alert_msg)
        
        # Log to a dedicated mobile_alerts.jsonl for dashboard visibility
        log_path = Path("logs/mobile_alerts.jsonl")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps({"ts": timestamp, "to": self.user_mobile, "msg": message}) + "
")

    def send_alpha_report(self, predictions):
        """Formats and sends the Top 5 Alpha report."""
        header = "🚀 TODAY'S TOP 5 AI ALPHA SELECTIONS"
        body = f"Hello, the Genesis AI has identified the following high-conviction opportunities:

"
        
        html_body = "<h2>🚀 Genesis AI: Morning Alpha Report</h2><table border='1'><tr><th>Symbol</th><th>Confidence</th><th>Target</th></tr>"
        
        for p in predictions:
            row = f"✅ {p['symbol']} {p['contract']} | Conf: {p['confidence']}% | Target: {p['profit_target']}
"
            body += row
            html_body += f"<tr><td>{p['symbol']}</td><td>{p['confidence']}%</td><td>{p['profit_target']}</td></tr>"
        
        html_body += "</table><p>Sent via Genesis Autonomous Brain.</p>"
        
        # Send both
        self.send_whatsapp_alert(body)
        self.send_email_alert("Morning Alpha Report", html_body)

# Global Instance
alert_manager = InstitutionalAlertManager()
