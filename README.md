# Account Automation Suite

A high-tech, modern Python GUI tool for automating the creation and management of Playit.gg accounts using disposable Gmail addresses. This suite features a beautiful PyQt5 interface, animated effects, and robust Selenium-based automation for seamless account generation.

---

## Features

- **Modern PyQt5 GUI**: Sleek, animated, and always-on-top window with custom gradients and effects.
- **Automated Account Generation**: Uses Selenium to automate Playit.gg account creation with disposable Gmail addresses from emailnator.com.
- **Secure Passwords**: Generates strong, random passwords for each account.
- **Account Management**: Saves credentials to a stylish HTML file with delete/restore functionality and visual feedback.
- **Thread-Safe Logging**: Real-time, animated log output for transparency and debugging.
- **Sound Effects**: Optional click sound for button presses.

---

## Requirements

- **Python 3.7+**
- **Google Chrome** (for Selenium automation)

### Python Dependencies

Install all required packages using pip:

```bash
pip install PyQt5 numpy selenium webdriver-manager
```

If you want sound effects, ensure you have the `PyQt5.QtMultimedia` module (included with PyQt5 on most systems).

---

## Setup & Usage

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
   - Click the `PLAYIT.GG` button to start automation.
   - The app will open a browser, generate a disposable Gmail, and automate Playit.gg registration.
   - Follow any prompts in the log area (e.g., manual email verification if required).
   - Credentials are saved to `accounts.html` with a beautiful UI and delete/restore options.

---

## Output Files

- **accounts.html**: All generated accounts, with interactive management (delete/restore, status, etc.).
- **found_emails.txt**: List of all disposable emails used.

---

## Troubleshooting

- **Missing Modules**: If you see import errors, ensure all pip packages are installed (see above).
- **ChromeDriver Issues**: The app uses `webdriver-manager` to auto-download the correct ChromeDriver. Make sure Chrome is installed and up to date.
- **Permissions**: Run the app with sufficient permissions to write output files in the project directory.

---

## Notes

- This tool is for educational and ethical use only. Do not use for spamming or violating any service's terms.
- The GUI is designed for Windows but should work on other platforms with minor tweaks.
- For best results, use a stable internet connection and the latest version of Chrome.

---

## Credits

- GUI: PyQt5
- Automation: Selenium, webdriver-manager
- Disposable Email: emailnator.com

---

Enjoy your automated account generation experience! 
