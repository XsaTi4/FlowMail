import csv
import json
import os
import random
import re
import smtplib
import ssl
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import webview
from email_validator import EmailNotValidError, validate_email


DEFAULT_SETTINGS = {
    "smtp_server": "",
    "smtp_port": "587",
    "smtp_user": "",
    "smtp_password": "",
    "from_email": "",
    "from_name": "",
    "delay": 2.0,
    "jitter": True,
    "disable_safety": False,
    "batch_size": 25,
    "batch_pause": 60,
    "max_per_domain": 10,
    "domain_cooldown": 120,
    "max_retries": 2,
    "retry_backoff": 15,
    "spread_by_domain": True,
}

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def get_base_path():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def utc_now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


BASE_DIR = get_base_path()
UI_DIR = os.path.join(BASE_DIR, "ui")
SYSTEM_TEMPLATES_DIR = os.path.join(BASE_DIR, "data", "templates")

USER_DATA_DIR = os.path.join(os.path.expanduser("~"), ".flowmail_data")
os.makedirs(USER_DATA_DIR, exist_ok=True)

SETTINGS_FILE = os.path.join(USER_DATA_DIR, "settings.json")
TEMPLATE_FILE = os.path.join(USER_DATA_DIR, "template.html")
USER_TEMPLATES_FILE = os.path.join(USER_DATA_DIR, "user_templates.json")
STATE_FILE = os.path.join(USER_DATA_DIR, "state.json")
SEND_HISTORY_FILE = os.path.join(USER_DATA_DIR, "send_history.json")

if not getattr(sys, "frozen", False):
    if not os.path.exists(SYSTEM_TEMPLATES_DIR) or not os.listdir(SYSTEM_TEMPLATES_DIR):
        try:
            from generate_templates import generate_system_templates

            generate_system_templates(os.path.join(BASE_DIR, "data"))
        except Exception as e:
            print(f"Warning: Failed to auto-generate system templates: {e}")


class Api:
    def __init__(self):
        self.state_lock = threading.Lock()
        self.sending = False
        self.paused = False
        self.pause_reason = ""
        self.latest_safety_event = ""

        self.total_emails = 0
        self.sent_emails = 0
        self.failed_emails = 0
        self.current_emails = []
        self.email_statuses = {}
        self.email_errors = {}

        self.subject = ""
        self.mode = "template"
        self.plain_text = ""
        self.last_index = 0

    @staticmethod
    def _safe_int(value, fallback):
        try:
            return int(value)
        except Exception:
            return fallback

    @staticmethod
    def _safe_float(value, fallback):
        try:
            return float(value)
        except Exception:
            return fallback

    def _sanitize_settings(self, settings):
        merged = DEFAULT_SETTINGS.copy()
        if isinstance(settings, dict):
            merged.update(settings)

        merged["smtp_server"] = str(merged.get("smtp_server", "")).strip()
        merged["smtp_port"] = str(max(1, self._safe_int(merged.get("smtp_port"), 587)))
        merged["smtp_user"] = str(merged.get("smtp_user", "")).strip()
        merged["smtp_password"] = str(merged.get("smtp_password", ""))
        merged["from_email"] = str(merged.get("from_email", "")).strip()
        merged["from_name"] = str(merged.get("from_name", "")).strip()

        merged["delay"] = max(0.0, self._safe_float(merged.get("delay"), 2.0))
        merged["jitter"] = bool(merged.get("jitter", True))
        merged["disable_safety"] = bool(merged.get("disable_safety", False))

        merged["batch_size"] = max(0, self._safe_int(merged.get("batch_size"), 25))
        merged["batch_pause"] = max(0.0, self._safe_float(merged.get("batch_pause"), 60.0))
        merged["max_per_domain"] = max(0, self._safe_int(merged.get("max_per_domain"), 10))
        merged["domain_cooldown"] = max(0.0, self._safe_float(merged.get("domain_cooldown"), 120.0))
        merged["max_retries"] = min(5, max(0, self._safe_int(merged.get("max_retries"), 2)))
        merged["retry_backoff"] = max(1.0, self._safe_float(merged.get("retry_backoff"), 15.0))
        merged["spread_by_domain"] = bool(merged.get("spread_by_domain", True))

        return merged

    @staticmethod
    def _default_state():
        return {
            "current_emails": [],
            "email_statuses": {},
            "email_errors": {},
            "last_index": 0,
            "subject": "",
            "mode": "template",
            "plain_text": "",
            "total_emails": 0,
            "sent_emails": 0,
            "failed_emails": 0,
            "paused": False,
            "pause_reason": "",
            "latest_safety_event": "",
            "updated_at": None,
        }

    @staticmethod
    def _normalize_email(email):
        return str(email or "").strip().lower()

    def _dedupe_emails(self, emails):
        unique = []
        seen = set()
        for email in emails or []:
            normalized = self._normalize_email(email)
            if not normalized:
                continue
            if normalized not in seen:
                unique.append(normalized)
                seen.add(normalized)
        return unique

    @staticmethod
    def _extract_domain(email):
        if "@" not in email:
            return ""
        return email.rsplit("@", 1)[1].lower().strip()

    def _spread_emails_by_domain(self, emails):
        grouped = defaultdict(deque)
        domain_order = []
        seen_domains = set()

        for email in emails:
            domain = self._extract_domain(email)
            grouped[domain].append(email)
            if domain not in seen_domains:
                seen_domains.add(domain)
                domain_order.append(domain)

        spread = []
        while True:
            made_progress = False
            for domain in domain_order:
                queue = grouped[domain]
                if queue:
                    spread.append(queue.popleft())
                    made_progress = True
            if not made_progress:
                break

        return spread

    def _sleep_with_cancel(self, seconds):
        seconds = max(0.0, self._safe_float(seconds, 0.0))
        if seconds <= 0:
            return

        end_time = time.time() + seconds
        while self.sending and time.time() < end_time:
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            time.sleep(min(0.25, remaining))

    def _is_retryable_error(self, exc):
        if isinstance(
            exc,
            (
                smtplib.SMTPServerDisconnected,
                smtplib.SMTPConnectError,
                TimeoutError,
                ConnectionError,
            ),
        ):
            return True

        if isinstance(exc, smtplib.SMTPResponseException):
            code = int(getattr(exc, "smtp_code", 0) or 0)
            return 400 <= code < 500

        if isinstance(exc, smtplib.SMTPDataError):
            code = int(getattr(exc, "smtp_code", 0) or 0)
            if code == 0:
                return True
            return 400 <= code < 500

        return False

    @staticmethod
    def _format_error(exc):
        message = str(exc).strip()
        return (message or exc.__class__.__name__)[:280]

    @staticmethod
    def _set_safety_event(event_text):
        return str(event_text or "").strip()[:300]

    @staticmethod
    def _save_json_atomic(path, payload):
        tmp_path = f"{path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        os.replace(tmp_path, path)

    def _load_send_history(self):
        if not os.path.exists(SEND_HISTORY_FILE):
            return []
        try:
            with open(SEND_HISTORY_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    return loaded
        except Exception:
            pass
        return []

    @staticmethod
    def _history_cutoff(hours):
        return int(time.time() - hours * 3600)

    def _count_recent_sent(self, hours=24):
        cutoff = self._history_cutoff(hours)
        count = 0
        entries = self._load_send_history()
        for item in entries:
            ts = self._safe_int(item.get("ts"), 0) if isinstance(item, dict) else 0
            status = item.get("status") if isinstance(item, dict) else None
            if ts >= cutoff and status == "sent":
                count += 1
        return count

    def _record_send_event(self, email, status):
        entries = self._load_send_history()
        cutoff_72h = self._history_cutoff(72)
        kept = []
        for item in entries:
            ts = self._safe_int(item.get("ts"), 0) if isinstance(item, dict) else 0
            if ts >= cutoff_72h:
                kept.append(item)

        kept.append(
            {
                "ts": int(time.time()),
                "email": self._normalize_email(email),
                "domain": self._extract_domain(email),
                "status": status,
            }
        )

        # Hard cap to keep file small.
        kept = kept[-5000:]
        self._save_json_atomic(SEND_HISTORY_FILE, kept)

    def _connect_smtp(self, settings):
        host = settings["smtp_server"]
        port = self._safe_int(settings["smtp_port"], 587)
        user = settings["smtp_user"]
        password = settings["smtp_password"]

        timeout = 30
        context = ssl.create_default_context()

        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=timeout, context=context)
            server.ehlo()
        else:
            server = smtplib.SMTP(host, port, timeout=timeout)
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()

        server.login(user, password)
        return server

    def _build_message(self, to_email, settings, template_html):
        from_email = settings.get("from_email") or settings.get("smtp_user")
        from_name = settings.get("from_name", "")
        from_addr = f"{from_name} <{from_email}>" if from_name else from_email

        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.subject
        msg["From"] = from_addr
        msg["To"] = to_email

        if self.mode == "template":
            part = MIMEText(template_html, "html")
        else:
            part = MIMEText(self.plain_text, "plain")

        msg.attach(part)
        return msg

    def _extract_valid_emails(self, text):
        candidates = EMAIL_REGEX.findall(text or "")
        valid = []

        for candidate in candidates:
            lowered = candidate.lower().strip()
            try:
                validated = validate_email(lowered, check_deliverability=False)
                valid.append(validated.normalized)
            except EmailNotValidError:
                continue

        return valid

    def _read_csv_as_text(self, filepath):
        try:
            df = pd.read_csv(
                filepath,
                dtype=str,
                keep_default_na=False,
                sep=None,
                engine="python",
            )
            return df.to_csv(index=False)
        except Exception:
            lines = []
            with open(filepath, "r", encoding="utf-8", errors="ignore", newline="") as f:
                sample = f.read(4096)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;|\t")
                except Exception:
                    dialect = csv.excel
                reader = csv.reader(f, dialect)
                for row in reader:
                    lines.append(" ".join(str(cell) for cell in row))
            return "\n".join(lines)

    def _read_xlsx_as_text(self, filepath):
        all_sheets = pd.read_excel(filepath, sheet_name=None, dtype=str)
        chunks = []

        for _, sheet_df in all_sheets.items():
            if sheet_df is None:
                continue
            chunk = sheet_df.fillna("").to_csv(index=False)
            chunks.append(chunk)

        return "\n".join(chunks)

    def get_settings(self):
        settings = DEFAULT_SETTINGS.copy()

        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    settings = self._sanitize_settings(loaded)
            except Exception:
                settings = DEFAULT_SETTINGS.copy()

        return self._sanitize_settings(settings)

    def save_settings(self, settings):
        sanitized = self._sanitize_settings(settings)

        if not sanitized["disable_safety"] and sanitized["delay"] < 0.8:
            sanitized["delay"] = 0.8

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(sanitized, f, indent=4)

        return {
            "success": True,
            "message": "Settings saved successfully.",
            "settings": sanitized,
        }

    def save_template(self, html):
        html = "" if html is None else html
        with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
            f.write(html)
        return {"success": True, "message": "Template saved successfully."}

    def get_template(self):
        if os.path.exists(TEMPLATE_FILE):
            with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    def get_user_templates(self):
        if os.path.exists(USER_TEMPLATES_FILE):
            try:
                with open(USER_TEMPLATES_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, list):
                        return loaded
            except Exception:
                pass
        return []

    def save_user_template(self, name, html):
        html = "" if html is None else html
        name = str(name or "").strip() or "Untitled template"

        templates = self.get_user_templates()
        templates.append({"name": name, "html": html})

        with open(USER_TEMPLATES_FILE, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=4)

        return {"success": True, "message": f"Template '{name}' saved to gallery."}

    def delete_user_template(self, index):
        templates = self.get_user_templates()
        if 0 <= index < len(templates):
            name = templates[index]["name"]
            del templates[index]
            with open(USER_TEMPLATES_FILE, "w", encoding="utf-8") as f:
                json.dump(templates, f, indent=4)
            return {"success": True, "message": f"Template '{name}' deleted."}
        return {"success": False, "message": "Template not found."}

    def get_preset_templates(self):
        templates = []
        if os.path.exists(SYSTEM_TEMPLATES_DIR):
            filenames = [name for name in os.listdir(SYSTEM_TEMPLATES_DIR) if name.endswith(".json")]

            def sort_key(name):
                match = re.search(r"(\d+)", name)
                if match:
                    return (0, int(match.group(1)))
                return (1, name.lower())

            for filename in sorted(filenames, key=sort_key):
                if filename.endswith(".json"):
                    try:
                        with open(
                            os.path.join(SYSTEM_TEMPLATES_DIR, filename),
                            "r",
                            encoding="utf-8",
                        ) as f:
                            templates.append(json.load(f))
                    except Exception:
                        pass
        return templates

    def parse_file(self, filepath):
        try:
            extension = os.path.splitext(filepath)[1].lower()
            if extension == ".csv":
                text = self._read_csv_as_text(filepath)
            elif extension == ".xlsx":
                text = self._read_xlsx_as_text(filepath)
            else:
                return {"success": False, "message": "Unsupported file format."}

            extracted = self._extract_valid_emails(text)
            unique = self._dedupe_emails(extracted)
            duplicate_count = max(0, len(extracted) - len(unique))

            domain_counts = defaultdict(int)
            for email in unique:
                domain = self._extract_domain(email)
                if domain:
                    domain_counts[domain] += 1

            top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "success": True,
                "emails": unique,
                "count": len(unique),
                "found_count": len(extracted),
                "duplicates_removed": duplicate_count,
                "top_domains": top_domains,
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def select_file(self):
        file_types = ("CSV Files (*.csv)", "Excel Files (*.xlsx)")
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types,
        )
        if result and len(result) > 0:
            return self.parse_file(result[0])
        return {"success": False, "message": "No file selected."}

    def get_queue(self, new_emails=None):
        if new_emails is not None:
            emails_to_show = self._dedupe_emails(new_emails)
            statuses = {}
            errors = {}
        else:
            emails_to_show = list(getattr(self, "current_emails", []))
            statuses = dict(getattr(self, "email_statuses", {}))
            errors = dict(getattr(self, "email_errors", {}))

        sent_count = sum(1 for status in statuses.values() if status == "sent")
        failed_count = sum(1 for status in statuses.values() if status == "failed")
        pending_count = max(0, len(emails_to_show) - sent_count - failed_count)

        return {
            "emails": emails_to_show,
            "statuses": statuses,
            "email_errors": errors,
            "last_index": getattr(self, "last_index", 0),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "pending_count": pending_count,
        }

    def clear_cache(self):
        if self.sending:
            return {
                "success": False,
                "message": "Stop sending before wiping cache.",
            }

        try:
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)

            self.current_emails = []
            self.email_statuses = {}
            self.email_errors = {}
            self.last_index = 0
            self.sent_emails = 0
            self.failed_emails = 0
            self.total_emails = 0
            self.paused = False
            self.pause_reason = ""
            self.latest_safety_event = ""
            self.subject = ""
            self.mode = "template"
            self.plain_text = ""

            return {
                "success": True,
                "message": "App cache and queue completely cleared.",
            }
        except Exception as e:
            return {"success": False, "message": f"Could not clear cache: {e}"}

    def remove_from_queue(self, email):
        if self.sending:
            return {"success": False, "message": "Pause sending to modify queue."}

        target = self._normalize_email(email)
        if target in self.current_emails:
            idx = self.current_emails.index(target)
            self.current_emails.remove(target)

            if idx < self.last_index:
                self.last_index -= 1

            self.total_emails = len(self.current_emails)

            if target in self.email_statuses:
                status = self.email_statuses.pop(target)
                if status == "sent":
                    self.sent_emails = max(0, self.sent_emails - 1)
                elif status == "failed":
                    self.failed_emails = max(0, self.failed_emails - 1)

            self.email_errors.pop(target, None)
            self.save_state()
            return {"success": True, "message": f"{target} removed."}

        return {"success": False, "message": "Email not found."}

    def get_state(self):
        state = self._default_state()
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    state.update(loaded)
            except Exception:
                pass

        state["current_emails"] = self._dedupe_emails(state.get("current_emails", []))
        state["email_statuses"] = dict(state.get("email_statuses", {}))
        state["email_errors"] = dict(state.get("email_errors", {}))
        state["last_index"] = max(0, self._safe_int(state.get("last_index"), 0))
        state["total_emails"] = max(0, self._safe_int(state.get("total_emails"), len(state["current_emails"])))
        state["sent_emails"] = max(0, self._safe_int(state.get("sent_emails"), 0))
        state["failed_emails"] = max(0, self._safe_int(state.get("failed_emails"), 0))
        state["paused"] = bool(state.get("paused", False))
        state["pause_reason"] = str(state.get("pause_reason", ""))
        state["latest_safety_event"] = str(state.get("latest_safety_event", ""))

        if state["total_emails"] == 0 and state["current_emails"]:
            state["total_emails"] = len(state["current_emails"])

        return state

    def save_state(self):
        state = {
            "current_emails": self.current_emails,
            "email_statuses": self.email_statuses,
            "email_errors": self.email_errors,
            "last_index": self.last_index,
            "subject": self.subject,
            "mode": self.mode,
            "plain_text": self.plain_text,
            "total_emails": self.total_emails,
            "sent_emails": self.sent_emails,
            "failed_emails": self.failed_emails,
            "paused": self.paused,
            "pause_reason": self.pause_reason,
            "latest_safety_event": self.latest_safety_event,
            "updated_at": utc_now_iso(),
        }

        with self.state_lock:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)

    def get_safety_recommendation(self, recipients_count):
        count = max(0, self._safe_int(recipients_count, 0))
        settings = self.get_settings()
        sent_last_24h = self._count_recent_sent(24)

        level_rank = {"low": 1, "medium": 2, "high": 3}
        risk_level = "low"
        reasons = []

        def escalate(level, reason):
            nonlocal risk_level
            if level_rank[level] > level_rank[risk_level]:
                risk_level = level
            reasons.append(reason)

        if settings["disable_safety"]:
            escalate("high", "Safety protections are disabled.")

        if sent_last_24h >= 1000:
            escalate(
                "high",
                f"High traffic detected: {sent_last_24h} emails sent in the last 24 hours.",
            )
        elif sent_last_24h >= 400:
            escalate(
                "medium",
                f"Elevated traffic: {sent_last_24h} emails sent in the last 24 hours.",
            )

        if count >= 100 and settings["delay"] < 1.5:
            escalate("high", "Delay is too low for this queue size.")
        elif count >= 40 and settings["delay"] < 1.0:
            escalate("medium", "Delay is low for medium-sized campaign.")
        elif settings["delay"] < 0.8:
            escalate("high", "Delay is below minimum safe threshold.")

        if settings["batch_size"] == 0:
            escalate("medium", "Batch cooldown is disabled.")
        elif settings["batch_pause"] < 15:
            escalate("medium", "Batch cooldown is too short (<15s).")

        if settings["max_per_domain"] == 0:
            escalate("medium", "Domain cooldown is disabled.")
        elif settings["domain_cooldown"] < 30:
            escalate("medium", "Domain cooldown is too short (<30s).")

        if settings["max_per_domain"] > 25 and settings["domain_cooldown"] < 60:
            escalate("high", "Too many emails per domain with low cooldown.")

        suggested = {
            "delay": 2.0 if count < 200 else 3.0,
            "batch_size": 25 if count < 300 else 15,
            "batch_pause": 60 if count < 300 else 120,
            "max_per_domain": 10,
            "domain_cooldown": 120,
            "max_retries": 2,
            "retry_backoff": 20,
        }

        return {
            "risk_level": risk_level,
            "reasons": reasons,
            "suggested": suggested,
            "count": count,
            "sent_last_24h": sent_last_24h,
        }

    def start_sending(
        self,
        emails,
        subject,
        mode="template",
        plain_text="",
        template_html="",
        safety_limit=0,
        resume=False,
    ):
        if self.sending:
            return {"success": False, "message": "Already sending emails."}

        settings = self.get_settings()
        stored_template = self.get_template()

        if not settings.get("smtp_server") or not settings.get("smtp_user") or not settings.get("smtp_password"):
            return {"success": False, "message": "SMTP settings are incomplete."}

        from_email = settings.get("from_email") or settings.get("smtp_user")
        if not from_email:
            return {"success": False, "message": "Set a valid From Email in Settings."}

        try:
            validated_from = validate_email(from_email, check_deliverability=False)
            settings["from_email"] = validated_from.normalized
        except EmailNotValidError:
            return {"success": False, "message": "From Email is invalid."}

        normalized_subject = str(subject or "").strip()
        if not normalized_subject:
            return {"success": False, "message": "Email subject cannot be empty."}

        normalized_mode = "text" if mode == "text" else "template"
        actual_template = template_html if template_html else stored_template

        if normalized_mode == "template" and not str(actual_template or "").strip():
            return {"success": False, "message": "Email template is empty."}

        plain_text = str(plain_text or "")
        if normalized_mode == "text" and not plain_text.strip():
            return {"success": False, "message": "Plain text is empty."}

        deduped_emails = self._dedupe_emails(emails)
        if not deduped_emails:
            return {"success": False, "message": "No recipients provided."}

        limit = max(0, self._safe_int(safety_limit, 0))
        sent_last_24h = self._count_recent_sent(24)
        safety_adjustments = []

        if settings.get("disable_safety") and limit > 0:
            limit = 0
            safety_adjustments.append("Session auto-pause limit ignored because safety is disabled.")

        if not settings.get("disable_safety"):
            if sent_last_24h >= 1500:
                return {
                    "success": False,
                    "message": (
                        "Safety lock: very high sending volume in last 24h. "
                        "Wait before next campaign or explicitly disable safety limits."
                    ),
                }

            if sent_last_24h >= 800:
                settings["delay"] = max(settings["delay"], 4.0)
                settings["batch_size"] = 10 if settings["batch_size"] == 0 else min(settings["batch_size"], 10)
                settings["batch_pause"] = max(settings["batch_pause"], 240)
                settings["max_per_domain"] = 5 if settings["max_per_domain"] == 0 else min(settings["max_per_domain"], 5)
                settings["domain_cooldown"] = max(settings["domain_cooldown"], 180)
                safety_adjustments.append(
                    f"24h traffic is high ({sent_last_24h}). Safety throttle increased automatically."
                )
            elif sent_last_24h >= 300:
                settings["delay"] = max(settings["delay"], 3.0)
                settings["batch_size"] = 15 if settings["batch_size"] == 0 else min(settings["batch_size"], 15)
                settings["batch_pause"] = max(settings["batch_pause"], 120)
                settings["max_per_domain"] = 8 if settings["max_per_domain"] == 0 else min(settings["max_per_domain"], 8)
                settings["domain_cooldown"] = max(settings["domain_cooldown"], 120)
                safety_adjustments.append(
                    f"24h traffic is elevated ({sent_last_24h}). Safer pacing applied."
                )

            if settings["delay"] < 0.8:
                settings["delay"] = 0.8
                safety_adjustments.append("Minimum delay raised to 0.8s by safety policy.")

            if settings["batch_size"] > 0 and settings["batch_pause"] < 15:
                settings["batch_pause"] = 15
                safety_adjustments.append("Batch cooldown raised to 15s (too low).")

            if settings["max_per_domain"] > 0 and settings["domain_cooldown"] < 30:
                settings["domain_cooldown"] = 30
                safety_adjustments.append("Domain cooldown raised to 30s (too low).")

            if settings["max_per_domain"] > 25 and settings["domain_cooldown"] < 60:
                settings["max_per_domain"] = 25
                settings["domain_cooldown"] = 60
                safety_adjustments.append("Domain burst risk detected. Per-domain pacing tightened automatically.")
        else:
            safety_adjustments.append("Safety protections are disabled manually.")

        self.sending = True
        self.paused = False
        self.pause_reason = ""
        self.latest_safety_event = self._set_safety_event(" ".join(safety_adjustments))
        self.subject = normalized_subject
        self.mode = normalized_mode
        self.plain_text = plain_text

        if not resume:
            if settings.get("spread_by_domain") and not settings.get("disable_safety"):
                self.current_emails = self._spread_emails_by_domain(deduped_emails)
            else:
                self.current_emails = deduped_emails

            self.total_emails = len(self.current_emails)
            self.last_index = 0
            self.sent_emails = 0
            self.failed_emails = 0
            self.email_statuses = {}
            self.email_errors = {}
        else:
            state = self.get_state()
            saved_emails = self._dedupe_emails(state.get("current_emails", []))
            missing_emails = [e for e in deduped_emails if e not in set(saved_emails)]

            if settings.get("spread_by_domain") and not settings.get("disable_safety") and missing_emails:
                missing_emails = self._spread_emails_by_domain(missing_emails)

            self.current_emails = saved_emails + missing_emails
            self.total_emails = len(self.current_emails)
            self.last_index = min(
                max(0, self._safe_int(state.get("last_index"), 0)),
                self.total_emails,
            )
            self.sent_emails = max(0, self._safe_int(state.get("sent_emails"), 0))
            self.failed_emails = max(0, self._safe_int(state.get("failed_emails"), 0))
            self.email_statuses = dict(state.get("email_statuses", {}))
            self.email_errors = dict(state.get("email_errors", {}))
            self.latest_safety_event = self._set_safety_event(state.get("latest_safety_event", ""))

            if self.last_index >= self.total_emails:
                self.sending = False
                self.paused = False
                self.pause_reason = ""
                return {
                    "success": False,
                    "message": "Queue is already completed. Add new recipients or start a new campaign.",
                }

        self.save_state()

        thread = threading.Thread(
            target=self._send_loop,
            args=(settings, actual_template, limit),
            daemon=True,
        )
        thread.start()

        if not resume:
            message = "Sending started."
            if self.latest_safety_event:
                message += f" Safety: {self.latest_safety_event}"
            return {"success": True, "message": message}

        message = f"Resumed from email #{self.last_index + 1}."
        if self.latest_safety_event:
            message += f" Safety: {self.latest_safety_event}"

        return {
            "success": True,
            "message": message,
        }

    def stop_sending(self, is_pause=False):
        if not self.sending and not self.paused:
            return {"success": True, "message": "No active sending session."}

        self.sending = False
        self.paused = bool(is_pause)
        self.pause_reason = "Paused manually." if is_pause else ""
        if is_pause:
            self.latest_safety_event = self._set_safety_event("Paused manually by user.")
        self.save_state()

        if is_pause:
            return {"success": True, "message": "Sending paused."}

        return {"success": True, "message": "Sending stopped."}

    def get_progress(self):
        return {
            "sending": self.sending,
            "paused": self.paused,
            "pause_reason": self.pause_reason,
            "latest_safety_event": self.latest_safety_event,
            "last_index": self.last_index,
            "total": self.total_emails,
            "sent": self.sent_emails,
            "failed": self.failed_emails,
        }

    def _send_loop(self, settings, template, safety_limit):
        server = None

        settings = self._sanitize_settings(settings)
        disable_safety = settings.get("disable_safety", False)

        delay = settings.get("delay", 0.0)
        jitter = settings.get("jitter", False) and not disable_safety

        batch_size = settings.get("batch_size", 0)
        batch_pause = settings.get("batch_pause", 0.0)
        max_per_domain = settings.get("max_per_domain", 0)
        domain_cooldown = settings.get("domain_cooldown", 0.0)
        max_retries = settings.get("max_retries", 0)
        retry_backoff = settings.get("retry_backoff", 15.0)

        if disable_safety:
            delay = 0.0
            batch_size = 0
            batch_pause = 0.0
            max_per_domain = 0
            domain_cooldown = 0.0
        else:
            delay = max(0.8, delay)

        session_sent = 0
        batch_counter = 0
        domain_counter = defaultdict(int)

        try:
            server = self._connect_smtp(settings)

            for i in range(self.last_index, len(self.current_emails)):
                if not self.sending:
                    break

                email = self.current_emails[i]
                domain = self._extract_domain(email)

                delivery_success = False
                error_message = ""

                for attempt in range(max_retries + 1):
                    if not self.sending:
                        break

                    try:
                        msg = self._build_message(email, settings, template)
                        server.send_message(msg)
                        delivery_success = True
                        break
                    except Exception as exc:
                        error_message = self._format_error(exc)
                        should_retry = (
                            attempt < max_retries
                            and self._is_retryable_error(exc)
                            and self.sending
                        )

                        if not should_retry:
                            break

                        if isinstance(exc, (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError)):
                            try:
                                server = self._connect_smtp(settings)
                            except Exception as reconnect_exc:
                                error_message = (
                                    f"{error_message}; reconnect failed: {self._format_error(reconnect_exc)}"
                                )
                                break

                        backoff = max(1.0, retry_backoff * (attempt + 1))
                        if jitter:
                            backoff *= random.uniform(0.9, 1.3)
                        self._sleep_with_cancel(backoff)

                if delivery_success:
                    self.sent_emails += 1
                    session_sent += 1
                    self.email_statuses[email] = "sent"
                    self.email_errors.pop(email, None)
                    domain_counter[domain] += 1
                    self._record_send_event(email, "sent")
                else:
                    self.failed_emails += 1
                    self.email_statuses[email] = "failed"
                    self.email_errors[email] = error_message or "Unknown sending error"
                    self._record_send_event(email, "failed")

                self.last_index = i + 1
                batch_counter += 1
                self.save_state()

                if safety_limit > 0 and session_sent >= safety_limit:
                    self.sending = False
                    self.paused = True
                    self.pause_reason = f"Safety auto-pause reached: {session_sent} sent in this session."
                    self.latest_safety_event = self._set_safety_event(self.pause_reason)
                    break

                if not self.sending or self.last_index >= len(self.current_emails):
                    continue

                if max_per_domain > 0 and domain and domain_counter[domain] > 0 and domain_counter[domain] % max_per_domain == 0:
                    self.pause_reason = (
                        f"Domain cooldown: waiting {int(domain_cooldown)}s after {max_per_domain} emails to {domain}."
                    )
                    self.latest_safety_event = self._set_safety_event(self.pause_reason)
                    self.save_state()
                    self._sleep_with_cancel(domain_cooldown)
                    self.pause_reason = ""

                if batch_size > 0 and batch_counter >= batch_size:
                    self.pause_reason = f"Batch cooldown: waiting {int(batch_pause)}s every {batch_size} emails."
                    self.latest_safety_event = self._set_safety_event(self.pause_reason)
                    self.save_state()
                    self._sleep_with_cancel(batch_pause)
                    batch_counter = 0
                    self.pause_reason = ""

                if delay > 0:
                    real_delay = delay
                    if jitter:
                        real_delay *= random.uniform(0.85, 1.4)
                    self._sleep_with_cancel(real_delay)

            if self.sending:
                self.paused = False
                self.pause_reason = ""

        except Exception as e:
            print(f"SMTP Error: {e}")
            self.paused = True
            self.pause_reason = f"SMTP connection error: {self._format_error(e)}"
            self.latest_safety_event = self._set_safety_event(self.pause_reason)
        finally:
            if server is not None:
                try:
                    server.quit()
                except Exception:
                    pass

            self.sending = False
            self.save_state()


if __name__ == "__main__":
    api = Api()
    html_path = os.path.join(UI_DIR, "index.html")
    webview.create_window(
        "FlowMail",
        html_path,
        js_api=api,
        width=1280,
        height=800,
        text_select=True,
    )
    webview.start(debug=False)
