#!/bin/bash

# Enhanced AI Notebook System Startup Script
# This script starts the enhanced backend with MCP integration

echo "🚀 Starting Enhanced AI Notebook System with MCP Integration..."
echo "================================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed. The system will work with limited AI capabilities."
    echo "   To install Ollama: https://ollama.ai/"
    echo "   After installation, run: ollama pull qwen2.5:3b"
    echo ""
else
    echo "✅ Ollama found. Checking for Qwen2.5:3b model..."
    
    # Check if the model is available
    if ollama list | grep -q "qwen2.5:3b"; then
        echo "✅ Qwen2.5:3b model found."
    else
        echo "⚠️  Qwen2.5:3b model not found. Pulling now..."
        ollama pull qwen2.5:3b
        if [ $? -eq 0 ]; then
            echo "✅ Qwen2.5:3b model downloaded successfully."
        else
            echo "❌ Failed to download Qwen2.5:3b model."
        fi
    fi
fi

# Navigate to backend directory
cd "$(dirname "$0")/backend" || {
    echo "❌ Failed to navigate to backend directory."
    exit 1
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "🔧 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    echo "   You may need to install system dependencies first:"
    echo "   - On Ubuntu/Debian: sudo apt-get install python3-dev build-essential"
    echo "   - On macOS: xcode-select --install"
    echo "   - On Windows: Install Visual Studio Build Tools"
    exit 1
fi

# Check if all required packages are installed
echo "🔧 Verifying installation..."
python3 -c "
import sys
required_packages = ['fastapi', 'uvicorn', 'pandas', 'numpy', 'networkx']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print(f'❌ Missing packages: {missing_packages}')
    sys.exit(1)
else:
    print('✅ All required packages are installed.')
"

if [ $? -ne 0 ]; then
    echo "❌ Package verification failed."
    exit 1
fi

# Start the enhanced backend
echo ""
echo "🚀 Starting Enhanced AI Notebook Backend..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   System Status: http://localhost:8000/system/status"
echo ""
echo "   Press Ctrl+C to stop the server"
echo "================================================================"

# Start the server
python3 main_enhanced.py

echo ""
echo "🛑 Enhanced AI Notebook Backend stopped."
echo "================================================================"
