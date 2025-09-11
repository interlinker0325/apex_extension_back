#!/usr/bin/env python3
"""
Setup script for APEX Selenium Backend
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing Python requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_chrome_driver():
    """Check if Chrome is installed"""
    print("🌐 Checking Chrome installation...")
    try:
        # Try to import selenium and webdriver_manager
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        
        # This will download ChromeDriver if needed
        ChromeDriverManager().install()
        print("✅ Chrome and ChromeDriver are ready!")
        return True
    except Exception as e:
        print(f"⚠️ Chrome setup issue: {e}")
        print("💡 Please make sure Google Chrome is installed")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up APEX Selenium Backend...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Check Chrome
    if not check_chrome_driver():
        print("⚠️ Chrome setup had issues, but continuing...")
    
    print("=" * 50)
    print("✅ Setup complete!")
    print("")
    print("🎯 Next steps:")
    print("1. Run: python app.py")
    print("2. Backend will start on http://localhost:5000")
    print("3. Use Chrome extension to start automation")
    print("")
    
    return True

if __name__ == "__main__":
    main()
