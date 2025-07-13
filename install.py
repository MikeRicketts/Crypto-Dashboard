"""
Installation Script for Crypto/Stock Price Tracker
Sets up the environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\nCreating directories...")
    
    directories = [
        "database",
        "logs",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("✗ pip not found. Please install pip first.")
        return False
    
    # Install dependencies
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies from requirements.txt"
    )
    
    return success

def check_python_version():
    """Check if Python version is compatible"""
    print("\nChecking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\nTesting imports...")
    
    required_modules = [
        "requests",
        "pandas", 
        "flask",
        "yfinance",
        "plotly",
        "apscheduler"
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError:
            print(f"✗ {module} - not found")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nMissing modules: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main installation process"""
    print("Crypto/Stock Price Tracker - Installation")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        sys.exit(1)
    
    # Test imports
    if not test_imports():
        print("\n❌ Some modules are missing. Please install them manually.")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("🎉 Installation completed successfully!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Test the application: python test_app.py")
    print("2. Start the application: python main.py")
    print("3. Open your browser to: http://localhost:5000")
    
    print("\nConfiguration:")
    print("- Edit config.py to customize settings")
    print("- Add your email/webhook settings for alerts")
    print("- Modify asset lists as needed")

if __name__ == "__main__":
    main() 