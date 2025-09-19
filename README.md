# 🎨✨ Account Automation Suite ✨🎨

> **A high-tech, modern Python GUI for automating Playit.gg account creation with disposable Gmail addresses.**

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.7+-blue?logo=python" />
  <img src="https://img.shields.io/badge/GUI-PyQt5-41b883?logo=qt" />
  <img src="https://img.shields.io/badge/Automation-Selenium-43B02A?logo=selenium" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" />
</p>

---

## 🌟 Features

- 🎛️ **Modern PyQt5 GUI**: Sleek, animated, always-on-top window with custom gradients and effects.
- 🤖 **Automated Account Generation**: Selenium automates Playit.gg account creation with disposable Gmail addresses from emailnator.com.
- 🔒 **Secure Passwords**: Strong, random passwords for every account.
- 🗂️ **Account Management**: Credentials saved to a stylish `accounts.html` with delete/restore and visual feedback.
- 📝 **Thread-Safe Logging**: Real-time, animated log output for transparency and debugging.

---

## 🛠️ Requirements

- <span style="color:#3572A5">**Python 3.7+**</span>
- <span style="color:#4285F4">**Google Chrome**</span> (for Selenium automation)

### 📦 Python Dependencies

Install all required packages using:

```bash
pip install PyQt5 numpy selenium webdriver-manager
```

---

## 🚀 Quick Start

1. **Clone or Download** this repository and navigate to the project folder:

   ```bash
   cd "Account genarator"
   ```

2. **Install Dependencies** (see above).

3. **Run the Application**:

   ```bash
   python Accout_Genaration.py
   ```

4. **Using the App**:
   - Click the <span style="color:#00ff41;font-weight:bold">PLAYIT.GG</span> button to start automation.
   - The app opens a browser, generates a disposable Gmail, and automates Playit.gg registration.
   - Follow any prompts in the log area (e.g., manual email verification if required).
   - Credentials are saved to <span style="color:#00d4ff">`accounts.html`</span> with a beautiful UI and delete/restore options.

---

## 📁 Output Files

- <span style="color:#00d4ff">**accounts.html**</span>: All generated accounts, with interactive management (delete/restore, status, etc.).
- <span style="color:#ffb300">**found_emails.txt**</span>: List of all disposable emails used.

---
🔑 Secret Key Reset Tool

Purpose: If you forget your Playit.gg account credentials, the included batch file can regenerate a “broken” secret key. This lets you safely set up a new agent without needing to access the old account.
Functionality:
Generates a random 4-digit secret key.
Updates the playit.toml file in the current user's local AppData folder.
Fully automated for the current user; no manual edits required.

Usage:
Double-click the reset_secret_key.bat file.
The batch updates the secret_key in your Playit configuration.
Use the new key when setting up a new agent.

## 🧩 Troubleshooting

- ❌ **Missing Modules**: If you see import errors, ensure all pip packages are installed (see above).
- 🟢 **ChromeDriver Issues**: The app uses `webdriver-manager` to auto-download the correct ChromeDriver. Make sure Chrome is installed and up to date.
- 🔐 **Permissions**: Run the app with sufficient permissions to write output files in the project directory.

---

## ⚠️ Notes

- 🚨 *This tool is for educational and ethical use only. Do not use for spamming or violating any service's terms!*
- 🪟 The GUI is designed for Windows but should work on other platforms with minor tweaks.
- 🌐 For best results, use a stable internet connection and the latest version of Chrome.

---

## 🙏 Credits

- 💻 GUI: PyQt5
- 🤖 Automation: Selenium, webdriver-manager
- 📧 Disposable Email: emailnator.com

---

<p align="center">
  <b>✨ Enjoy your automated account generation experience! ✨</b><br>
  <img src="https://img.shields.io/badge/Happy%20Hacking!-00ff41?style=for-the-badge" />
</p> 
