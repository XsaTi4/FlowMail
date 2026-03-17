import webview
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import time
import threading
from email_validator import validate_email, EmailNotValidError

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
TEMPLATE_FILE = os.path.join(DATA_DIR, 'template.html')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class Api:
    def __init__(self):
        self.sending = False
        self.total_emails = 0
        self.sent_emails = 0
        self.failed_emails = 0
        
    def get_settings(self):
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        return {"smtp_server": "", "smtp_port": "587", "smtp_user": "", "smtp_password": "", "from_email": "", "from_name": "", "delay": 1.0}

    def save_settings(self, settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return {"success": True, "message": "Settings saved successfully."}

    def save_template(self, html):
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        return {"success": True, "message": "Template saved successfully."}

    def get_template(self):
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_preset_templates(self):
        templates_dir = os.path.join(DATA_DIR, 'templates')
        templates = []
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(templates_dir, filename), 'r') as f:
                            templates.append(json.load(f))
                    except Exception:
                        pass
        return templates

    def parse_file(self, filepath):
        try:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                return {"success": False, "message": "Unsupported file format."}

            # Find all emails across all columns
            emails = []
            for col in df.columns:
                # Convert column to string
                col_data = df[col].astype(str)
                # Find valid emails using basic regex first to extract
                extracted = col_data.str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})').dropna()
                for email_candidate in extracted[0]:
                    try:
                        valid = validate_email(email_candidate)
                        emails.append(valid.email)
                    except EmailNotValidError:
                        continue
            
            emails = list(set(emails)) # Unique emails
            return {"success": True, "emails": emails, "count": len(emails)}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def select_file(self):
        file_types = ('CSV Files (*.csv)', 'Excel Files (*.xlsx)')
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and len(result) > 0:
            return self.parse_file(result[0])
        return {"success": False, "message": "No file selected."}
        
    def start_sending(self, emails, subject, mode="template", plain_text=""):
        if self.sending:
            return {"success": False, "message": "Already sending emails."}
            
        settings = self.get_settings()
        template = self.get_template()
        
        if not settings.get("smtp_server") or not settings.get("smtp_user"):
            return {"success": False, "message": "SMTP settings are incomplete."}
        if mode == "template" and not template:
            return {"success": False, "message": "Email template is empty."}
        if mode == "text" and not plain_text.strip():
            return {"success": False, "message": "Plain text is empty."}
        if not emails:
            return {"success": False, "message": "No recipients provided."}
            
        self.sending = True
        self.total_emails = len(emails)
        self.sent_emails = 0
        self.failed_emails = 0
        
        thread = threading.Thread(target=self._send_loop, args=(emails, subject, settings, template, mode, plain_text))
        thread.daemon = True
        thread.start()
        
        return {"success": True, "message": "Sending started."}
        
    def stop_sending(self):
        self.sending = False
        return {"success": True, "message": "Sending stopped."}
        
    def get_progress(self):
        return {
            "sending": self.sending,
            "total": self.total_emails,
            "sent": self.sent_emails,
            "failed": self.failed_emails
        }

    def _send_loop(self, emails, subject, settings, template, mode, plain_text):
        try:
            server = smtplib.SMTP(settings["smtp_server"], int(settings["smtp_port"]))
            server.starttls()
            server.login(settings["smtp_user"], settings["smtp_password"])
            
            delay = float(settings.get("delay", 1.0))
            from_addr = f'{settings.get("from_name", "")} <{settings["from_email"]}>' if settings.get("from_name") else settings["from_email"]
            
            for email in emails:
                if not self.sending:
                    break
                    
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = subject
                    msg['From'] = from_addr
                    msg['To'] = email
                    
                    if mode == "template":
                        part = MIMEText(template, 'html')
                    else:
                        part = MIMEText(plain_text, 'plain')
                        
                    msg.attach(part)
                    
                    server.send_message(msg)
                    self.sent_emails += 1
                except Exception as e:
                    print(f"Failed to send to {email}: {e}")
                    self.failed_emails += 1
                
                if delay > 0:
                    time.sleep(delay)
                    
            server.quit()
        except Exception as e:
            print(f"SMTP Error: {e}")
        finally:
            self.sending = False

if __name__ == '__main__':
    api = Api()
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'index.html')
    window = webview.create_window('Email Sender application', html_path, js_api=api, width=1280, height=800, text_select=True)
    webview.start(debug=True)
