import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QUrl, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QLinearGradient, QPen
from PyQt5.QtMultimedia import QSoundEffect
import os
import numpy as np
# --- Automation imports ---
import threading
import time
import secrets
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.support.ui import Select

class HighTechGUI(QWidget):
    # Signal for thread-safe log updates
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Account Automation Suite")
        self.setWindowFlags(Qt.WindowType(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint))
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.92)
        self.setMinimumSize(700, 500)
        self._gradient_phase = 0
        self._gradient_timer = QTimer(self)
        self._gradient_timer.timeout.connect(self._update_gradient)
        self._gradient_timer.start(100)
        self._drag_pos = None
        self._setup_ui()
        self._setup_sound()
        self._automation_thread = None
        
        # Simple log buffer for handling rapid messages
        self._log_buffer = ""
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._flush_log_buffer)
        self._log_timer.setSingleShot(True)
        
        # Connect the signal to the log update method
        self.log_signal.connect(self._safe_animate_log)
        
        # Keep window on top
        self.setWindowState(Qt.WindowState.WindowActive)
        self.raise_()
        self.activateWindow()

    def _flush_log_buffer(self):
        """Flush accumulated log messages"""
        if self._log_buffer:
            self.log.moveCursor(self.log.textCursor().End)
            self.log.insertPlainText(self._log_buffer)
            self.log.moveCursor(self.log.textCursor().End)
            self.log.ensureCursorVisible()
            self._log_buffer = ""

    def _safe_animate_log(self, text):
        """Thread-safe log update method"""
        if text == "READY_SIGNAL":
            self.set_status("READY", color="#00ff41")
            self.enable_buttons()
        else:
            # Add to buffer
            self._log_buffer += text
            # Start timer to flush buffer (debounce rapid messages)
            if not self._log_timer.isActive():
                self._log_timer.start(150)  # 150ms delay for better readability

    # --- Automation logic from automate.py as methods ---
    def setup_driver(self):
        self.log_signal.emit("[INFO] Setting up Chrome WebDriver...\n")
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1200,800")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        # Suppress debug messages and warnings
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--silent")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver

    def save_email_to_file(self, email):
        with open('found_emails.txt', 'a') as file:
            file.write(email + '\n')

    def save_credentials(self, service_name, email, password, username=None):
        # Check if base HTML file exists, if not create it
        base_file = 'accounts.html'
        
        if not os.path.exists(base_file):
            # Create new base HTML file
            self._create_base_html_file()
        
        # Read existing content
        with open(base_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Remove the "no accounts" message if it exists
        content = content.replace(
            '<div class="no-accounts">\n                <div class="icon">🔐</div>\n                <p>No accounts generated yet.</p>\n                <p>Start the automation to see your accounts here!</p>\n            </div>',
            ''
        )
        
        # Generate unique ID for this account
        account_id = f"account_{int(time.time())}"
        
        # Add the new account card
        new_account_html = f"""
            <div class="account-card" id="{account_id}">
                <div class="bubble"></div>
                <div class="bubble"></div>
                <div class="bubble"></div>
                <div class="success-indicator"></div>
                <div class="service-badge">Playit.gg</div>
                
                <div class="credential-item">
                    <div class="credential-label">Email Address</div>
                    <div class="credential-value">{email}</div>
                </div>
                
                <div class="credential-item">
                    <div class="credential-label">Password</div>
                    <div class="credential-value">{password}</div>
                </div>
                
                <div class="credential-item">
                    <div class="credential-label">Status</div>
                    <div class="credential-value" id="status-{account_id}">ACTIVE</div>
                </div>
                
                <div class="timestamp">
                    Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}
                </div>
                
                <button class="delete-button" onclick="deleteAccount('{account_id}', 'Playit.gg', '{email}')">
                    <span class="delete-icon">🗑️</span>
                    DELETE ACCOUNT
                </button>
            </div>
"""
        
        # Insert the new account before the closing accounts-grid div
        content = content.replace(
            '        </div>\n    </div>',
            f'{new_account_html}\n        </div>\n    </div>'
        )
        
        # Add delete functionality to the JavaScript if not already present
        if 'function deleteAccount(' not in content:
            delete_script = """
        // Delete account functionality
        function deleteAccount(accountId, serviceName, email) {
            if (confirm(`Are you sure you want to delete this ${serviceName} account?\\nEmail: ${email}\\n\\nThis action cannot be undone!`)) {
                const accountCard = document.getElementById(accountId);
                if (accountCard) {
                    // Add fade out animation
                    accountCard.style.transition = 'all 0.5s ease';
                    accountCard.style.transform = 'scale(0.8)';
                    accountCard.style.opacity = '0';
                    
                    setTimeout(() => {
                        // Instead of removing, mark as deleted
                        accountCard.classList.add('deleted-account');
                        accountCard.style.transform = 'scale(1)';
                        accountCard.style.opacity = '0.3';
                        
                        // Add deleted overlay
                        const deletedOverlay = document.createElement('div');
                        deletedOverlay.className = 'deleted-overlay';
                        deletedOverlay.innerHTML = `
                            <div class="deleted-text">DELETED</div>
                            <button class="restore-button" onclick="restoreAccount('${accountId}', '${serviceName}', '${email}')">
                                <span class="restore-icon">🔄</span>
                                RESTORE
                            </button>
                        `;
                        accountCard.appendChild(deletedOverlay);
                        
                        // Mark as previously deleted in the status
                        const statusElement = document.getElementById(`status-${accountId}`);
                        if (statusElement) {
                            statusElement.textContent = 'PREVIOUSLY DELETED';
                            statusElement.style.color = '#ff0000';
                            statusElement.style.fontWeight = 'bold';
                            statusElement.classList.add('status-previously-deleted');
                            
                            // Add red styling to the credential item container
                            const credentialItem = statusElement.closest('.credential-item');
                            if (credentialItem) {
                                credentialItem.classList.add('status-previously-deleted');
                            }
                        }
                        
                        // Mark as previously deleted in localStorage
                        localStorage.setItem(`previouslyDeleted_${accountId}`, 'true');
                        
                        // Add to previously deleted accounts list
                        let previouslyDeletedAccounts = JSON.parse(localStorage.getItem('previouslyDeletedAccounts') || '[]');
                        if (!previouslyDeletedAccounts.includes(accountId)) {
                            previouslyDeletedAccounts.push(accountId);
                            localStorage.setItem('previouslyDeletedAccounts', JSON.stringify(previouslyDeletedAccounts));
                        }
                        
                        updateStats();
                        
                        // Check if all accounts are deleted
                        const visibleAccounts = document.querySelectorAll('.account-card:not(.deleted-account)');
                        if (visibleAccounts.length === 0) {
                            const container = document.getElementById('accounts-container');
                            container.innerHTML = `
                                <div class="no-accounts">
                                    <div class="icon">🔐</div>
                                    <p>No active accounts.</p>
                                    <p>All accounts have been deleted. Use the restore button to bring them back!</p>
                                </div>
                            `;
                        }
                        
                        // Store deleted account ID in localStorage
                        let deletedAccounts = JSON.parse(localStorage.getItem('deletedAccounts') || '[]');
                        if (!deletedAccounts.includes(accountId)) {
                            deletedAccounts.push(accountId);
                            localStorage.setItem('deletedAccounts', JSON.stringify(deletedAccounts));
                        }
                        
                        // Show success message
                        showNotification('Account deleted successfully!', 'success');
                    }, 500);
                }
            }
        }
        
        // Restore account functionality
        function restoreAccount(accountId, serviceName, email) {
            if (confirm(`Are you sure you want to restore this ${serviceName} account?\\nEmail: ${email}`)) {
                const accountCard = document.getElementById(accountId);
                if (accountCard) {
                    // Remove deleted styling
                    accountCard.classList.remove('deleted-account');
                    accountCard.style.opacity = '1';
                    
                    // Remove deleted overlay
                    const deletedOverlay = accountCard.querySelector('.deleted-overlay');
                    if (deletedOverlay) {
                        deletedOverlay.remove();
                    }
                    
                    // Mark as previously deleted in the status
                    const statusElement = document.getElementById(`status-${accountId}`);
                    if (statusElement) {
                        statusElement.textContent = 'PREVIOUSLY DELETED';
                        statusElement.style.color = '#ff0000';
                        statusElement.style.fontWeight = 'bold';
                    }
                    
                    updateStats();
                    
                    // Remove from localStorage
                    let deletedAccounts = JSON.parse(localStorage.getItem('deletedAccounts') || '[]');
                    deletedAccounts = deletedAccounts.filter(id => id !== accountId);
                    localStorage.setItem('deletedAccounts', JSON.stringify(deletedAccounts));
                    
                    // Show success message
                    showNotification('Account restored successfully!', 'success');
                }
            }
        }
        
        // Hide deleted accounts on page load
        function hideDeletedAccounts() {
            const deletedAccounts = JSON.parse(localStorage.getItem('deletedAccounts') || '[]');
            deletedAccounts.forEach(accountId => {
                const accountCard = document.getElementById(accountId);
                if (accountCard) {
                    // Mark as deleted
                    accountCard.classList.add('deleted-account');
                    accountCard.style.opacity = '0.3';
                    
                    // Add deleted overlay if not already present
                    if (!accountCard.querySelector('.deleted-overlay')) {
                        const serviceBadge = accountCard.querySelector('.service-badge');
                        const serviceName = serviceBadge ? serviceBadge.textContent : 'Unknown';
                        const emailElement = accountCard.querySelector('.credential-value');
                        const email = emailElement ? emailElement.textContent : '';
                        
                        const deletedOverlay = document.createElement('div');
                        deletedOverlay.className = 'deleted-overlay';
                        deletedOverlay.innerHTML = `
                            <div class="deleted-text">DELETED</div>
                            <button class="restore-button" onclick="restoreAccount('${accountId}', '${serviceName}', '${email}')">
                                <span class="restore-icon">🔄</span>
                                RESTORE
                            </button>
                        `;
                        accountCard.appendChild(deletedOverlay);
                    }
                }
            });
            
            // Apply red styling to previously deleted accounts
            const previouslyDeletedAccounts = JSON.parse(localStorage.getItem('previouslyDeletedAccounts') || '[]');
            previouslyDeletedAccounts.forEach(accountId => {
                const statusElement = document.getElementById(`status-${accountId}`);
                if (statusElement) {
                    statusElement.textContent = 'PREVIOUSLY DELETED';
                    statusElement.style.color = '#ff0000';
                    statusElement.style.fontWeight = 'bold';
                    statusElement.classList.add('status-previously-deleted');
                    
                    // Add red styling to the credential item container
                    const credentialItem = statusElement.closest('.credential-item');
                    if (credentialItem) {
                        credentialItem.classList.add('status-previously-deleted');
                    }
                }
            });
        }
        
        // Clear all deleted accounts (reset function)
        function resetDeletedAccounts() {
            if (confirm('Are you sure you want to restore all deleted accounts?')) {
                localStorage.removeItem('deletedAccounts');
                location.reload();
            }
        }
        
        // Restore all deleted accounts function
        function restoreAllDeletedAccounts() {
            const deletedAccounts = JSON.parse(localStorage.getItem('deletedAccounts') || '[]');
            if (deletedAccounts.length === 0) {
                showNotification('No deleted accounts to restore!', 'info');
                return;
            }
            
            if (confirm(`Are you sure you want to restore all ${deletedAccounts.length} deleted accounts?`)) {
                // Restore all deleted accounts
                deletedAccounts.forEach(accountId => {
                    const accountCard = document.getElementById(accountId);
                    if (accountCard) {
                        // Remove deleted styling
                        accountCard.classList.remove('deleted-account');
                        accountCard.style.opacity = '1';
                        
                        // Remove deleted overlay
                        const deletedOverlay = accountCard.querySelector('.deleted-overlay');
                        if (deletedOverlay) {
                            deletedOverlay.remove();
                        }
                        
                        // Mark as previously deleted in the status
                        const statusElement = document.getElementById(`status-${accountId}`);
                        if (statusElement) {
                            statusElement.textContent = 'PREVIOUSLY DELETED';
                            statusElement.style.color = '#ff0000';
                            statusElement.style.fontWeight = 'bold';
                        }
                    }
                });
                
                // Clear localStorage
                localStorage.removeItem('deletedAccounts');
                
                // Update stats
                updateStats();
                
                // Show success message
                showNotification(`Successfully restored ${deletedAccounts.length} accounts!`, 'success');
            }
        }
        
        // Show notification
        function showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'success' ? 'linear-gradient(45deg, #00ff41, #00d4ff)' : type === 'error' ? 'linear-gradient(45deg, #ff4444, #ff8800)' : 'linear-gradient(45deg, #00d4ff, #00ff41)'};
                color: #000;
                padding: 15px 25px;
                border-radius: 10px;
                font-family: 'Orbitron', monospace;
                font-weight: 600;
                z-index: 1000;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
                max-width: 400px;
                word-wrap: break-word;
            `;
            
            document.body.appendChild(notification);
            
            // Animate in
            setTimeout(() => {
                notification.style.transform = 'translateX(0)';
            }, 100);
            
            // Remove after 3 seconds
            setTimeout(() => {
                notification.style.transform = 'translateX(100%)';
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 3000);
        }
        
        // Move deleted/previously deleted accounts to the bottom
        function moveDeletedToBottom() {
            const grid = document.querySelector('.accounts-grid');
            if (!grid) return;
            const cards = Array.from(grid.children);
            const active = [];
            const deleted = [];
            cards.forEach(card => {
                if (card.classList.contains('deleted-account') || card.querySelector('.credential-value.status-previously-deleted')) {
                    deleted.push(card);
                } else {
                    active.push(card);
                }
            });
            // Remove all
            cards.forEach(card => grid.removeChild(card));
            // Re-add in order: active first, then deleted
            active.concat(deleted).forEach(card => grid.appendChild(card));
        }
        
        // Call after any delete/restore
        function afterAccountChange() {
            moveDeletedToBottom();
            updateStats();
        }
        
        // Patch deleteAccount and restoreAccount to call afterAccountChange
        // (insert after their logic)
        // ...
        // In deleteAccount, after marking as deleted:
        moveDeletedToBottom();
        // ...
        // In restoreAccount, after restoring:
        moveDeletedToBottom();
        // ...
        // On page load:
        document.addEventListener('DOMContentLoaded', moveDeletedToBottom);
"""
            
            # Insert the delete script before the closing script tag
            content = content.replace(
                '    </script>\n</body>',
                f'{delete_script}\n    </script>\n</body>'
            )
        
        # Write the updated content back
        with open(base_file, 'w', encoding='utf-8') as file:
            file.write(content)
        
        self.log_signal.emit(f"✨ Account saved to {base_file} with delete functionality! ✨\n")

    def _create_base_html_file(self):
        """Create the base HTML file with template"""
        template_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Account Generator - All Accounts</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            font-family: 'Rajdhani', sans-serif;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 10;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }
        
        .title {
            font-family: 'Orbitron', monospace;
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(45deg, #00ff41, #00d4ff, #ff00ff, #ffff00);
            background-size: 300% 300%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: titleGlow 3s ease-in-out infinite;
            text-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
            margin-bottom: 20px;
        }
        
        @keyframes titleGlow {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        .subtitle {
            font-size: 1.5rem;
            color: #00ff41;
            font-weight: 300;
            letter-spacing: 3px;
            animation: pulse 2s ease-in-out infinite;
            margin-bottom: 20px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        .stats-bar {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 65, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            align-items: center;
            animation: slideInDown 1s ease-out forwards;
        }
        
        @keyframes slideInDown {
            from {
                transform: translateY(-50px);
                opacity: 0;
            }
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-family: 'Orbitron', monospace;
            font-size: 2rem;
            font-weight: 700;
            color: #00ff41;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .accounts-grid {
            display: flex;
            flex-direction: column;
            gap: 30px;
            margin-top: 30px;
        }
        
        .account-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 65, 0.3);
            border-radius: 20px;
            padding: 30px;
            position: relative;
            overflow: hidden;
            transform: translateY(50px);
            opacity: 0;
            animation: slideInUp 1s ease-out forwards;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .account-card:hover {
            transform: translateY(-10px);
            border-color: #00ff41;
            box-shadow: 0 30px 60px rgba(0, 255, 65, 0.2);
        }
        
        .account-card::after {
            content: '';
            position: absolute;
            top: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: radial-gradient(circle, rgba(0, 255, 65, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            animation: float 3s ease-in-out infinite;
        }
        
        .account-card::before {
            content: '';
            position: absolute;
            bottom: 30px;
            left: 30px;
            width: 40px;
            height: 40px;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%);
            border-radius: 50%;
            animation: float 4s ease-in-out infinite reverse;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }
        
        @keyframes slideInUp {
            to {
                transform: translateY(0);
                opacity: 1;
            }
        }
        
        .account-card .bubble {
            position: absolute;
            background: radial-gradient(circle, rgba(0, 255, 65, 0.2) 0%, transparent 70%);
            border-radius: 50%;
            animation: bubbleFloat 6s ease-in-out infinite;
        }
        
        .account-card .bubble:nth-child(1) {
            width: 30px;
            height: 30px;
            top: 10%;
            left: 10%;
            animation-delay: 0s;
        }
        
        .account-card .bubble:nth-child(2) {
            width: 20px;
            height: 20px;
            top: 60%;
            right: 15%;
            animation-delay: 2s;
        }
        
        .account-card .bubble:nth-child(3) {
            width: 25px;
            height: 25px;
            bottom: 20%;
            left: 20%;
            animation-delay: 4s;
        }
        
        @keyframes bubbleFloat {
            0%, 100% { transform: translateY(0px) scale(1); opacity: 0.7; }
            50% { transform: translateY(-15px) scale(1.1); opacity: 1; }
        }
        
        .service-badge {
            display: inline-block;
            background: linear-gradient(45deg, #00ff41, #00d4ff);
            color: #000;
            padding: 12px 25px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 25px;
            animation: badgePulse 2s ease-in-out infinite;
            box-shadow: 0 10px 30px rgba(0, 255, 65, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .service-badge::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
            animation: badgeShine 3s ease-in-out infinite;
        }
        
        @keyframes badgeShine {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes badgePulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.05) rotate(2deg); }
        }
        
        .credential-item {
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.1), rgba(0, 212, 255, 0.1));
            border: 2px solid rgba(0, 255, 65, 0.3);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 25px rgba(0, 255, 65, 0.1);
        }
        
        .credential-item:hover {
            border-color: #00ff41;
            background: linear-gradient(135deg, rgba(0, 255, 65, 0.2), rgba(0, 212, 255, 0.2));
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 35px rgba(0, 255, 65, 0.2);
        }
        
        .credential-item::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ff41, #00d4ff, #ff00ff, #ffff00);
            border-radius: 22px;
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .credential-item:hover::before {
            opacity: 0.3;
        }
        
        .credential-label {
            font-family: 'Orbitron', monospace;
            font-size: 0.8rem;
            color: #00ff41;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
            text-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
        }
        
        .credential-value {
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.1rem;
            color: #ffffff;
            font-weight: 500;
            word-break: break-all;
            background: rgba(0, 0, 0, 0.3);
            padding: 12px 15px;
            border-radius: 15px;
            border: 1px solid rgba(0, 255, 65, 0.2);
            backdrop-filter: blur(5px);
            transition: all 0.3s ease;
        }
        
        .credential-value:hover {
            background: rgba(0, 255, 65, 0.1);
            border-color: #00ff41;
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.2);
        }
        
        .timestamp {
            text-align: center;
            margin-top: 20px;
            font-size: 0.9rem;
            color: #888;
            font-style: italic;
        }
        
        .success-indicator {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 15px;
            height: 15px;
            background: #00ff41;
            border-radius: 50%;
            animation: successPulse 2s ease-in-out infinite;
        }
        
        @keyframes successPulse {
            0%, 100% {
                transform: scale(1);
                box-shadow: 0 0 0 0 rgba(0, 255, 65, 0.7);
            }
            50% {
                transform: scale(1.2);
                box-shadow: 0 0 0 8px rgba(0, 255, 65, 0);
            }
        }
        
        .delete-button {
            background: linear-gradient(45deg, #ff4444, #ff8800);
            color: #fff;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-family: 'Orbitron', monospace;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            margin-top: 20px;
            width: 100%;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .delete-button:hover {
            transform: scale(1.02);
            box-shadow: 0 5px 15px rgba(255, 68, 68, 0.4);
            background: linear-gradient(45deg, #ff6666, #ffaa00);
        }
        
        .delete-icon {
            font-size: 1.1rem;
        }
        
        /* Deleted account styles */
        .deleted-account {
            opacity: 0.3 !important;
            position: relative;
            filter: grayscale(50%);
        }
        
        .deleted-account:hover {
            opacity: 0.5 !important;
        }
        
        .deleted-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 10;
            border: 2px solid #ff4444;
        }
        
        .deleted-text {
            font-family: 'Orbitron', monospace;
            font-size: 1.5rem;
            font-weight: 900;
            color: #ff4444;
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 20px;
            text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
            animation: deletedPulse 2s ease-in-out infinite;
        }
        
        @keyframes deletedPulse {
            0%, 100% { opacity: 0.7; }
            50% { opacity: 1; }
        }
        
        .restore-button {
            background: linear-gradient(45deg, #00ff41, #00d4ff);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-family: 'Orbitron', monospace;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        
        .restore-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.4);
            background: linear-gradient(45deg, #00ff66, #00e6ff);
        }
        
        .restore-icon {
            font-size: 1rem;
        }
        
        /* Previously deleted status styling */
        .credential-item.status-previously-deleted {
            background: linear-gradient(135deg, rgba(255, 0, 0, 0.2), rgba(255, 68, 0, 0.2));
            border: 2px solid rgba(255, 0, 0, 0.5);
            box-shadow: 0 8px 25px rgba(255, 0, 0, 0.3);
            animation: redPulse 2s ease-in-out infinite;
        }
        
        .credential-item.status-previously-deleted:hover {
            border-color: #ff0000;
            background: linear-gradient(135deg, rgba(255, 0, 0, 0.3), rgba(255, 68, 0, 0.3));
            box-shadow: 0 12px 35px rgba(255, 0, 0, 0.4);
        }
        
        .credential-item.status-previously-deleted::before {
            background: linear-gradient(45deg, #ff0000, #ff4400, #ff8800, #ffcc00);
        }
        
        @keyframes redPulse {
            0%, 100% { 
                box-shadow: 0 8px 25px rgba(255, 0, 0, 0.3);
                transform: scale(1);
            }
            50% { 
                box-shadow: 0 12px 35px rgba(255, 0, 0, 0.5);
                transform: scale(1.02);
            }
        }
        
        .credential-value.status-previously-deleted {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid rgba(255, 0, 0, 0.5);
            color: #ff4444;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
            animation: textGlow 1.5s ease-in-out infinite;
        }
        
        .credential-value.status-previously-deleted:hover {
            background: rgba(255, 0, 0, 0.3);
            border-color: #ff0000;
            box-shadow: 0 5px 15px rgba(255, 0, 0, 0.4);
        }
        
        @keyframes textGlow {
            0%, 100% { 
                text-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
                color: #ff4444;
            }
            50% { 
                text-shadow: 0 0 20px rgba(255, 0, 0, 0.8);
                color: #ff6666;
            }
        }
        
        .floating-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .particle {
            position: absolute;
            width: 3px;
            height: 3px;
            background: #00ff41;
            border-radius: 50%;
            animation: float 8s infinite linear;
        }
        
        .particle:nth-child(1) { left: 5%; animation-delay: 0s; }
        .particle:nth-child(2) { left: 15%; animation-delay: 1s; }
        .particle:nth-child(3) { left: 25%; animation-delay: 2s; }
        .particle:nth-child(4) { left: 35%; animation-delay: 3s; }
        .particle:nth-child(5) { left: 45%; animation-delay: 4s; }
        .particle:nth-child(6) { left: 55%; animation-delay: 5s; }
        .particle:nth-child(7) { left: 65%; animation-delay: 0s; }
        .particle:nth-child(8) { left: 75%; animation-delay: 1s; }
        .particle:nth-child(9) { left: 85%; animation-delay: 2s; }
        .particle:nth-child(10) { left: 95%; animation-delay: 3s; }
        
        @keyframes float {
            0% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }
        }
        
        .no-accounts {
            text-align: center;
            padding: 100px 20px;
            color: #888;
            font-size: 1.2rem;
        }
        
        .no-accounts .icon {
            font-size: 4rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        
        @media (max-width: 768px) {
            .title {
                font-size: 2.5rem;
            }
            
            .accounts-grid {
                grid-template-columns: 1fr;
            }
            
            .account-card {
                padding: 20px;
            }
            
            .stats-bar {
                flex-direction: column;
                gap: 20px;
            }
        }
        
        .global-restore-button {
            background: linear-gradient(45deg, #00ff41, #00d4ff);
            color: #000;
            border: none;
            padding: 12px 25px;
            border-radius: 15px;
            font-family: 'Orbitron', monospace;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin: 0 auto;
            box-shadow: 0 5px 15px rgba(0, 255, 65, 0.3);
        }
        
        .global-restore-button:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 25px rgba(0, 255, 65, 0.5);
            background: linear-gradient(45deg, #00ff66, #00e6ff);
        }
        
        .global-restore-button:active {
            transform: scale(0.95);
        }
    </style>
</head>
<body>
    <div class="floating-particles">
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
        <div class="particle"></div>
    </div>
    
    <div class="container">
        <div class="header">
            <h1 class="title">ACCOUNT GENERATOR</h1>
            <p class="subtitle">High-Tech Automation Suite - All Accounts</p>
            <button class="global-restore-button" onclick="restoreAllDeletedAccounts()">
                <span class="restore-icon">🔄</span>
                RESTORE ALL DELETED ACCOUNTS
            </button>
        </div>
        
        <div class="stats-bar">
            <div class="stat-item">
                <span class="stat-number" id="total-accounts">0</span>
                <span class="stat-label">Total Accounts</span>
            </div>
        </div>
        
        <div class="accounts-grid" id="accounts-container">
            <div class="no-accounts">
                <div class="icon">🔐</div>
                <p>No accounts generated yet.</p>
                <p>Start the automation to see your accounts here!</p>
            </div>
        </div>
    </div>
    
    <script>
        // Update stats when accounts are added
        function updateStats() {
            const accounts = document.querySelectorAll('.account-card');
            const totalAccounts = accounts.length;
            
            document.getElementById('total-accounts').textContent = totalAccounts;
        }
        
        // Add interactive effects
        document.addEventListener('DOMContentLoaded', function() {
            updateStats();
            hideDeletedAccounts(); // Hide deleted accounts on page load
            
            // Add hover effects to account cards
            const accountCards = document.querySelectorAll('.account-card');
            accountCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
            
            // Add click effect to title
            const title = document.querySelector('.title');
            title.addEventListener('click', function() {
                this.style.animation = 'none';
                setTimeout(() => {
                    this.style.animation = 'titleGlow 3s ease-in-out infinite';
                }, 10);
            });
        });
        
        // Auto-update stats when new accounts are added
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    updateStats();
                }
            });
        });
        
        observer.observe(document.getElementById('accounts-container'), {
            childList: true,
            subtree: true
        });
    </script>
</body>
</html>"""
        
        with open('accounts.html', 'w', encoding='utf-8') as file:
            file.write(template_content)

    def generate_secure_password(self, length=16):
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    def click_generate_new(self, driver):
        try:
            generate_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(text(), 'Generate New')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", generate_button)
            generate_button.click()
        except Exception as e:
            self.log_signal.emit(f"Could not click the button: {e}\n")

    def create_playit_account(self, driver, email):
        self.log_signal.emit("Automating Playit.gg account creation...\n")
        emailnator_tab = driver.window_handles[0]
        driver.execute_script("window.open('');")
        registration_tab = driver.window_handles[-1]
        driver.switch_to.window(registration_tab)
        driver.get("https://playit.gg/login/create?redirect=%2Faccount%2Fagents%3F")
        try:
            password = self.generate_secure_password()
            email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
            password_input = driver.find_element(By.NAME, "password")
            confirm_password_input = driver.find_element(By.NAME, "confirm-password")
            email_input.send_keys(email)
            password_input.send_keys(password)
            confirm_password_input.send_keys(password)
            self.log_signal.emit("Filled out the registration form.\n")
            create_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @name='_action' and @value='create']")))
            create_button.click()
            self.log_signal.emit("Submitted the registration form.\n")
            time.sleep(2)
            driver.switch_to.window(emailnator_tab)
            driver.switch_to.window(registration_tab)
            driver.close()
            driver.switch_to.window(emailnator_tab)
            self.log_signal.emit("Registration tab closed. Now waiting for verification email...\n")
            for i in range(15):
                try:
                    reload_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "reload")))
                    reload_button.click()
                    self.log_signal.emit(f"Reloaded inbox, attempt {i+1}...\n")
                    verification_email_link = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//td[contains(., 'playit.gg Support')]")
                    ))
                    verification_email_link.click()
                    self.log_signal.emit("Found and opened verification email.\n")
                    break
                except Exception:
                    if i == 14:
                        self.log_signal.emit("Could not find verification email after 90 seconds.\n")
                        raise
                    time.sleep(1)
            self.log_signal.emit("\nACTION REQUIRED: Please click the verification link in the email.\n")
            self.log_signal.emit("The script will continue automatically once the verification tab is detected...\n")
            verification_tab_found = False
            for _ in range(30):
                all_handles = driver.window_handles
                for handle in all_handles:
                    if handle != emailnator_tab:
                        driver.switch_to.window(handle)
                        if driver.current_url.startswith("https://playit.gg/account/settings/account/verify-email"):
                            self.log_signal.emit("Verification tab detected. Resuming automation.\n")
                            verification_tab_found = True
                            break
                if verification_tab_found:
                    break
                driver.switch_to.window(emailnator_tab)
                time.sleep(1)
            if not verification_tab_found:
                raise Exception("Timed out waiting for verification tab.")
            verify_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'blue') and contains(., 'Verify Email')]"))
            )
            verify_button.click()
            self.log_signal.emit("Clicked the final 'Verify Email' button.\n")
            self.save_credentials("Playit.gg", email, password)
            self.log_signal.emit(f"\nSuccessfully created and verified account for {email}.\n")
            self.log_signal.emit(f"Credentials have been appended to accounts.txt.\n")
            self.log_signal.emit(f"Password: {password}\n")
        except Exception as e:
            self.log_signal.emit(f"An error occurred during Playit.gg automation: {e}\n")

    def get_gmail_address(self, driver):
        self.log_signal.emit("Searching for a Gmail address...\n")
        for _ in range(10):
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Email Address']")))
            email_value = email_field.get_attribute("value")
            if email_value and "gmail.com" in email_value:
                try:
                    go_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and @name='goBtn']")))
                    driver.execute_script("arguments[0].scrollIntoView(true);", go_button)
                    go_button.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", go_button)
                self.log_signal.emit(f"Successfully found email: {email_value}\n")
                return email_value
            else:
                self.log_signal.emit("Not a Gmail address, generating a new one...\n")
                old_email_value = email_value
                try:
                    generate_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[@type='button' and contains(text(), 'Generate New')]"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", generate_button)
                    generate_button.click()
                except Exception:
                    self.log_signal.emit("Standard click failed, trying JavaScript click...\n")
                    driver.execute_script("arguments[0].click();", generate_button)
                WebDriverWait(driver, 10).until(
                    lambda d: d.find_element(By.CSS_SELECTOR, "input[placeholder='Email Address']").get_attribute("value") != old_email_value
                )
        self.log_signal.emit("Failed to find a Gmail address after multiple attempts.\n")
        return None

    def run_automation(self, service):
        driver = None
        try:
            driver = self.setup_driver()
            driver.get("https://www.emailnator.com/")
            try:
                cookie_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "accept-cookies-usage"))
                )
                cookie_button.click()
            except Exception as e:
                self.log_signal.emit(f"No cookie consent popup found or could not click: {e}\n")
            email_value = None
            while True:
                try:
                    email_field = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Email Address']"))
                    )
                    email_value = email_field.get_attribute("value")
                    if email_value and "gmail.com" in email_value:
                        self.log_signal.emit("success\n")
                        self.save_email_to_file(email_value)
                        go_button = driver.find_element(By.XPATH, "//button[@type='button' and @name='goBtn']")
                        go_button.click()
                        self.log_signal.emit(f"\nSuccessfully found email: {email_value}\n")
                        self.log_signal.emit("The inbox for this email is now open in the first tab.\n")
                        break
                    else:
                        self.click_generate_new(driver)
                        time.sleep(2)
                except Exception as e:
                    self.log_signal.emit(f"An error occurred while getting email: {e}\n")
                    email_value = None
                    break
            if email_value:
                    self.create_playit_account(driver, email_value)
            self.log_signal.emit("\n[INFO] Automation complete. You may close the browser.\n")
            input("Press Enter to close the browser...")
        except Exception as e:
            self.log_signal.emit(f"An error occurred during automation: {e}\n")
        finally:
            if driver:
                driver.quit()
        self.log_signal.emit("\n[INFO] Automation finished. Ready for next task.\n")
        # Emit signals to update UI in main thread
        self.log_signal.emit("READY_SIGNAL")

    def enable_buttons(self):
        for btn in self.buttons:
            btn.setEnabled(True)

    def disable_buttons(self):
        for btn in self.buttons:
            btn.setEnabled(False)

    def _on_service_clicked(self, name):
        self.set_status(f"{name.upper()} SELECTED", color="#ffb300")
        # Clear the log area before starting automation
        self.log.clear()
        self.disable_buttons()
        # Start automation in a thread
        def run():
            try:
                self.run_automation(name.lower())
            except Exception as e:
                self.log_signal.emit(f"Thread error: {e}\n")
        self._automation_thread = threading.Thread(target=run)
        self._automation_thread.start()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Custom exit button (top right)
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(28, 28)
        exit_btn.setStyleSheet('''
            QPushButton {
                background: rgba(0,0,0,0.0);
                color: #ff4c4c;
                border: none;
                font-size: 15px;
                border-radius: 14px;
            }
            QPushButton:hover {
                background: #ff4c4c;
                color: #fff;
            }
        ''')
        exit_btn.clicked.connect(self.close_app)
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_layout = QHBoxLayout()
        exit_layout.addStretch(1)
        exit_layout.addWidget(exit_btn)
        exit_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(exit_layout)

        # Title (no accent bar, no background)
        title = QLabel("ACCOUNT AUTOMATION SUITE")
        title.setFont(QFont("Roboto Mono", 19, QFont.Bold))
        title.setStyleSheet("color: #e0e0e0; background: transparent; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle (no background)
        subtitle = QLabel("TACTICAL ACCOUNT GENERATOR CONSOLE")
        subtitle.setFont(QFont("Roboto Mono", 10))
        subtitle.setStyleSheet("color: #6c757d; background: transparent; border: none;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Button Row
        button_row = QHBoxLayout()
        button_row.setSpacing(14)
        self.buttons = []
        for name, color in [
            ("Playit.gg", "#444950")
        ]:
            btn = QPushButton(name.upper())
            btn.setFont(QFont("Roboto Mono", 11, QFont.Bold))
            btn.setStyleSheet(self._button_style(color))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(32)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.pressed.connect(self._play_click_sound)
            btn.clicked.connect(lambda checked, n=name: self._on_service_clicked(n))
            self.buttons.append(btn)
            button_row.addWidget(btn)
        layout.addLayout(button_row)

        # Log Area
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setFont(QFont("Roboto Mono", 11))
        self.log.setStyleSheet(self._log_style())
        self.log.setMinimumHeight(100)
        layout.addWidget(self.log)

        # Status Bar (no background, no border)
        self.status = QLabel()
        self.status.setFont(QFont("Roboto Mono", 10))
        self.status.setStyleSheet("color: #00ff41; background: transparent; border: none; padding: 4px 0 0 0;")
        self.set_status("READY", color="#00ff41")
        layout.addWidget(self.status)

    def _main_style(self):
        return """
            QWidget {
                background: #181a1b;
                border-radius: 0px;
            }
        """

    def _button_style(self, color):
        return f"""
            QPushButton {{
                background: #23272a;
                color: #e0e0e0;
                border: 1.5px solid #444950;
                border-radius: 4px;
                padding: 6px 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }}
            QPushButton:hover, QPushButton:focus {{
                background: #23272a;
                color: #00ff41;
                border: 2px solid #00ff41;
            }}
            QPushButton:pressed {{
                background: #181a1b;
                color: #00ff41;
                border: 2px solid #00ff41;
            }}
        """

    def _log_style(self):
        return """
            QTextEdit {
                background: rgba(30,32,34,0.85);
                color: #b0ffb0;
                border-radius: 8px;
                border: 2px solid #00ff41;
                padding: 6px;
                font-family: 'Roboto Mono', 'Consolas', 'SF Mono', monospace;
                font-size: 12px;
                selection-background-color: #00ff41;
                selection-color: #181a1b;
            }
        """

    def _setup_sound(self):
        self.sound = QSoundEffect()
        sound_path = os.path.join(os.path.dirname(__file__), "click.wav")
        if os.path.exists(sound_path):
            self.sound.setSource(QUrl.fromLocalFile(sound_path))
        else:
            self.sound = None

    def _play_click_sound(self):
        if self.sound:
            self.sound.play()

    def set_status(self, text, color="#4caf50"):
        self.status.setText(f'<span style="color:{color};font-size:1.2em;">●</span> {text}')

    def _animate_log(self, text, delay=10):
        # Typewriter animation for log
        self.log.moveCursor(self.log.textCursor().End)
        def type_char(index=0):
            if index < len(text):
                self.log.insertPlainText(text[index])
                QTimer.singleShot(delay, lambda: type_char(index + 1))
            else:
                self.log.moveCursor(self.log.textCursor().End)
        type_char()

    def _update_gradient(self):
        self._gradient_phase = (self._gradient_phase + 1) % 360
        self.update()

    # Make window movable
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)
        # Layered animated background
        angle1 = (self._gradient_phase / 360.0) * 2 * 3.14159
        angle2 = ((self._gradient_phase + 120) / 360.0) * 2 * 3.14159
        x1 = 0.5 + 0.5 * np.cos(angle1)
        y1 = 0.5 + 0.5 * np.sin(angle1)
        x2 = 0.5 - 0.5 * np.cos(angle1)
        y2 = 0.5 - 0.5 * np.sin(angle1)
        grad1 = QLinearGradient(rect.width() * x1, rect.height() * y1, rect.width() * x2, rect.height() * y2)
        grad1.setColorAt(0, QColor("#181a1b"))
        grad1.setColorAt(0.5, QColor("#23272a"))
        grad1.setColorAt(0.98, QColor("#232a1a"))
        grad1.setColorAt(1, QColor("#003f1a"))
        painter.setBrush(grad1)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 18, 18)
        # Second, slower gradient for depth
        x3 = 0.5 + 0.5 * np.cos(angle2)
        y3 = 0.5 + 0.5 * np.sin(angle2)
        x4 = 0.5 - 0.5 * np.cos(angle2)
        y4 = 0.5 - 0.5 * np.sin(angle2)
        grad2 = QLinearGradient(rect.width() * x3, rect.height() * y3, rect.width() * x4, rect.height() * y4)
        grad2.setColorAt(0, QColor(0, 255, 255, 30))
        grad2.setColorAt(1, QColor(255, 0, 255, 20))
        painter.setBrush(grad2)
        painter.drawRoundedRect(rect, 18, 18)

        # Draw animated squiggly border with gradient and glow
        border_grad = QLinearGradient(0, 0, rect.width(), rect.height())
        border_grad.setColorAt(0, QColor("#00ff41"))
        border_grad.setColorAt(0.5, QColor("#00eaff"))
        border_grad.setColorAt(1, QColor("#ff00ea"))
        pen = QPen(border_grad, 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        amplitude = 6
        freq = 2 * 3.14159 / 80
        phase = self._gradient_phase / 10.0
        # Glow: draw a thinner, more subtle squiggle underneath
        glow_pen = QPen(border_grad, 3)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        glow_pen.setColor(QColor(0,255,65,60))
        painter.setPen(glow_pen)
        for x in range(0, rect.width(), 2):
            y = -int(amplitude * np.sin(freq * x + phase))
            painter.drawPoint(x, y)
            painter.drawPoint(x, rect.height() - 1 + int(amplitude * np.sin(freq * x + phase + 1)))
        for y in range(0, rect.height(), 2):
            painter.drawPoint(-int(amplitude * np.sin(freq * y + phase + 2)), y)
            painter.drawPoint(rect.width() - 1 + int(amplitude * np.sin(freq * y + phase + 3)), y)
        # Main squiggle
        painter.setPen(pen)
        for x in range(0, rect.width(), 2):
            y = -int(amplitude * np.sin(freq * x + phase))
            painter.drawPoint(x, y)
            painter.drawPoint(x, rect.height() - 1 - int(amplitude * np.sin(freq * x + phase + 1)))
        for y in range(0, rect.height(), 2):
            painter.drawPoint(int(amplitude * np.sin(freq * y + phase + 2)), y)
            painter.drawPoint(rect.width() - 1 - int(amplitude * np.sin(freq * y + phase + 3)), y)

        super().paintEvent(event)

    def close_app(self):
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HighTechGUI()
    gui.show()
    sys.exit(app.exec_()) 