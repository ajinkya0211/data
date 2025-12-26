@echo off
REM Enhanced AI Notebook System Startup Script for Windows
REM This script starts the enhanced backend with MCP integration

echo 🚀 Starting Enhanced AI Notebook System with MCP Integration...
echo ================================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Check if Ollama is available
ollama --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Ollama is not installed. The system will work with limited AI capabilities.
    echo    To install Ollama: https://ollama.ai/
    echo    After installation, run: ollama pull qwen2.5:3b
    echo.
) else (
    echo ✅ Ollama found. Checking for Qwen2.5:3b model...
    
    REM Check if the model is available
    ollama list | findstr "qwen2.5:3b" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Qwen2.5:3b model not found. Pulling now...
        ollama pull qwen2.5:3b
        if errorlevel 1 (
            echo ❌ Failed to download Qwen2.5:3b model.
        ) else (
            echo ✅ Qwen2.5:3b model downloaded successfully.
        )
    ) else (
        echo ✅ Qwen2.5:3b model found.
    )
)

REM Navigate to backend directory
cd /d "%~dp0backend" || (
    echo ❌ Failed to navigate to backend directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade pip
echo 🔧 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 🔧 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies.
    echo    You may need to install system dependencies first:
    echo    - Install Visual Studio Build Tools
    echo    - Install Windows SDK
    pause
    exit /b 1
)

REM Check if all required packages are installed
echo 🔧 Verifying installation...
python -c "import fastapi, uvicorn, pandas, numpy, networkx; print('✅ All required packages are installed.')"

if errorlevel 1 (
    echo ❌ Package verification failed.
    pause
    exit /b 1
)

REM Start the enhanced backend
echo.
echo 🚀 Starting Enhanced AI Notebook Backend...
echo    Backend will be available at: http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo    System Status: http://localhost:8000/system/status
echo.
echo    Press Ctrl+C to stop the server
echo ================================================================

REM Start the server
python main_enhanced.py

echo.
echo 🛑 Enhanced AI Notebook Backend stopped.
echo ================================================================
pause
