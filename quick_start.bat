@echo off
title MoneyPrinterTurboPro Quick Start
color 0B

echo.
echo ========================================
echo    MoneyPrinterTurboPro Quick Start
echo ========================================
echo.

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
if exist "venv\Scripts\activate.bat" (
    echo 🚀 Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found
    echo Using system Python...
)

:: Check if port 8501 is already in use
netstat -an | findstr ":8501" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️  Port 8501 is already in use, using port 8502
    set PORT=8502
) else (
    set PORT=8501
)

echo.
echo 🌐 Starting MoneyPrinterTurboPro WebUI...
echo 📍 URL: http://localhost:%PORT%
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

:: Start Streamlit
cd webui
python -m streamlit run main.py --server.port %PORT% --server.headless false

echo.
echo 🛑 WebUI server stopped
pause
