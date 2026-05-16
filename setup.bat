@echo off
REM ============================================
REM BMW GraphRAG Project - Windows Setup Script
REM ============================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  🚗 Bayerische Motoren Werke - GraphRAG Project              ║
echo ║     Windows Setup Script                                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo    Please install Python from https://www.python.org
    echo    Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment
if not exist "venv" (
    echo.
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo    Try running: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Dependencies installed

REM Check if .env exists
echo.
if not exist ".env" (
    echo ⚠️  .env file not found!
    echo.
    echo Please follow these steps:
    echo 1. Open .env.example and copy it to .env
    echo 2. Add your GROQ API key to .env file
    echo    Get free key: https://console.groq.com
    echo 3. Save .env file
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
) else (
    echo ✅ .env file found
)

REM Ready to launch
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║  ✅ Setup Complete! Launching Streamlit Dashboard...         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Launch Streamlit
streamlit run app.py

REM If streamlit fails
if errorlevel 1 (
    echo.
    echo ❌ Failed to launch Streamlit
    echo.
    echo Try running manually:
    echo   streamlit run app.py
    echo.
    pause
    exit /b 1
)
