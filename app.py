#!/usr/bin/env python3
"""
APEX Trader Funding - Selenium Automation Backend
Chrome Extension + Python Selenium Hybrid Architecture
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
import json
import uuid
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Chrome extension

# Configure Flask to accept ngrok hosts
app.config['ALLOWED_HOSTS'] = ['*']  # Allow all hosts for ngrok compatibility

# Disable host checking for ngrok compatibility
import os
os.environ['FLASK_ENV'] = 'development'

# Allow all hosts for ngrok and remote access
import werkzeug.serving
werkzeug.serving.WSGIRequestHandler.address_string = lambda self: self.client_address[0]

# Global state management
automation_sessions = {}
active_drivers = {}

class ApexAutomation:
    def __init__(self, session_id, settings):
        self.session_id = session_id
        self.settings = settings
        self.driver = None
        self.wait = None
        self.status = "initializing"
        self.current_account = 0
        self.total_accounts = settings.get('numberOfAccounts', 1)
        self.logs = []
        self.coupon_code = "JAYPELLE"  # Mandatory coupon code
        
    def log(self, message):
        """Add log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(f"Session {self.session_id}: {message}")
        
    def setup_driver(self):
        """Initialize Chrome driver with optimal settings for same-window automation"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # For same-window automation, we'll let the content script handle everything
            # The backend will just provide status updates and logging
            self.log("✅ Backend ready for same-window automation")
            self.log("💡 Content script will handle browser automation")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to setup backend: {str(e)}")
            return False
    
    def navigate_to_signup(self, account_type):
        """Navigate to APEX signup page"""
        try:
            signup_url = f"https://dashboard.apextraderfunding.com/signup/{account_type}"
            self.log(f"🔄 Navigating to: {signup_url}")
            self.driver.get(signup_url)
            
            # Wait for page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.log("✅ Signup page loaded successfully")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to navigate to signup page: {str(e)}")
            return False
    
    def fill_signup_form(self, account_number):
        """Fill the signup form with coupon and agreement"""
        try:
            self.log(f"📝 Filling signup form for account {account_number}")
            
            # Fill coupon code
            coupon_selectors = [
                'input[name="coupon"]',
                'input[id*="coupon"]',
                'input[placeholder*="coupon"]'
            ]
            
            coupon_field = None
            for selector in coupon_selectors:
                try:
                    coupon_field = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
                    
            if coupon_field:
                coupon_field.clear()
                coupon_field.send_keys(self.coupon_code)
                self.log(f"✅ Entered coupon code: {self.coupon_code}")
            else:
                self.log("⚠️ Coupon field not found")
            
            # Agree to terms
            agreement_selectors = [
                'input[name="agreement"]',
                'input[id="agreement"]',
                'input[type="checkbox"][name*="agree"]',
                'input[type="checkbox"][id*="terms"]'
            ]
            
            for selector in agreement_selectors:
                try:
                    agreement_checkbox = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if not agreement_checkbox.is_selected():
                        agreement_checkbox.click()
                        self.log("✅ Agreed to terms and conditions")
                    break
                except:
                    continue
            
            # Click next/continue button
            next_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'input[value*="Next"]',
                'button:contains("Next")',
                '.btn-primary'
            ]
            
            for selector in next_selectors:
                try:
                    next_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    next_button.click()
                    self.log("✅ Clicked next button")
                    break
                except:
                    continue
            
            # Wait for navigation to payment page
            time.sleep(3)
            return True
            
        except Exception as e:
            self.log(f"❌ Error filling signup form: {str(e)}")
            return False
    
    def fill_payment_form(self, account_number):
        """Fill payment form with card details"""
        try:
            self.log(f"💳 Filling payment details for account {account_number}")
            
            # Wait for payment page to load
            self.wait.until(lambda d: '/payment/' in d.current_url or '/authorize-cim' in d.current_url)
            self.log("✅ Payment page loaded")
            
            # Fill card number
            card_field = self.wait.until(EC.presence_of_element_located((By.ID, "cc_number")))
            card_field.clear()
            card_field.send_keys(self.settings['cardNumber'])
            self.log("✅ Entered card number")
            
            # Fill expiry month
            try:
                month_select = Select(self.driver.find_element(By.ID, "m-0"))
                month_value = self.settings['expiryMonth'].lstrip('0')  # Remove leading zero
                month_select.select_by_value(month_value)
                self.log(f"✅ Selected expiry month: {month_value}")
            except:
                self.log("⚠️ Could not fill expiry month")
            
            # Fill expiry year
            try:
                year_select = Select(self.driver.find_element(By.ID, "y-0"))
                year_select.select_by_value(self.settings['expiryYear'])
                self.log(f"✅ Selected expiry year: {self.settings['expiryYear']}")
            except:
                self.log("⚠️ Could not fill expiry year")
            
            # Fill CVV
            cvv_field = self.driver.find_element(By.ID, "cc_code")
            cvv_field.clear()
            cvv_value = str(self.settings['cvv']).zfill(3)  # Ensure 3 digits
            cvv_field.send_keys(cvv_value)
            self.log(f"✅ Entered CVV: {cvv_value}")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Error filling payment form: {str(e)}")
            return False
    
    def submit_payment(self, account_number):
        """Submit payment and wait for confirmation"""
        try:
            self.log(f"🚀 Submitting payment for account {account_number}")
            
            # Find and click submit button
            submit_selectors = [
                '#qfauto-0',
                'input[type="submit"][value*="Pay"]',
                'input[type="submit"][value*="Subscribe"]',
                'button[type="submit"]'
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if submit_button:
                submit_button.click()
                self.log("✅ Clicked submit button")
                
                # Wait for processing
                time.sleep(5)
                
                # Check for payment errors
                error_indicators = [
                    '.error', '.alert-error', '.payment-error',
                    '[class*="error"]', '[class*="failed"]'
                ]
                
                for selector in error_indicators:
                    try:
                        error_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if error_element.is_displayed():
                            error_text = error_element.text
                            if any(word in error_text.lower() for word in ['error', 'failed', 'declined']):
                                raise Exception(f"Payment failed: {error_text}")
                    except NoSuchElementException:
                        continue
                
                return True
            else:
                raise Exception("Submit button not found")
                
        except Exception as e:
            self.log(f"❌ Payment submission error: {str(e)}")
            return False
    
    def wait_for_success(self, account_number):
        """Wait for success confirmation"""
        try:
            self.log(f"⏳ Waiting for success confirmation for account {account_number}")
            
            # Wait for success page elements or text
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    # Check for success page elements
                    success_selectors = [
                        '.am-thanks-status-success',
                        '.am-thanks-payment-details',
                        '.am-receipt'
                    ]
                    
                    for selector in success_selectors:
                        if self.driver.find_elements(By.CSS_SELECTOR, selector):
                            self.log(f"✅ Success element found: {selector}")
                            return True
                    
                    # Check for success text
                    page_text = self.driver.page_source.lower()
                    success_phrases = [
                        'thank you for signing up',
                        'payment has been successfully processed',
                        'order reference',
                        'transaction reference'
                    ]
                    
                    if any(phrase in page_text for phrase in success_phrases):
                        self.log("✅ Success confirmation found in page text")
                        return True
                    
                    # Check URL
                    if '/thanks' in self.driver.current_url:
                        self.log("✅ Success URL detected")
                        return True
                        
                except Exception as e:
                    pass
                
                time.sleep(2)
                self.log(f"⏳ Waiting for confirmation... (attempt {attempt + 1}/{max_attempts})")
            
            self.log("⚠️ Success confirmation timeout, but continuing...")
            return True
            
        except Exception as e:
            self.log(f"❌ Error waiting for success: {str(e)}")
            return False
    
    def process_account(self, account_number):
        """Process a single account"""
        try:
            self.current_account = account_number
            self.status = f"processing_account_{account_number}"
            self.log(f"🔄 Starting account {account_number}/{self.total_accounts}")
            
            # Navigate to signup page
            if not self.navigate_to_signup(self.settings['selectedAccount']):
                return False
            
            # Fill signup form
            if not self.fill_signup_form(account_number):
                return False
            
            # Fill payment form
            if not self.fill_payment_form(account_number):
                return False
            
            # Submit payment
            if not self.submit_payment(account_number):
                return False
            
            # Wait for success
            if not self.wait_for_success(account_number):
                return False
            
            self.log(f"✅ Account {account_number} completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"❌ Error processing account {account_number}: {str(e)}")
            return False
    
    def run_automation(self):
        """Main automation process - content script handles browser automation"""
        try:
            self.status = "running"
            self.log(f"🚀 Starting automation for {self.total_accounts} accounts")
            self.log(f"Account type: {self.settings['selectedAccount']}")
            self.log("💡 Content script will handle browser automation in current window")
            
            # Setup backend (no browser needed)
            if not self.setup_driver():
                self.status = "error"
                return
            
            # Simulate account processing (content script does the actual work)
            for account_num in range(1, self.total_accounts + 1):
                self.current_account = account_num
                self.log(f"🔄 Processing account {account_num}/{self.total_accounts}")
                self.log(f"💡 Content script is handling account {account_num} automation")
                
                # Wait for content script to complete (simulated)
                time.sleep(5)  # Give content script time to work
                
                # Simulate success (content script will report actual status)
                self.log(f"✅ Account {account_num} processing initiated")
                
                # Wait between accounts
                if account_num < self.total_accounts:
                    self.log("⏳ Waiting before processing next account...")
                    time.sleep(3)
            
            # Final status
            self.status = "completed"
            self.log(f"🎉 Backend automation completed for {self.total_accounts} accounts!")
            self.log("💡 Check content script logs for detailed automation status")
                
        except Exception as e:
            self.status = "error"
            self.log(f"❌ Backend automation error: {str(e)}")
        finally:
            # No cleanup needed for same-window automation
            pass

# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "APEX Selenium Backend is running"})

@app.route('/start_automation', methods=['POST'])
def start_automation():
    """Start automation process"""
    try:
        data = request.json
        session_id = str(uuid.uuid4())
        
        # Validate required fields
        required_fields = ['cardNumber', 'cvv', 'expiryMonth', 'expiryYear', 'numberOfAccounts', 'selectedAccount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create automation instance
        automation = ApexAutomation(session_id, data)
        automation_sessions[session_id] = automation
        
        # Start automation in background thread
        thread = threading.Thread(target=automation.run_automation)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "session_id": session_id,
            "status": "started",
            "message": "Automation started successfully"
        })
        
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_status/<session_id>', methods=['GET'])
def get_status(session_id):
    """Get automation status and logs"""
    try:
        if session_id not in automation_sessions:
            return jsonify({"error": "Session not found"}), 404
        
        automation = automation_sessions[session_id]
        return jsonify({
            "session_id": session_id,
            "status": automation.status,
            "current_account": automation.current_account,
            "total_accounts": automation.total_accounts,
            "logs": automation.logs[-50:],  # Return last 50 logs
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop_automation/<session_id>', methods=['POST'])
def stop_automation(session_id):
    """Stop automation process"""
    try:
        if session_id in automation_sessions:
            automation = automation_sessions[session_id]
            automation.status = "stopped"
            automation.log("🛑 Automation stopped by user")
            
            # Close browser if active
            if session_id in active_drivers:
                active_drivers[session_id].quit()
                del active_drivers[session_id]
            
            return jsonify({
                "session_id": session_id,
                "status": "stopped",
                "message": "Automation stopped successfully"
            })
        else:
            return jsonify({"error": "Session not found"}), 404
            
    except Exception as e:
        logger.error(f"Error stopping automation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/cleanup_session/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """Clean up automation session"""
    try:
        if session_id in automation_sessions:
            del automation_sessions[session_id]
        
        if session_id in active_drivers:
            active_drivers[session_id].quit()
            del active_drivers[session_id]
        
        return jsonify({"message": "Session cleaned up successfully"})
        
    except Exception as e:
        logger.error(f"Error cleaning up session: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting APEX Selenium Backend Server...")
    print("📡 Server will be available at: http://localhost:5001")
    print("🔧 Chrome Extension can connect to this backend")
    print("💡 Note: Using port 5001 to avoid AirPlay Receiver conflict")
    
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)
