# FlowMail 📧

FlowMail is a minimalist, modern, desktop application built for bulk email campaigns. With an integrated drag-and-drop template builder, customizable anti-ban safety limits, and support for HTML & Plain Text emails, it makes reaching your audience effortless.

## Features ✨

*   **Beautiful Desktop UI:** Built on top of Tailwind CSS and embedded via `pywebview`. Dark mode enabled by default.
*   **Drag-&-Drop Builder:** Integrated GrapesJS builder to create and modify responsive HTML email templates visually.
*   **Template Gallery:** 15 pre-built professional templates included, plus the ability to save your own custom designs!
*   **CSV / Excel Import:** Easily upload `.csv` or `.xlsx` files; the app will automatically extract all valid email addresses.
*   **Manual Input:** Quick manual entry for small batches of recipients.
*   **Safe Sending Limits & Resumption:** 
    *   Set custom delays to respect SMTP rate limits.
    *   Auto-pause mechanism stops sending after a set limit.
    *   State saving allows you to **Resume** exactly where you left off if you close the app or reach a limit! 🛡️
*   **Built-in Provider Presets:** 1-click SMTP configurations for Gmail, Outlook, and Yahoo.
*   **Progress Tracking:** Live progress bar, success, and failure counts displayed on the dashboard.

## Installation 🚀

### 1. Prerequisites
You need Python 3.10+ installed on your system.

### 2. Clone the repository
```bash
git clone https://github.com/XsaTi4/FlowMail.git
cd "FlowMail"
```

### 3. Setup Virtual Environment & Install Dependencies
```bash
# Create venv
python3 -m venv venv

# Activate venv 
# (Mac/Linux)
source venv/bin/activate
# (Windows)
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```

## Security & Privacy 🔒
Your email credentials (SMTP passwords, app passwords) are stored **locally** on your machine in `data/settings.json`. They are never sent anywhere except directly to your chosen SMTP provider (e.g., Google or Microsoft) when sending emails.

## Connecting Gmail / Google Workspace 🛠️
Due to modern security standards, you cannot use your regular account password. You must use an **App Password**:
1. Go to your [Google Account Security](https://myaccount.google.com/security) settings.
2. Enable **2-Step Verification**.
3. Go to the [App Passwords page](https://myaccount.google.com/apppasswords).
4. Create a new app password (e.g., name it "FlowMail").
5. Copy the 16-character code and paste it into the "SMTP Password" field in FlowMail.

---

*This application is designed for legitimate newsletters, notifications, and updates. Please respect anti-spam laws (like CAN-SPAM, GDPR) when using bulk email tools.*
