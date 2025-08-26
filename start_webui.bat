@echo off
title MoneyPrinterTurboPro WebUI Launcher
color 0A

echo.
echo ========================================
echo    MoneyPrinterTurboPro WebUI Launcher
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to your system PATH
    echo.
    pause
    exit /b 1
)

:: Check if we're in the right directory
if not exist "webui\main.py" (
    echo ❌ ERROR: Please run this batch file from the MoneyPrinterTurboPro directory
    echo.
    echo Current directory: %CD%
    echo Expected location: MoneyPrinterTurboPro\
    echo.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo 🔧 Setting up virtual environment...
    echo.
    python -m venv venv
    if errorlevel 1 (
        echo ❌ ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo 🚀 Activating virtual environment...
call venv\Scripts\activate.bat

:: Install/upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

:: Install requirements
echo 📦 Installing dependencies...
pip install -r requirements-webui.txt

:: Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Failed to install Streamlit
    pause
    exit /b 1
)

:: Check if openpyxl is installed
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Failed to install openpyxl
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully!
echo.

:: Check if port 8501 is already in use
netstat -an | findstr ":8501" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  WARNING: Port 8501 is already in use
    echo This might mean the WebUI is already running
    echo.
    choice /C YN /M "Do you want to continue anyway"
    if errorlevel 2 (
        echo.
        echo Launching WebUI on port 8502 instead...
        set PORT=8502
    ) else (
        set PORT=8501
    )
) else (
    set PORT=8501
)

echo.
echo 🌐 Starting MoneyPrinterTurboPro WebUI...
echo 📍 URL: http://localhost:%PORT%
echo.
echo 💡 Tips:
echo    - Press Ctrl+C to stop the server
echo    - Keep this window open while using the WebUI
echo    - The WebUI will automatically open in your browser
echo.

:: Start Streamlit
cd webui
python -m streamlit run main.py --server.port %PORT% --server.headless false

:: If we get here, the server was stopped
echo.
echo 🛑 WebUI server stopped
echo.
pause
