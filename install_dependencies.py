#!/usr/bin/env python3
"""
Install Required Dependencies for AI Notebook System
This script installs all necessary Python packages for data analysis.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required dependencies"""
    print("🚀 Installing Required Dependencies for AI Notebook System")
    print("=" * 60)
    
    # Core data science packages
    packages = [
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "scikit-learn>=1.3.0",
        "jupyter>=1.0.0",
        "ipykernel>=6.0.0"
    ]
    
    print("📋 Required packages:")
    for package in packages:
        print(f"  • {package}")
    
    print("\n🔧 Installing packages...")
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Installation Summary:")
    print(f"  ✅ Successfully installed: {success_count}")
    print(f"  ❌ Failed to install: {total_count - success_count}")
    print(f"  📦 Total packages: {total_count}")
    
    if success_count == total_count:
        print("\n🎉 All dependencies installed successfully!")
        print("🚀 The AI Notebook System is ready to execute data analysis!")
    else:
        print(f"\n⚠️  {total_count - success_count} packages failed to install.")
        print("Please check the error messages above and try installing them manually.")
    
    print("\n💡 Next steps:")
    print("1. Restart the backend server")
    print("2. Run the complete AI journey demo")
    print("3. Execute notebook cells to see outputs")

if __name__ == "__main__":
    main() 