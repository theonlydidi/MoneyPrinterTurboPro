# MoneyPrinterTurboPro WebUI Launcher (PowerShell)
# This script provides a more reliable alternative to batch files

Write-Host "========================================" -ForegroundColor Green
Write-Host "   MoneyPrinterTurboPro WebUI Launcher" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to your system PATH" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "webui\main.py")) {
    Write-Host "❌ ERROR: Please run this script from the MoneyPrinterTurboPro directory" -ForegroundColor Red
    Write-Host ""
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Write-Host "Expected location: MoneyPrinterTurboPro\" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "🚀 Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  No virtual environment found" -ForegroundColor Yellow
    Write-Host "Using system Python..." -ForegroundColor Yellow
}

# Check if required packages are installed
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan
try {
    python -c "import streamlit" 2>$null
    Write-Host "✅ Streamlit found" -ForegroundColor Green
} catch {
    Write-Host "❌ Streamlit not found. Installing..." -ForegroundColor Yellow
    pip install -r requirements-webui.txt
}

try {
    python -c "import openpyxl" 2>$null
    Write-Host "✅ openpyxl found" -ForegroundColor Green
} catch {
    Write-Host "❌ openpyxl not found. Installing..." -ForegroundColor Yellow
    pip install openpyxl
}

# Check if port 8501 is already in use
$port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
if ($port8501) {
    Write-Host "⚠️  Port 8501 is already in use, using port 8502" -ForegroundColor Yellow
    $port = 8502
} else {
    $port = 8501
}

Write-Host ""
Write-Host "🌐 Starting MoneyPrinterTurboPro WebUI..." -ForegroundColor Green
Write-Host "📍 URL: http://localhost:$port" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
Set-Location "webui"
try {
    python -m streamlit run main.py --server.port $port --server.headless false
} catch {
    Write-Host "❌ Error starting Streamlit: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "🛑 WebUI server stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
