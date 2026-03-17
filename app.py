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
USER_TEMPLATES_FILE = os.path.join(DATA_DIR, 'user_templates.json')
STATE_FILE = os.path.join(DATA_DIR, 'state.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class Api:
    def __init__(self):
        self.sending = False
        self.paused = False
        self.total_emails = 0
        self.sent_emails = 0
        self.failed_emails = 0
        self.current_emails = []
        self.email_statuses = {}
        self.subject = ""
        self.mode = "template"
        self.plain_text = ""
        self.last_index = 0
        
    def get_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    if "jitter" not in settings:
                        settings["jitter"] = False
                    return settings
            except Exception:
                pass
        return {"smtp_server": "", "smtp_port": "587", "smtp_user": "", "smtp_password": "", "from_email": "", "from_name": "", "delay": 1.0, "jitter": False}

    def save_settings(self, settings):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return {"success": True, "message": "Settings saved successfully."}

    def save_template(self, html):
        if html is None:
            html = ""
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        return {"success": True, "message": "Template saved successfully."}

    def get_template(self):
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def get_user_templates(self):
        if os.path.exists(USER_TEMPLATES_FILE):
            try:
                with open(USER_TEMPLATES_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def save_user_template(self, name, html):
        if html is None:
            html = ""
        templates = self.get_user_templates()
        templates.append({"name": name, "html": html})
        with open(USER_TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=4)
        return {"success": True, "message": f"Template '{name}' saved to gallery."}

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
                try:
                    df = pd.read_csv(filepath)
                except Exception:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read()
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath)
            else:
                return {"success": False, "message": "Unsupported file format."}

            if 'df' in locals():
                text = df.to_string(index=False)
                
            import re
            emails = []
            extracted = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
            for email_candidate in extracted:
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
        
    def get_queue(self):
        return {
            "emails": self.current_emails,
            "statuses": self.email_statuses,
            "last_index": self.last_index
        }
        
    def get_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"current_emails": [], "email_statuses": {}, "last_index": 0, "subject": "", "mode": "template", "plain_text": ""}

    def save_state(self):
        state = {
            "current_emails": self.current_emails,
            "email_statuses": getattr(self, "email_statuses", {}),
            "last_index": self.last_index,
            "subject": self.subject,
            "mode": self.mode,
            "plain_text": self.plain_text,
            "total_emails": self.total_emails,
            "sent_emails": self.sent_emails,
            "failed_emails": self.failed_emails
        }
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)

    def start_sending(self, emails, subject, mode="template", plain_text="", template_html="", safety_limit=0, resume=False):
        if self.sending:
            return {"success": False, "message": "Already sending emails."}
            
        settings = self.get_settings()
        template = self.get_template()
        
        if not settings.get("smtp_server") or not settings.get("smtp_user"):
            return {"success": False, "message": "SMTP settings are incomplete."}
        
        actual_template = template_html if template_html else template
        
        if mode == "template" and not actual_template:
            return {"success": False, "message": "Email template is empty."}
        if mode == "text" and not plain_text.strip():
            return {"success": False, "message": "Plain text is empty."}
        if not emails:
            return {"success": False, "message": "No recipients provided."}
            
        self.sending = True
        self.paused = False
        self.current_emails = emails
        self.subject = subject
        self.mode = mode
        self.plain_text = plain_text
        self.total_emails = len(emails)
        
        if not resume:
            self.last_index = 0
            self.sent_emails = 0
            self.failed_emails = 0
            self.email_statuses = {}
        else:
            state = self.get_state()
            if state and "last_index" in state and emails == state.get("current_emails"):
                self.last_index = state.get("last_index", 0)
                self.sent_emails = state.get("sent_emails", 0)
                self.failed_emails = state.get("failed_emails", 0)
                self.email_statuses = state.get("email_statuses", {})
            else:
                self.last_index = 0
                self.sent_emails = 0
                self.failed_emails = 0
                self.email_statuses = {}
                
        self.save_state()
        
        thread = threading.Thread(target=self._send_loop, args=(settings, actual_template, safety_limit))
        thread.daemon = True
        thread.start()
        
        return {"success": True, "message": "Sending started." if not resume else f"Resumed from email #{self.last_index + 1}."}
        
    def stop_sending(self, is_pause=False):
        self.sending = False
        self.save_state()
        if is_pause:
            self.paused = True
            return {"success": True, "message": "Sending paused by safety limit."}
        return {"success": True, "message": "Sending stopped manually or finished."}
        
    def get_progress(self):
        return {
            "sending": self.sending,
            "paused": self.paused,
            "last_index": self.last_index,
            "total": self.total_emails,
            "sent": self.sent_emails,
            "failed": self.failed_emails
        }

    def _send_loop(self, settings, template, safety_limit):
        try:
            server = smtplib.SMTP(settings["smtp_server"], int(settings["smtp_port"]))
            server.starttls()
            server.login(settings["smtp_user"], settings["smtp_password"])
            
            delay = float(settings.get("delay", 1.0))
            from_addr = f'{settings.get("from_name", "")} <{settings["from_email"]}>' if settings.get("from_name") else settings["from_email"]
            
            session_sent = 0
            
            for i in range(self.last_index, len(self.current_emails)):
                if not self.sending:
                    break
                    
                email = self.current_emails[i]
                self.last_index = i
                
                try:
                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = self.subject
                    msg['From'] = from_addr
                    msg['To'] = email
                    
                    if self.mode == "template":
                        part = MIMEText(template, 'html')
                    else:
                        part = MIMEText(self.plain_text, 'plain')
                        
                    msg.attach(part)
                    
                    server.send_message(msg)
                    self.sent_emails += 1
                    session_sent += 1
                    self.email_statuses[email] = "sent"
                except Exception as e:
                    print(f"Failed to send to {email}: {e}")
                    self.failed_emails += 1
                    self.email_statuses[email] = "failed"
                
                self.save_state()
                
                if safety_limit > 0 and session_sent >= safety_limit:
                    self.sending = False
                    self.paused = True
                    break
                
                if delay > 0 and i < len(self.current_emails) - 1 and self.sending:
                    actual_delay = delay
                    if settings.get("jitter", False):
                        import random
                        actual_delay = delay * random.uniform(0.8, 1.5)
                    time.sleep(actual_delay)
                    
            server.quit()
        except Exception as e:
            print(f"SMTP Error: {e}")
        finally:
            self.sending = False
            self.save_state()

if __name__ == '__main__':
    api = Api()
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'index.html')
    window = webview.create_window('Email Sender application', html_path, js_api=api, width=1280, height=800, text_select=True)
    webview.start(debug=True)
