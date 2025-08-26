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

:: Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo 🚀 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found
    echo Using system Python...
)

:: Check if Streamlit is available
echo 📦 Checking Streamlit installation...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo ❌ Streamlit not found. Installing...
    pip install streamlit
)

:: Check if openpyxl is available
echo 📦 Checking openpyxl installation...
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo ❌ openpyxl not found. Installing...
    pip install openpyxl
)

:: Find available port
set PORT=8501
netstat -an | findstr ":%PORT%" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port %PORT% is already in use, trying port 8502...
    set PORT=8502
    netstat -an | findstr ":%PORT%" >nul 2>&1
    if not errorlevel 1 (
        echo ⚠️  Port 8502 is also in use, trying port 8503...
        set PORT=8503
    )
)

echo.
echo ✅ All dependencies verified!
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
echo 🚀 Launching Streamlit on port %PORT%...
python -m streamlit run main.py --server.port %PORT% --server.headless false

:: If we get here, the server was stopped
echo.
echo 🛑 WebUI server stopped
echo.
pause
