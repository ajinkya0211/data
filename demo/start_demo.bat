@echo off
echo 🚀 Starting AI Notebook Demo...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Start backend
echo 🐍 Starting backend server...
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 📦 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
pip install -r requirements.txt

echo 🚀 Starting backend on http://localhost:8000
start "Backend Server" python main.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo ⚛️  Starting frontend...
cd ..\frontend

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    npm install
)

echo 🚀 Starting frontend on http://localhost:3000
start "Frontend Server" npm run dev

echo.
echo 🎉 Demo is starting up!
echo 📊 Backend: http://localhost:8000
echo 🎨 Frontend: http://localhost:3000
echo.
echo Press any key to stop the demo...
pause >nul

echo 🛑 Stopping demo...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ Demo stopped
pause
