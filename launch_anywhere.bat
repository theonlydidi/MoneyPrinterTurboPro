@echo off
title MoneyPrinterTurboPro Launcher
color 0E

echo.
echo ========================================
echo    MoneyPrinterTurboPro Launcher
echo ========================================
echo.

:: Find the MoneyPrinterTurboPro directory
set "PROJECT_DIR="
for /d %%i in ("C:\Users\%USERNAME%\New folder\MoneyPrinterTurboPro*") do (
    if exist "%%i\webui\main.py" (
        set "PROJECT_DIR=%%i"
        goto :found
    )
)

:: Check current directory and parent directories
if exist "webui\main.py" (
    set "PROJECT_DIR=%CD%"
    goto :found
)

if exist "..\webui\main.py" (
    set "PROJECT_DIR=%CD%\.."
    goto :found
)

if exist "..\..\webui\main.py" (
    set "PROJECT_DIR=%CD%\..\.."
    goto :found
)

:: Check common locations
if exist "C:\MoneyPrinterTurboPro\webui\main.py" (
    set "PROJECT_DIR=C:\MoneyPrinterTurboPro"
    goto :found
)

if exist "C:\Users\%USERNAME%\Desktop\MoneyPrinterTurboPro\webui\main.py" (
    set "PROJECT_DIR=C:\Users\%USERNAME%\Desktop\MoneyPrinterTurboPro"
    goto :found
)

if exist "C:\Users\%USERNAME%\Documents\MoneyPrinterTurboPro\webui\main.py" (
    set "PROJECT_DIR=C:\Users\%USERNAME%\Documents\MoneyPrinterTurboPro"
    goto :found
)

echo ❌ ERROR: Could not find MoneyPrinterTurboPro directory
echo.
echo Please ensure the project is installed in one of these locations:
echo   - C:\Users\%USERNAME%\New folder\MoneyPrinterTurboPro
echo   - C:\MoneyPrinterTurboPro
echo   - C:\Users\%USERNAME%\Desktop\MoneyPrinterTurboPro
echo   - C:\Users\%USERNAME%\Documents\MoneyPrinterTurboPro
echo.
echo Or place this batch file in the MoneyPrinterTurboPro directory
echo.
pause
exit /b 1

:found
echo ✅ Found MoneyPrinterTurboPro at: %PROJECT_DIR%
echo.

:: Change to project directory
cd /d "%PROJECT_DIR%"

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
echo 📁 Project: %PROJECT_DIR%
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

:: Start Streamlit
cd webui
python -m streamlit run main.py --server.port %PORT% --server.headless false

echo.
echo 🛑 WebUI server stopped
pause
