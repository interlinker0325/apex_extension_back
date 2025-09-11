# APEX Selenium Backend

Chrome Extension + Python Selenium Hybrid Architecture for APEX Trader Funding automation.

## 🏗️ Architecture

```
Chrome Extension (Frontend)    ←→    Python Selenium Server (Backend)
├── popup.html/js                   ├── Flask API server
├── options.html/js                 ├── Selenium WebDriver
├── User settings storage           ├── Multi-account processing
└── Real-time status updates        └── Robust error handling
```

## 🚀 Features

- **Reliable Automation**: Python Selenium for robust browser automation
- **User-Friendly Interface**: Chrome extension popup for easy control
- **Multi-Account Processing**: Sequential account creation with error handling
- **Real-Time Updates**: Live status and logs in extension popup
- **Privacy-First**: No credential sharing - works with existing login session
- **Error Recovery**: Continues with next account if one fails

## 📋 Prerequisites

- **Python 3.7+**
- **Google Chrome** browser
- **Chrome Extension** loaded in browser

## 🛠️ Setup

### 1. Install Python Dependencies

```bash
cd APEX_selenium_backend
python setup.py
```

Or manually:
```bash
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
python app.py
```

Server will start on: `http://localhost:5000`

### 3. Load Chrome Extension

1. Open Chrome → Extensions → Developer mode
2. Load unpacked → Select `APEX_frontend` folder
3. Configure payment settings in extension options

## 🎯 Usage

1. **Start Backend**: Run `python app.py`
2. **Login to APEX**: Go to https://dashboard.apextraderfunding.com and login
3. **Open Extension**: Click extension icon in Chrome
4. **Configure Settings**: Set payment details and number of accounts
5. **Start Automation**: Click "START SCRAPING"
6. **Monitor Progress**: Watch real-time logs and status

## 📡 API Endpoints

### `POST /start_automation`
Start automation process
```json
{
  "cardNumber": "1234 5678 9012 3456",
  "cvv": "123",
  "expiryMonth": "03", 
  "expiryYear": "2030",
  "numberOfAccounts": 2,
  "selectedAccount": "25k-Tradovate"
}
```

### `GET /get_status/{session_id}`
Get automation status and logs
```json
{
  "status": "processing",
  "current_account": 1,
  "total_accounts": 2,
  "logs": ["[12:34:56] Starting automation..."]
}
```

### `POST /stop_automation/{session_id}`
Stop running automation

### `DELETE /cleanup_session/{session_id}`
Clean up automation session

## 🔧 Configuration

### Coupon Code
Mandatory coupon code is configured in `app.py`:
```python
self.coupon_code = "JAYPELLE"  # Mandatory coupon code
```

### Backend URL
Chrome extension connects to backend via:
```javascript
const BACKEND_URL = 'http://localhost:5000';
```

## 🐛 Troubleshooting

### Backend Connection Failed
- Make sure Python backend is running: `python app.py`
- Check if port 5000 is available
- Verify Chrome extension has localhost permissions

### Chrome Driver Issues
- Ensure Google Chrome is installed
- Run `python setup.py` to install ChromeDriver
- Check Chrome version compatibility

### Automation Stuck
- Check backend logs for detailed error messages
- Verify APEX website structure hasn't changed
- Ensure payment details are valid format

## 📊 Status Codes

- `initializing`: Setting up Chrome driver
- `running`: Automation in progress
- `processing_account_N`: Currently processing account N
- `completed`: All accounts processed successfully
- `completed_with_errors`: Some accounts failed
- `error`: Automation failed
- `stopped`: Manually stopped

## 🔒 Security

- No credential storage in backend
- Uses existing browser login session
- Local communication only (localhost:5000)
- Session-based automation tracking

## 🚀 Advantages Over Pure Extension

1. **More Reliable**: Selenium WebDriver vs DOM manipulation
2. **Better Error Handling**: Python exception handling
3. **Easier Debugging**: Standard Python debugging tools
4. **Robust Multi-Account**: No page context loss issues
5. **Maintainable**: Single Python file vs multiple extension scripts

## 📝 Logs

Backend logs include:
- Account processing progress
- Form filling status
- Payment submission results
- Error messages and recovery attempts
- Success confirmations

Example log output:
```
[12:34:56] ✅ Chrome driver initialized successfully
[12:34:57] 🔄 Processing account 1/2
[12:34:58] 📝 Filling signup form for account 1
[12:35:01] ✅ Entered coupon code: JAYPELLE
[12:35:02] ✅ Agreed to terms and conditions
[12:35:05] 💳 Filling payment details for account 1
[12:35:08] ✅ Payment submitted successfully
[12:35:12] ✅ Success confirmation found
[12:35:13] ✅ Account 1 completed successfully!
```
