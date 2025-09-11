#!/usr/bin/env python3
"""
Start APEX Selenium Backend with ngrok tunnel
"""

import subprocess
import time
import requests
import json
import sys
import os
from threading import Thread

def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ ngrok is not installed")
    print("📥 Download from: https://ngrok.com/download")
    print("💡 Or install via: brew install ngrok (macOS) or choco install ngrok (Windows)")
    return False

def start_ngrok_tunnel(port=5000):
    """Start ngrok tunnel"""
    print(f"🌐 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        ngrok_process = subprocess.Popen([
            'ngrok', 'http', str(port), '--log=stdout'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for ngrok to start
        time.sleep(3)
        
        # Get ngrok URL
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()['tunnels']
                for tunnel in tunnels:
                    if tunnel['proto'] == 'https':
                        ngrok_url = tunnel['public_url']
                        print(f"✅ ngrok tunnel started: {ngrok_url}")
                        return ngrok_url, ngrok_process
        except:
            pass
        
        print("⚠️ Could not get ngrok URL automatically")
        print("💡 Check ngrok dashboard at http://localhost:4040")
        return None, ngrok_process
        
    except Exception as e:
        print(f"❌ Failed to start ngrok: {e}")
        return None, None

def update_extension_config(ngrok_url):
    """Update Chrome extension config with ngrok URL"""
    config_path = '../APEX_frontend/config.js'
    
    try:
        # Read current config
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Update BACKEND_URL
        import re
        pattern = r"BACKEND_URL:\s*'[^']*'"
        replacement = f"BACKEND_URL: '{ngrok_url}'"
        updated_content = re.sub(pattern, replacement, content)
        
        # Write updated config
        with open(config_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated extension config: {ngrok_url}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update extension config: {e}")
        return False

def start_backend_server():
    """Start the Flask backend server"""
    print("🐍 Starting Python backend server...")
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def main():
    """Main function"""
    print("🚀 APEX Selenium Backend with ngrok")
    print("=" * 50)
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        return False
    
    # Start ngrok tunnel
    ngrok_url, ngrok_process = start_ngrok_tunnel()
    
    if not ngrok_url:
        print("❌ Failed to get ngrok URL")
        return False
    
    # Update extension config
    if not update_extension_config(ngrok_url):
        print("⚠️ Could not update extension config automatically")
        print(f"💡 Manually update BACKEND_URL in config.js to: {ngrok_url}")
    
    print("=" * 50)
    print("🎯 Setup Complete!")
    print(f"🌐 Backend URL: {ngrok_url}")
    print("📱 Chrome extension will connect to this URL")
    print("")
    print("🔄 Starting backend server...")
    print("💡 Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Start backend server
        start_backend_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        if ngrok_process:
            ngrok_process.terminate()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
